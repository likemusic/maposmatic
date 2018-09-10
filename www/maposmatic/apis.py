# coding: utf-8

# maposmatic, the web front-end of the MapOSMatic city map generation system
# Copyright (C) 2009  David Decotigny
# Copyright (C) 2009  Frédéric Lehobey
# Copyright (C) 2009  Pierre Mauduit
# Copyright (C) 2009  David Mentré
# Copyright (C) 2009  Maxime Petazzoni
# Copyright (C) 2009  Thomas Petazzoni
# Copyright (C) 2009  Gaël Utard

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# API calls for MapOSMatic

import json

from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse, HttpResponseNotAllowed, Http404
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

import ocitysmap
from www.maposmatic import helpers, forms, nominatim, models
import www.settings

import logging
LOG = logging.getLogger('maposmatic')


def styles(request):
    result = {}
    for style in ocitysmap.OCitySMap().get_all_style_configurations():
        result[style.name] = { "description": style.description, 
                               "annotation": style.annotation,
                               "preview_url": request.build_absolute_uri('/media/img/style/'+style.name+'.png')
                             }

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')



def overlays(request):
    result = {}
    for overlay in ocitysmap.OCitySMap().get_all_overlay_configurations():
        result[overlay.name] = { "description": overlay.description, 
                                 "annotation": overlay.annotation,
                                 "preview_url": request.build_absolute_uri('/media/img/overlay/'+overlay.name+'.png')
                               }

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')



def paper_formats(request):
    result = {}
    for p in ocitysmap.OCitySMap.get_all_paper_sizes():
        result[p[0]] = {'width': p[1], 'height': p[2]}

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')



def layouts(request):
    result = {}
    for renderer in ocitysmap.OCitySMap().get_all_renderers():
        result[renderer.name] = { "description": renderer.description,
                                  "preview_url": request.build_absolute_uri('/media/img/layout/'+renderer.name+'.png')
                         }

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')



def job_stati(request):
    # TODO do not hard-code these, get them from OCitysMap cleanly
    result = {
        "0": "Submitted",
        "1": "In progress",
        "2": "Done",
        "3": "Done w/o files",
        "4": "Cancelled"
    }

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')



def jobs(request, job_id):
    """API handler for external rendering requests"""

    if request.method == 'GET':
        return _jobs_get(request, job_id)
    elif request.method == 'POST':
        return _jobs_post(request)
    else:
        return HttpResponseNotAllowed(['GET','POST'])

def _jobs_get(request, job_id):
    if not job_id:
        return HttpResponseNotFound('not found')

    job = get_object_or_404(models.MapRenderingJob, id=job_id)

    reply = model_to_dict(job)

    result = {}
    result['id']              = job_id
    result['status']          = reply['status']

    if reply['administrative_osmid']:
        result['osm_id']      = reply['administrative_osmid']
    else:
        result['bbox_top']    = reply['lat_upper_left']
        result['bbox_bottom'] = reply['lat_bottom_right']
        result['bbox_left']   = reply['lon_upper_left']
        result['bbox_right']  = reply['lon_bottom_right']

    result['title']           = reply['maptitle']
    result['layout']          = reply['layout']
    result['style']           = reply['stylesheet']

    if reply['overlay']:
        result['overlays']    = reply['overlay'].split(',')

    result['language']        = reply['map_language']
    result['paper_height_mm'] = reply['paper_height_mm']
    result['paper_width_mm']  = reply['paper_width_mm']

    if job.status == 0:
        result['queue_size'] = models.MapRenderingJob.objects.queue_size()
    else:
        result['queue_size'] = 0

    result['files'] = {}
    if job.status == 2:
        files = job.output_files()
        for key, val in files['maps'].items():
            result['files'][key] = request.build_absolute_uri(val[0])

    if job.status <= 1:
        status = 202
    else:
        status = 200

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str)
                       , content_type='text/json', status=status)



def _jobs_post(request):
    result = { "error": {} }

    job = models.MapRenderingJob()

    if request.content_type == 'application/json':
        input = json.loads(request.body.decode('utf-8'))
    else:
        input = json.loads(request.POST['job'])

    valid_keys = ['osmid', 'bbox_top', 'bbox_bottom', 'bbox_left', 'bbox_right',
                  'title', 'language', 'layout', 'style', 'overlays',
                  'paper_size', 'orientation']

    for key in input:
        if key not in valid_keys:
            result['error'][key] = "Unknown parameter '%s'" % key

    if 'osmid' in input:
        job.administrative_osmid= input['osmid']
    elif 'bbox_top' in input:
        job.lat_upper_left   = input['bbox_top']
        job.lon_upper_left   = input['bbox_left']
        job.lat_bottom_right = input['bbox_bottom']
        job.lon_bottom_right = input['bbox_right']
    else:
        result['error']['geometry'] = 'No bounding box or OsmID given'

    if 'title' in input:
        job.maptitle = input['title']

    if 'language' in input:
        job.map_language = input['language']
    else:
        job.map_language = 'en_US.UTF-8'

    if 'layout' in input:
        job.layout = input['layout']
    else:
        job.layout = 'plain'

    if 'style' in input:
        job.stylesheet = input['style']
    else:
        job.stylesheet = 'CartoOSM'

    if 'overlays' in input:
        if isinstance(input['overlays'], str):
            job.overlay = input['overlays']
        else:
            job.overlay = ",".join(input['overlays'])

    job.paper_width_mm  = 210
    job.paper_height_mm = 297

    if 'paper_size' in input:
        try:
            p = ocitysmap.OCitySMap.get_paper_size_by_name(input['paper_size'])
            if 'orientation' in input:
                if input['orientation'] == 'landscape':
                    p[1], p[0] = p[0], p[1]
            job.paper_width_mm  = p[0]
            job.paper_height_mm = p[1]
        except LookupError as e:
            result['error']['paper_size']  = str(e)

    if not result['error']:
        job.status = 0
        job.submitterip = request.META['REMOTE_ADDR']
        job.index_queue_at_submission = (models.MapRenderingJob.objects.queue_size())
        job.nonce = helpers.generate_nonce(models.MapRenderingJob.NONCE_SIZE)
        try:
            job.full_clean()
            job.save()

            if 'umap' in request.FILES:
                job.umap.save('umap', request.FILES['umap'])

            if 'track' in request.FILES:
                job.track.save('track', request.FILES['track'])

            if 'poi_file' in request.FILES:
                job.poi_file.save('poi_file', request.FILES['poi_file'])

            reply = model_to_dict(job)

            result['id']              = reply['id']
            result['status']          = reply['status']

            result['interactive']     = request.build_absolute_uri('../../maps/%d' % reply['id'])

            if reply['administrative_osmid']:
                result['osm_id']      = reply['administrative_osmid']
            else:
                result['bbox_top']    = reply['lat_upper_left']
                result['bbox_bottom'] = reply['lat_bottom_right']
                result['bbox_left']   = reply['lon_upper_left']
                result['bbox_right']  = reply['lon_bottom_right']

            result['title']           = reply['maptitle']
            result['layout']          = reply['layout']
            result['style']           = reply['stylesheet']
            if reply['overlay']:
                result['overlays']    = reply['overlay'].split(',')
            result['language']        = reply['map_language']
            result['paper_height_mm'] = reply['paper_height_mm']
            result['paper_width_mm']  = reply['paper_width_mm']
        except ValidationError as e:
            result['error'] = e.message_dict
        except Exception as e:
            result['error']['reason'] = str(e)

    if result['error']:
        status = 400
    else:
        del result['error']
        status = 202

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str)
                         , content_type='text/json', status=status)


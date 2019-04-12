# coding: utf-8

# maposmatic, the web front-end of the MapOSMatic city map generation system
# Copyright (C) 2018  Hartmut Holzgraefe

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

from os import path

import json

from django.core.exceptions import ValidationError
from django.core.files import File
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse, HttpResponseNotAllowed, Http404
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

import ocitysmap
from www.maposmatic import helpers, forms, nominatim, models
import www.settings

import gpxpy
import gpxpy.gpx

import requests
from tempfile import NamedTemporaryFile

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
        if p[1] and p[2]:
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



def jobs(request, job_id=False):
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
        input = json.loads(request.body.decode('utf-8-sig'))
    else:
        input = json.loads(request.POST['job'])

    valid_keys = ['osmid', 'bbox_top', 'bbox_bottom', 'bbox_left', 'bbox_right',
                  'title', 'language', 'layout', 'style', 'overlays',
                  'paper_size', 'orientation', 'track_url']

    for key in input:
        if key not in valid_keys:
            result['error'][key] = "Unknown parameter '%s'" % key

    if 'osmid' in input:
        job.administrative_osmid= input['osmid']
    elif 'bbox_top' in input and 'bbox_bottom' in input and 'bbox_left' in input and 'bbox_right' in input:
        job.lat_upper_left   = input['bbox_top']
        job.lon_upper_left   = input['bbox_left']
        job.lat_bottom_right = input['bbox_bottom']
        job.lon_bottom_right = input['bbox_right']

    if 'title' in input:
        job.maptitle = input['title']

    if 'language' in input:
        job.map_language = input['language']
    else:
        job.map_language = 'en_US.UTF-8'

    if 'layout' in input:
        job.layout = input['layout']

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

    if 'track_url' in input:
        try:
            request.FILES['track'] = _get_remote_file(input['track_url'])
        except Exception as e:
            result['error']['track_url'] = "Can't fetch track_url: %s" % e

    if 'track' in request.FILES:
        try:
            gpxxml = request.FILES['track'].read().decode('utf-8-sig')
            LOG.warning(gpxxml)
            gpx = gpxpy.parse(gpxxml)

            if _no_geometry(job):
                (min_lat, max_lat, min_lon, max_lon) = gpx.get_bounds()
                d_lat = (max_lat - min_lat) * 0.05
                d_lon = (max_lon - min_lon) * 0.05
                job.lat_bottom_right = min_lat - d_lat
                job.lat_upper_left   = max_lat + d_lat
                job.lon_bottom_right = min_lon - d_lon
                job.lon_upper_left   = max_lon + d_lon

            if not job.maptitle and gpx.name:
                job.maptitle = gpx.name

            if 'track' in request.FILES:
                job.track.save(request.FILES['track'].name, request.FILES['track'], save=False)

        except Exception as e:
            result['error']['track'] = 'Cannot parse GPX track: %s' % e

    if 'umap_url' in input:
        try:
            request.FILES['umap'] = _get_remote_file(input['umap_url'])
        except Exception as e:
            result['error']['umap_url'] = "Can't fetch umap_url: %s" % e

    if 'umap' in request.FILES:
        try:
            umapjson = request.FILES['umap'].read().decode('utf-8-sig')

            umap = json.loads(umapjson)

            if not job.maptitle and umap['properties']['name']:
                job.maptitle = umap['properties']['name']

            bounds = [180, -180, 90, -90]
            for layer in umap['layers']:
                for feature in layer['features']:
                    bounds = _geojson_get_bounds(feature['geometry']['coordinates'], bounds)

            if _no_geometry(job):
                d_lon = (bounds[1] - bounds[0]) * 0.05
                d_lat = (bounds[3] - bounds[2]) * 0.05
                job.lat_bottom_right = bounds[2] - d_lat
                job.lat_upper_left   = bounds[3] + d_lat
                job.lon_bottom_right = bounds[0] - d_lon
                job.lon_upper_left   = bounds[1] + d_lon

            if 'umap' in request.FILES:
                job.umap.save(request.FILES['umap'].name, request.FILES['umap'], save=False)

        except Exception as e:
            result['error']['track'] = 'Cannot parse Umap file: %s' % e

    if 'poi_file' in request.FILES:
        try:
            poijson = request.FILES['poi_file'].read().decode('utf-8-sig')

            poi = json.loads(poijson)

            if not job.maptitle and poi['title']:
                job.maptitle = poi['title']

            bounds = [180, -180, 90, -90]
            for cat in poi['nodes']:
                for node in cat['nodes']:
                    bounds[0] = min(float(node['lon']), bounds[0])
                    bounds[1] = max(float(node['lon']), bounds[1])
                    bounds[2] = min(float(node['lat']), bounds[2])
                    bounds[3] = max(float(node['lat']), bounds[3])

            if _no_geometry(job):
                d_lon = (bounds[1] - bounds[0]) * 0.05
                d_lat = (bounds[3] - bounds[2]) * 0.05
                job.lat_bottom_right = bounds[2] - d_lat
                job.lat_upper_left   = bounds[3] + d_lat
                job.lon_bottom_right = bounds[0] - d_lon
                job.lon_upper_left   = bounds[1] + d_lon

            if not job.layout:
                job.layout = 'single_page_index_side'

            if 'poi_file' in request.FILES:
                job.poi_file.save('poi_file', request.FILES['poi_file'], save=False)

        except Exception as e:
            result['error']['track'] = 'Cannot parse POI file: %s' % e

    if _no_geometry(job):
        result['error']['geometry'] = 'No bounding box or OSM id given'

    if not job.layout:
        job.layout = 'plain'

    if not result['error']:
        job.status = 0
        job.submitterip = request.META['REMOTE_ADDR']
        job.index_queue_at_submission = (models.MapRenderingJob.objects.queue_size())
        job.nonce = helpers.generate_nonce(models.MapRenderingJob.NONCE_SIZE)
        try:
            job.full_clean()
            job.save()

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



def _no_geometry(job):
    return not job.administrative_osmid and not job.lat_upper_left

def _geojson_get_bounds(coords, bounds = [180, -180, 90, -90]):
    if isinstance(coords[0], list):
        for coord in coords:
            bounds = _get_bounds(coord, bounds)
    else:
        bounds[0] = min(coords[0], bounds[0])
        bounds[1] = max(coords[0], bounds[1])
        bounds[2] = min(coords[1], bounds[2])
        bounds[3] = max(coords[1], bounds[3])

    return bounds

def _get_remote_file(url):
    r = requests.get(url)
    with NamedTemporaryFile(delete=False) as f:
        tmpname = f.name
        f.write(r.content)
    return File(open(f.name, "rb"), path.basename(url))

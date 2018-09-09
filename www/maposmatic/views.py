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

# Views for MapOSMatic

import datetime
import logging
import json

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.urls import get_script_prefix

import ocitysmap
from www.maposmatic import helpers, forms, nominatim, models
import www.settings

from www.maposmatic import gisdb
import psycopg2

LOG = logging.getLogger('maposmatic')

def index(request):
    """The main page."""
    form = forms.MapSearchForm(request.GET)

    job_list = (models.MapRenderingJob.objects.all()
                .order_by('-submission_time'))
    job_list = (job_list.filter(status=0) |
                job_list.filter(status=1))

    return render(request,
                  'maposmatic/index.html',
                  { 'form': form,
                    'queued': job_list.count()
                  }
                 )

def about(request):
    """The about page."""
    form = forms.MapSearchForm(request.GET)

    job_list = (models.MapRenderingJob.objects.all()
                .order_by('-submission_time'))
    job_list = (job_list.filter(status=0) |
                job_list.filter(status=1))

    return render(request,
                  'maposmatic/about.html',
                  { 'form': form,
                    'queued': job_list.count()
                  }
                 )


def donate(request):
    """The donate page."""
    form = forms.MapSearchForm(request.GET)

    job_list = (models.MapRenderingJob.objects.all()
                .order_by('-submission_time'))
    job_list = (job_list.filter(status=0) |
                job_list.filter(status=1))

    return render(request,
                  'maposmatic/donate.html',
                  { 'form': form,
                    'queued': job_list.count()
                  }
                 )

def donate_thanks(request):
    """The thanks for donation page."""
    return render_to_response('maposmatic/donate-thanks.html')

def new(request):
    """The map creation page and form."""

    if request.method == 'POST':
        form = forms.MapRenderingJobForm(request.POST, request.FILES)
        if form.is_valid():
            request.session['new_layout'] = form.cleaned_data.get('layout')
            request.session['new_stylesheet'] = form.cleaned_data.get('stylesheet')
            request.session['new_overlay'] = form.cleaned_data.get('overlay')

            job = form.save(commit=False)
            job.administrative_osmid = form.cleaned_data.get('administrative_osmid')
            job.stylesheet = form.cleaned_data.get('stylesheet')
            job.overlay = ",".join(form.cleaned_data.get('overlay'))
            job.layout = form.cleaned_data.get('layout')
            job.paper_width_mm = form.cleaned_data.get('paper_width_mm')
            job.paper_height_mm = form.cleaned_data.get('paper_height_mm')
            job.status = 0 # Submitted
            job.submitterip = request.META['REMOTE_ADDR']
            job.submitteremail = form.cleaned_data.get('submitteremail')
            job.map_language = form.cleaned_data.get('map_language')
            job.index_queue_at_submission = (models.MapRenderingJob.objects
                                             .queue_size())
            job.nonce = helpers.generate_nonce(models.MapRenderingJob.NONCE_SIZE)
            job.save()

            return HttpResponseRedirect(reverse('map-by-id-and-nonce',
                                                args=[job.id, job.nonce]))
        else:
            LOG.debug("FORM NOT VALID")
    else:
        init_vals = request.GET.dict()
        oc = ocitysmap.OCitySMap(www.settings.OCITYSMAP_CFG_PATH)

        if not 'layout' in init_vals and 'new_layout' in request.session :
            init_vals['layout'] = request.session['new_layout']
        else:
           request.session['new_layout'] = oc.get_all_renderer_names()[0]

        if not 'stylesheet' in init_vals and 'new_stylesheet' in request.session:
            init_vals['stylesheet'] = request.session['new_stylesheet']
        else:
            request.session['new_stylesheet'] = oc.get_all_style_names()[0]

        if not 'overlay' in init_vals and 'new_overlay' in request.session:
            init_vals['overlay'] = request.session['new_overlay']

        form = forms.MapRenderingJobForm(initial=init_vals)

    return render(request, 'maposmatic/new.html', { 'form' : form })

def map_full(request, id, nonce=None):
    """The full-page map details page.

    Args:
        id (int): the job ID in the database.
    """

    job = get_object_or_404(models.MapRenderingJob, id=id)
    isredirected = request.session.get('redirected', False)
    request.session.pop('redirected', None)

    queue_size = models.MapRenderingJob.objects.queue_size()
    progress = 100
    if queue_size:
        progress = 20 + int(80 * (queue_size -
            job.current_position_in_queue()) / float(queue_size))

    refresh = job.is_rendering() and \
        www.settings.REFRESH_JOB_RENDERING or \
        www.settings.REFRESH_JOB_WAITING

    return render(request, 'maposmatic/map-full.html',
                              { 'map': job, 'redirected': isredirected,
                                'nonce': nonce, 'refresh': refresh,
                                'progress': progress, 'queue_size': queue_size })

def maps(request):
    """Displays all maps and jobs, sorted by submission time, or maps matching
    the search terms when provided."""

    map_list = None

    form = forms.MapSearchForm(request.GET)
    if form.is_valid():
        map_list = (models.MapRenderingJob.objects
                    .order_by('-submission_time')
                    .filter(maptitle__icontains=form.cleaned_data['query']))
        if len(map_list) == 1:
            return HttpResponseRedirect(reverse('map-by-id',
                                                args=[map_list[0].id]))
    else:
        form = forms.MapSearchForm()

    if map_list is None:
        map_list = (models.MapRenderingJob.objects
                    .order_by('-submission_time'))

    paginator = Paginator(map_list, www.settings.ITEMS_PER_PAGE)

    try:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1

        maps = paginator.page(page)
    except (EmptyPage, InvalidPage):
        maps = paginator.page(paginator.num_pages)

    return render(request, 'maposmatic/maps.html',
                              { 'maps': maps, 'form': form,
                                'is_search': form.is_valid(),
                                'pages': helpers.get_pages_list(maps, paginator) })


def recreate(request):
    if request.method == 'POST':
        form = forms.MapRecreateForm(request.POST)
        if form.is_valid():
            job = get_object_or_404(models.MapRenderingJob,
                                    id=form.cleaned_data['id'])

            newjob = models.MapRenderingJob()
            newjob.maptitle = job.maptitle

            newjob.administrative_city = job.administrative_city
            newjob.administrative_osmid = job.administrative_osmid

            newjob.lat_upper_left = job.lat_upper_left
            newjob.lon_upper_left = job.lon_upper_left
            newjob.lat_bottom_right = job.lat_bottom_right
            newjob.lon_bottom_right = job.lon_bottom_right

            newjob.stylesheet = job.stylesheet
            newjob.overlay = job.overlay
            newjob.layout = job.layout
            newjob.paper_width_mm = job.paper_width_mm
            newjob.paper_height_mm = job.paper_height_mm

            newjob.status = 0 # Submitted
            newjob.submitterip = request.META['REMOTE_ADDR']
            newjob.submittermail = None # TODO
            newjob.map_language = job.map_language
            newjob.index_queue_at_submission = (models.MapRenderingJob.objects
                                               .queue_size())
            newjob.nonce = helpers.generate_nonce(models.MapRenderingJob.NONCE_SIZE)

            newjob.track = job.track
            newjob.umap  = job.umap
            newjob.poi_file = job.poi_file

            newjob.save()

            return HttpResponseRedirect(reverse('map-by-id-and-nonce',
                                                args=[newjob.id, newjob.nonce]))

    return HttpResponseBadRequest("ERROR: Invalid request")

def cancel(request):
    if request.method == 'POST':
        form = forms.MapCancelForm(request.POST)
        if form.is_valid():
            job = get_object_or_404(models.MapRenderingJob,
                                    id=form.cleaned_data['id'],
                                    nonce=form.cleaned_data['nonce'])
            job.cancel()

            return HttpResponseRedirect(reverse('map-by-id-and-nonce',
                                                args=[job.id, job.nonce]))

    return HttpResponseBadRequest("ERROR: Invalid request")

def api_nominatim(request):
    """Nominatim query gateway."""
    exclude = request.GET.get('exclude', '')
    squery = request.GET.get('q', '')
    lang = None

    if 'HTTP_ACCEPT_LANGUAGE' in request.META:
        # Accept-Language headers typically look like
        # fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3. Unfortunately,
        # Nominatim behaves improperly with such a string: it gives
        # the region name in French, but the country name in
        # English. We split at the first comma to only keep the
        # preferred language, which makes Nominatim work properly.
        lang = request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0]

    try:
        contents = nominatim.query(squery, exclude, with_polygons=False,
                accept_language=lang)
    except Exception as e:
        LOG.exception("Error querying Nominatim")
        contents = []

    return HttpResponse(content=json.dumps(contents),
                        content_type='text/json')

def api_nominatim_reverse(request, lat, lon):
    """Nominatim reverse geocoding query gateway."""
    lat = float(lat)
    lon = float(lon)
    return HttpResponse(json.dumps(nominatim.reverse_geo(lat, lon)),
                        content_type='text/json')

def api_postgis_reverse(request, lat, lon):
    lat = float(lat)
    lon = float(lon)
    cursor = None
    query = """select country_code
                 from country_osm_grid
                where st_contains(geometry,
                                  st_geomfromtext('POINT(%f %f)', 4326))
            """ % (lon, lat)

    try:
        db = gisdb.get()
        if db is None:
            raise Http404("postgis: no database")

        cursor = db.cursor()
        if cursor is None:
            raise Http404("postgis: no cursor")

        cursor.execute(query)
        country_code = cursor.fetchone()
        if country_code is None or len(country_code) < 1:
            raise Http404("postgis: country not found")

        return HttpResponse('{"address": {"country_code": "%s"}}' % country_code[0], content_type='text/json')
    except:
        pass
    finally:
        # Close the DB cursor if necessary
        if cursor is not None and not cursor.closed:
            cursor.close()

    raise Http404("postgis: something went wrong")


def api_papersize(request):
    """API handler to get the compatible paper sizes for the provided layout
    and bounding box."""

    if request.method != 'POST':
        return HttpResponseBadRequest("ERROR: Bad request")

    f = forms.MapPaperSizeForm(request.POST)
    if not f.is_valid():
        return HttpResponseBadRequest("ERROR: Invalid arguments")

    renderer = ocitysmap.OCitySMap(www.settings.OCITYSMAP_CFG_PATH)
    osmid = f.cleaned_data.get('osmid')
    layout = f.cleaned_data.get('layout')
    stylesheet = renderer.get_stylesheet_by_name(
        f.cleaned_data.get('stylesheet'))

    # Determine geographic area
    if osmid is not None:
        try:
            bbox_wkt, area_wkt = renderer.get_geographic_info(osmid)
        except ValueError:
            LOG.exception("Error determining compatible paper sizes")
            raise
        bbox = ocitysmap.coords.BoundingBox.parse_wkt(bbox_wkt)
    else:
        lat_upper_left = f.cleaned_data.get("lat_upper_left")
        lon_upper_left = f.cleaned_data.get("lon_upper_left")
        lat_bottom_right = f.cleaned_data.get("lat_bottom_right")
        lon_bottom_right = f.cleaned_data.get("lon_bottom_right")

        # Check we have correct floats
        if (lat_upper_left == None or lon_upper_left == None
            or lat_bottom_right == None or lon_bottom_right == None):
           return HttpResponseBadRequest("ERROR: Invalid arguments")

        bbox = ocitysmap.coords.BoundingBox(
            lat_upper_left, lon_upper_left,
            lat_bottom_right, lon_bottom_right)

    renderer_cls = ocitysmap.renderers.get_renderer_class_by_name(layout)
    paper_sizes = sorted(renderer_cls.get_compatible_paper_sizes(bbox),
                         key = lambda p: p[1])

    return HttpResponse(content=json.dumps(paper_sizes),
                        content_type='text/json')

def api_bbox(request, osm_id):
    """API handler that returns the bounding box from an OSM ID polygon."""

    try:
        osm_id = int(osm_id)
    except ValueError:
        return HttpResponseBadRequest("ERROR: Invalid arguments")

    renderer = ocitysmap.OCitySMap(www.settings.OCITYSMAP_CFG_PATH)
    try:
        bbox_wkt, area_wkt = renderer.get_geographic_info(osm_id)
        bbox = ocitysmap.coords.BoundingBox.parse_wkt(bbox_wkt)
        return HttpResponse(content=json.dumps(bbox.as_json_bounds()),
                            content_type='text/json')
    except:
        LOG.exception("Error calculating bounding box for OSM ID %d!" % osm_id)

    return HttpResponseBadRequest("ERROR: OSM ID %d not found!" % osm_id)

def api_polygon(request, osm_id):
    """API handler that returns the polygon outline from an OSM ID polygon."""

    try:
        osm_id = int(osm_id)
    except ValueError:
        return HttpResponseBadRequest("ERROR: Invalid arguments")

    renderer = ocitysmap.OCitySMap(www.settings.OCITYSMAP_CFG_PATH)
    try:
        bbox_wkt, area_wkt = renderer.get_geographic_info(osm_id)
        bbox = ocitysmap.coords.BoundingBox.parse_wkt(bbox_wkt).as_json_bounds()
        return HttpResponse(content=json.dumps({'bbox': bbox, 'wkt': area_wkt}),
                            content_type='text/json')
    except:
        LOG.exception("Error retrieving polygon outline for OSM ID %d!" % osm_id)

    return HttpResponseBadRequest("ERROR: OSM ID %d not found!" % osm_id)




def api_jobs(request, job_id):
    """API handler for external rendering requests"""

    if request.method == 'GET':
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


    if request.method == 'POST':
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



def api_paper_formats(request):
    result = {}
    for p in ocitysmap.OCitySMap.get_all_paper_sizes():
        result[p[0]] = {'width': p[1], 'height': p[2]}

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')



def api_layouts(request):
    result = {}
    for renderer in ocitysmap.OCitySMap().get_all_renderers():
        result[renderer.name] = { "description": renderer.description,
                                  "preview_url": request.build_absolute_uri('/media/img/layout/'+renderer.name+'.png')
                         }

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')




def api_styles(request):
    result = {}
    for style in ocitysmap.OCitySMap().get_all_style_configurations():
        result[style.name] = { "description": style.description, 
                               "annotation": style.annotation,
                               "preview_url": request.build_absolute_uri('/media/img/style/'+style.name+'.png')
                             }

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')




def api_overlays(request):
    result = {}
    for overlay in ocitysmap.OCitySMap().get_all_overlay_configurations():
        result[overlay.name] = { "description": overlay.description, 
                                 "annotation": overlay.annotation,
                                 "preview_url": request.build_absolute_uri('/media/img/overlay/'+overlay.name+'.png')
                               }

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')




def api_job_stati(request):
    # TODO do not hard-code these, get them from OCitysMap cleanly
    result = {
        "0": "Submitted",
        "1": "In progress",
        "2": "Done",
        "3": "Done w/o files",
        "4": "Cancelled"
    }

    return HttpResponse( content=json.dumps(result, indent=4, sort_keys=True, default=str), content_type='text/json')

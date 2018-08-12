{% comment %}
 coding: utf-8

 maposmatic, the web front-end of the MapOSMatic city map generation system
 Copyright (C) 2012  David Decotigny
 Copyright (C) 2012  Frédéric Lehobey
 Copyright (C) 2012  Pierre Mauduit
 Copyright (C) 2012  David Mentré
 Copyright (C) 2012  Maxime Petazzoni
 Copyright (C) 2012  Thomas Petazzoni
 Copyright (C) 2012  Gaël Utard

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
{% endcomment %}
{% load i18n %}
{% load extratags %}

/**
 * Map creation wizard.
 */

var BBOX_MAXIMUM_LENGTH_IN_KM = {{ BBOX_MAXIMUM_LENGTH_IN_METERS }} / 1000;

var locationFilter = null;
var map = wizardmap($('#step-location-map'));
var country = null;
var languages = $('#id_map_language').html();

jQuery.fn.reverse = [].reverse;

$('#wizard').carousel({'interval': false});

/**
 * When the carousel initiates its slide, trigger the 'prepare' event on the
 * slide that is about to be activated.
 */
$('#wizard').bind('slide.bs.carousel', function(e) {
  $(e.relatedTarget).trigger('prepare');
});

/**
 * The 'slid' event is triggered when the carousel finishes a slide in either
 * direction. This function is called by the 'slid' event handler to make sure
 * the prev/next links are in the * correct state based on the position in the
 * carousel.
 */
$('#wizard').bind('slid.bs.carousel', setPrevNextLinks);

$('#wizard-step-location label').click(function(e) {
  $('#id_administrative_city').val('');
  $('#id_administrative_osmid').val('');
  country = null;
  $(this).tab('show');
  setPrevNextLinks();

  // If we're switching to the administrative boundary / city search tab, reset
  // the focus inside the input field.
  if ($(this).attr('for') == 'id_mode_0') {
    $('#id_administrative_city').focus();
  }

  // If it's the first time we switch to the bounding box tab, initialize the
  // minimap.
  if ($(this).attr('for') == 'id_mode_1' && !map) {
    map = wizardmap($('#step-location-map'));
  }
  if ($(this).attr('for') == 'id_mode_2' && !map) {
    map = wizardmap($('#step-location-map'));
  }
  if ($(this).attr('for') == 'id_mode_3' && !map) {
    map = wizardmap($('#step-location-map'));
  }
});

/**
 * Bind the keyup event on the map title field to control the disabled state of
 * the final submit button. The button can only be pressed if a map title is
 * present. The rest of the validation is assumed to have been taken care of at
 * each step boundary.
 */
$('#id_maptitle').bind('keyup', function(e) {
  if ($(this).val()) {
    $('#id_go_next_btn').removeAttr('disabled');
  } else {
    $('#id_go_next_btn').attr('disabled', 'disabled');
  }
});

function setPrevNextLinks() {
  var current = $('#wizard .carousel-inner div.item.active');
  var first   = $('#wizard .carousel-inner div.item:first-child');
  var last    = $('#wizard .carousel-inner div.item:last-child');

  $('#prevlink').hide();
  $('#nextlink').hide();
  if (current.attr('id') == first.attr('id')) {
    if ($('#id_administrative_osmid').val()) {
      $('#nextlink').show();
    }
  } else if (current.attr('id') == last.attr('id')) {
    $('#prevlink').show();
  } else {
    $('#prevlink').show();
    $('#nextlink').show();
  }
}


/*
$('#wizard').bind('slid.bs.carousel', function (e) {
    switch($(e.target).find(".active")[2].id) {
    case 'wizard-step-paper-size':
	fetch_paper_sizes();
    }
})
*/

$('#wizard-step-paper-size').bind('prepare', function(e) {
  $('#paper-selection').hide();
  $('#paper-size-loading-error').hide();
  $('#paper-size-loading').show();
  $('#nextlink').hide();

  var args = null;
  if ($('#id_administrative_osmid').val()) {
    args = {
      osmid: $('#id_administrative_osmid').val(),
    };
  } else {
    args = {
      lat_upper_left: $('#id_lat_upper_left').val(),
      lon_upper_left: $('#id_lon_upper_left').val(),
      lat_bottom_right: $('#id_lat_bottom_right').val(),
      lon_bottom_right: $('#id_lon_bottom_right').val()
    };
  }

  args['layout'] = $('input[name=layout]:checked').val();
  args['stylesheet'] = $('input[name=stylesheet]:checked').val();
  args['overlay'] = $('input[name=overlay]:checked').val();

  $.ajax('/apis/papersize/', { type: 'post', data: args })
    .complete(function() { $('#paper-size-loading').hide(); })
    .error(function() { $('#paper-size-loading-error').show(); })
    .success(function(data) {

      function get_paper_def(paper) {
        for (i in data) {
          if (paper == data[i][0]) {
            return data[i];
          }
        }

        return null;
      }

      function handle_paper_size_click(w, h, p_ok, l_ok, l_preferred) {
        var l = $('#paper-selection input[value=landscape]');
        var p = $('#paper-selection input[value=portrait]');

        if (l_ok) {
          l.removeAttr('disabled');
          if (!p_ok) { l.attr('checked', 'checked'); }
        } else {
          l.attr('disabled', 'disabled');
          p.attr('checked', 'checked');
        }

        if (p_ok) {
          p.removeAttr('disabled');
          if (!l_ok) { p.attr('checked', 'checked'); }
        } else {
          p.attr('disabled', 'disabled');
          l.attr('checked', 'checked');
        }

        if (l_ok && p_ok) {
          if (l_preferred) {
            l.attr('checked', 'checked');
          } else {
            p.attr('checked', 'checked');
          }
        }
        $('#id_paper_width_mm').val(w);
        $('#id_paper_height_mm').val(h);
      }

      var default_paper = null;

      $.each($('#paper-size ul li'), function(i, item) {
        $(item).hide();

        var paper = $('label input[value]', item).val();
        var def = get_paper_def(paper);
        if (def) {
          $('label', item).bind('click', function() {
            handle_paper_size_click(def[1], def[2], def[3], def[4], def[6]);
          });

          if (def[5]) {
            default_paper = $(item);
          }

          $(item).show();

          // TODO: fix for i18n
          if (paper == 'Best fit') {
            w = def[1] / 10;
            h = def[2] / 10;
            $('label em.papersize', item).html('(' + w.toFixed(1) + ' &times; ' + h.toFixed(1) + ' cm²)');
          }
        }
      });

      $('label input', default_paper).click();
      $('#paper-selection').show();
      $('#nextlink').show();
    });
});

$('#wizard-step-lang-title').bind('prepare', function(e) {
  // Prepare the language list
  var list = $('#id_map_language');
  list.html(languages);

  /*
   * The goal is to build a list of languages in which we have first
   * the languages matching the current country code, then an empty
   * disabled entry used as a separator and finally all other
   * languages. To do so, we use prependTo(), which adds elements at
   * the beginning of the list. So we start by prepending the
   * separator, then the "no localization" special language, and
   * finally the languages matching the current country code.
   */
  $('<option disabled="disabled"></option>').prependTo(list);
  $('option[value=C]', list).prependTo(list);
  list.children('option').reverse().each(function() {
    if (country && $(this).val().match('.._' + country.toUpperCase() + '\..*') != null) {
      $(this).prependTo(list);
    }
  });
  $('option:first', list).attr('selected', 'selected');

  // Seed the summary fields
  if ($('#id_administrative_osmid').val()) {
    $('#summary-location').text($('#id_administrative_city').val());
  } else {
    $('#summary-location').html(
      '(' + $('#id_lat_upper_left').val() + ', ' +
            $('#id_lon_upper_left').val() + ')' +
      '&nbsp;&rarr;&nbsp;' +
      '(' + $('#id_lat_bottom_right').val() + ', ' +
            $('#id_lon_bottom_right').val() + ')');
  }

  $('#summary-layout').text($('input[name=layout]:checked').parent().text().trim());
  $('#summary-stylesheet').text($('input[name=stylesheet]:checked').parent().text().trim());
  $('#summary-overlay').text($('input[name=overlay]:checked').parent().text().trim());
  $('#summary-paper-size').text(
      ($('input[value=landscape]').is(':checked')
          ? '{% trans "Landscape" %}'
          : '{% trans "Portrait" %}'
      ) + ', ' + $('input[name=papersize]:checked').parent().text().trim());
});

function lonAdjust(lon) {
  while (lon > 180.0)  lon -= 360.0;
  while (lon < -180.0) lon += 360.0;
  return lon;
}


function wizardmap(elt) {
  var map = create_map($('#step-location-map'));
  var lock = false;
  var bbox = null;
  var bbox_style = {
    fill: true,
    fillColor: "#FFFFFF",
    fillOpacity: 0.5,
    stroke: true,
    strokeOpacity: 0.8,
    strokeColor: "#FF0000",
    strokeWidth: 2
  };
  var countryquery = null;
  locationFilter = new L.LocationFilter({buttonPosition: 'topright'});
  locationFilter.on("change", function (e) {
      bbox = e.target.getBounds();
      map.fitBounds(bbox);
      update_fields();
  });
  locationFilter.on("enabled", function (e) {
      bbox = e.target.getBounds();
      map.fitBounds(bbox);
      update_fields();
  });
  locationFilter.on("disabled", function (e) {
      bbox = null;
      update_fields();
  });
  locationFilter.addTo(map);

  // locate client position
  L.control.locate().addTo(map);
      
  // search button
  map.addControl( new L.Control.Search({
      url: '//nominatim.openstreetmap.org/search?format=json&q={s}',
      jsonpParam: 'json_callback',
      propertyName: 'display_name',
      propertyLoc: ['lat','lon'],
      circleLocation: true,
      markerLocation: false,
      autoType: false,
      autoCollapse: true,
      minLength: 2,
      zoom: 17
  }) );

  /**
   * Update the 4 text fields with the area coordinates.
   *
   * If a feature has been drawned (bbox != null), the bounding box of the
   * feature is used, otherwise the map extent is used.
   */
  var update_fields = function() {
    if (lock) {
      return;
    }

    var bounds = (bbox != null) ? bbox : map.getBounds();

    $('#id_lat_upper_left').val(bounds.getNorth().toFixed(4));
    $('#id_lon_upper_left').val(lonAdjust(bounds.getWest()).toFixed(4));
    $('#id_lat_bottom_right').val(bounds.getSouth().toFixed(4));
    $('#id_lon_bottom_right').val(lonAdjust(bounds.getEast()).toFixed(4));

    var center = bounds.getCenter();

    var upper_left   = bounds.getNorthWest();
    var upper_right  = bounds.getNorthEast();
    var bottom_left  = bounds.getSouthWest();
    var bottom_right = bounds.getSouthEast();

    var width  = upper_left.distanceTo(upper_right);
    var height = upper_right.distanceTo(bottom_right);
      
    if (width < {{ BBOX_MAXIMUM_LENGTH_IN_METERS }} &&
        height < {{ BBOX_MAXIMUM_LENGTH_IN_METERS }}) { 
      $('#area-size-alert').hide();
      $('#nextlink').show();

      // Attempt to get the country by reverse geo lookup
      if (countryquery != null) { countryquery.abort(); }
      countryquery = $.getJSON(
        '/apis/reversegeo/' + center.lat + '/' + center.lng + '/',
        function(data) {
          $.each(data, function(i, item) {
            if (typeof item.country_code != 'undefined') {
              country = item.country_code;
            }
          });
        });
    } else {
      $('#area-size-alert').show();
      $('#nextlink').hide();
    }
  };

  /**
   * Set the map bounds and extent to the current values given by the 4 text
   * fields.
   */
  var set_map_bounds_from_fields = function() {
    lock = true;
    set_map_bounds(map, [
      [$('#id_lat_upper_left').val(), $('#id_lon_upper_left').val()],
      [$('#id_lat_bottom_right').val(), $('#id_lon_bottom_right').val()]
    ]);
    lock = false;
  };


  // Bind events. 
  map.on('moveend', update_fields);
  map.on('zoomend', update_fields);

  $('#step-location-bbox input').bind('keydown', function(e) {
    if (bbox) {
      return;
    }

    if (e.keyCode == 38 || e.keyCode == 40) {
      var v = parseFloat($(e.target).val()) + (0.01 * (e.keyCode == 38 ? 1 : -1));
      $(e.target).val(v.toFixed(4));
    }

    set_map_bounds_from_fields();
    update_fields();
  });

  update_fields();
  return map;
}

/* general file upload event handler */
function loadFile(input, onload_func) {
  var file, fr;
  if (typeof window.FileReader !== 'function') {
    console.log("The file API isn't supported on this browser yet.");
    return;
  }
  if (!input) {
    console.log("Um, couldn't find the fileinput element.");
  }
  else if (!input.files) {
    console.log("This browser doesn't seem to support the `files` property of file inputs.");
  }
  else if (!input.files[0]) {
    console.log("Please select a file before clicking 'Load'");
  }
  else {
    file = input.files[0];
    fr = new FileReader();
    fr.onload = receivedText;
    fr.readAsText(file);
  }
  function receivedText() {
    onload_func(fr.result);
  }
}

/* handle upload of GPX files*/
$("#id_track").change(function() {
  loadFile($("#id_track")[0], function(xml) {
    if (/Trident\/|MSIE/.test(window.navigator.userAgent)) {
      // InterNet Explorer 10 / 11
      xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
      xmlDoc.async = false;
      xmlDoc.loadXML(xml);
      if (xmlDoc.parseError.errorCode!=0) {
	alert("not a valid XML file");
	$("#id_track")[0].value = '';
        return false;
      }
    } else {
      var parser = new DOMParser();
      var parsererrorNS = parser.parseFromString('INVALID', 'text/xml').getElementsByTagName("parsererror")[0].namespaceURI;
      var dom = parser.parseFromString(xml, 'text/xml');
      if(dom.getElementsByTagNameNS(parsererrorNS, 'parsererror').length > 0) {
	alert("not a valid XML file");
	$("#id_track")[0].value = '';
	return false;
      }
    }

    var gpx = new L.GPX(xml, { async: false,
                     marker_options: {
                       startIconUrl: false,
                       endIconUrl: false,
                       shadowUrl: false
                     }
                   }
              ).addTo(map);

     var new_bbox = gpx.getBounds();

     if ('_northEast' in new_bbox === false) {
       alert("Not a GPX file");
       $("#id_track")[0].value = '';
       return false;
     }

     $('#locTabs li:nth-child(2) label').tab('show') // Select geo location tab
     $('input:radio[name=mode]').val(['bbox']);
     $('#id_maptitle').val(gpx.get_name());

     new_bbox = new_bbox.pad(0.1)
     map.fitBounds(new_bbox);
     locationFilter.setBounds(new_bbox);
     locationFilter.enable(); 

     return true;
  });
});

// TODO - this shouldn't be hardcoded, but read from the config file instead
var umap_style_mapping = {
    "OpenStreetMap"            : "CartoOsm",
    "OSM-monochrome"           : "CartoOsmBw",
    "OSM Humanitarian (OSM-FR)": "Humanitarian",
    "OSM-Fr"                   : "French",
    "OSM hikebikemap"          : "HikeBikeMap",
    "OSM Deutschland (OSM-DE)" : "GermanCartoOSM",
    "OSM OpenTopoMap"          : "OpenTopoMap",
    "OSM OpenRiverboatMap"     : "OpenRiverboatMap",
    "OSM Toner (Stamen)"       : "Toner"
};

/* handle upload of UMAP files*/
$("#id_umap").change(function() {

    loadFile($("#id_umap")[0], function(umap) {
	var umap_json, layer, feature;
	var new_features = []

	try {
	    umap_json = JSON.parse(umap);
	} catch(e) {
	    alert('This does not look like a valid Umap export file (json parse error)');
	    $("#id_umap")[0].value = '';
	    return false;
	}

	if (! (umap_json.type == 'umap')) {
	    alert('This does not look like a valid Umap export file (wrong or missing type info)');
	    $("#id_umap")[0].value = '';
	    return false;
	}

	for (layer in umap_json.layers) {
	    for (feature in umap_json.layers[layer].features) {
		new_features.push(umap_json.layers[layer].features[feature]);
	    }
	}

	var new_geojson = {'type': 'FeatureCollection', 'features': new_features};

	var json_layer = L.geoJson(new_geojson).addTo(map);
	var new_bbox = json_layer.getBounds();

	if ('_northEast' in new_bbox === false) {
	    alert('Umap file contains no geometry data');
	    $("#id_umap")[0].value = '';
	    return false;
	}

	$('#locTabs li:nth-child(2) label').tab('show') // Select geo location tab
	$('input:radio[name=mode]').val(['bbox']);
	$('#id_maptitle').val(umap_json.properties.name);

	var umap_title;
	try {
	    umap_title = umap_json.properties.tilelayer.name;
	} catch (err) {
	    umap_title = "OSM-Fr";
	}
	if (umap_title in umap_style_mapping) {
	    $("input:radio[name=stylesheet][value='"+umap_style_mapping[umap_title]+"']").prop("checked",true);
	}

	map.fitBounds(new_bbox);

	if (new_bbox.getSouthWest().equals(new_bbox.getNorthEast())) {
	    new_bbox = map.getBounds();
	}

	new_bbox = new_bbox.pad(0.1);
	locationFilter.setBounds(new_bbox);
	locationFilter.enable();

	return true;
    });
});

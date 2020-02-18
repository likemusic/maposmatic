{% load i18n %}
{% load extratags %}

var upload_file_layers = [];
var upload_file_bounds = false;

function clear_upload_layers() {
    var old_layer;
    for (old_layer of upload_file_layers) {
	old_layer.removeFrom(map);
    }
    upload_file_layers = [];
    upload_file_bounds = false;
    $("#file-list").text('');
}

function add_upload_layer(filename, new_layer) {
    new_layer.addTo(map);
    // txt += delim + files[i].name;
    // delim = '; ';

    upload_file_layers.push(new_layer);

    var new_bbox = new_layer.getBounds();

    if (upload_file_bounds == false) {
	upload_file_bounds = new_bbox;
    } else {
	upload_file_bounds.extend(new_bbox);
    }

    map.fitBounds(upload_file_bounds);

    if (upload_file_bounds.getSouthWest().equals(upload_file_bounds.getNorthEast())) {
	upload_file_bounds = map.getBounds();
    }

    upload_file_bounds = upload_file_bounds.pad(0.1);
    map.fitBounds(upload_file_bounds);

    // TODO: fill file list display
    // $("#file-list").text(txt);

    $('#step-location-bbox-tab').tab('show'); // Select geo location tab

    locationFilter.setBounds(upload_file_bounds);
    locationFilter.enable();

    if (new_layer.get_name() != '') {
	$('#id_maptitle').val(new_layer.get_name());
    }
}

$("#id_uploadfile").change(function() {
    var upload_file;

    clear_upload_layers();

    var n = 0;
    for (upload_file of $("#id_uploadfile")[0].files) {
	var fr, file;

	file = upload_file;
	fr = new FileReader();
	fr.filename = file.name;
	fr.filenum = n;
	n = n + 1;
	fr.onload = function (e) {
	    if (e.target.result) {
		layer = verify_upload_file(file.name, e.target.result, e.target.filenum);
		if (layer != false) {
		    add_upload_layer(e.target.filename, layer);
		}
	    } else {
		alert("Could not read " + e.target.filename);
	    }
	};
	fr.readAsText(upload_file);
    }


});

function verify_upload_file(filename, data_str, filenum) {
    if (data_str.startsWith('<?xml')) {
	return verify_gpx_data(data_str, filename, filenum);
    } else if (data_str.startsWith('{')) {
	return verify_umap_data(data_str, filename, filenum);
    }

    alert(filename + ": unknown file type");
    return false;
}

var file_colors = ['blue', 'red', 'green', 'violet', 'orange'];

function verify_gpx_data(data_str, filename, filenum)
{
    if (/Trident\/|MSIE/.test(window.navigator.userAgent)) {
      // InterNet Explorer 10 / 11
      xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
      xmlDoc.async = false;
      xmlDoc.loadXML(data_str);
      if (xmlDoc.parseError.errorCode!=0) {
	alert("not a valid XML file");
        return false;
      }
    } else {
      var parser = new DOMParser();
      var parsererrorNS = parser.parseFromString('INVALID', 'text/xml').getElementsByTagName("parsererror")[0].namespaceURI;
      var dom = parser.parseFromString(data_str, 'text/xml');
      if(dom.getElementsByTagNameNS(parsererrorNS, 'parsererror').length > 0) {
	alert(filename + "is not a valid XML file");
	return false;
      }
    }

    var color = file_colors[filenum % file_colors.length];
    var gpx = new L.GPX(data_str, { async: false,
				    polyline_options: {
					color: color,
					opacity: 0.75,
				    },
				    marker_options: {
					wptIconUrls: false,
					startIconUrl: false,
					endIconUrl: false,
					shadowUrl: false,
				    }
				  },
		       );

     var new_bbox = gpx.getBounds();

     if ('_northEast' in new_bbox === false) {
       alert(filename + "is not a valid GPX file");
       return false;
     }

    return gpx;
}


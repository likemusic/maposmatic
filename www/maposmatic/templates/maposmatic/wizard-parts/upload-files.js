{% load i18n %}
{% load extratags %}

$("#id_uploadfile").change(function() {
    files = $("#id_uploadfile")[0].files;
    var txt = '';
    var delim = '';
    for (var i = 0; i < files.length; i++) {
	if (verify_upload_file(files[i])) {
	    txt += delim + files[i].name;
	    delim = '; ';
	}
    }
    $("#file-list").text(txt);
});

function verify_upload_file(file) {
    loadFile(file, function(data_str) {
	if (data_str.startsWith('<?xml')) {
	    return verify_gpx_data(data_str, file.name);
	}
	if (data_str.startsWith('{')) {
	    return verify_umap_data(data_str, file.name);
	}
    });
}

function verify_gpx_data(data_str, filename)
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

    var gpx = new L.GPX(data_str, { async: false,
				    marker_options: {
					wptIconUrls: false,
					startIconUrl: false,
					endIconUrl: false,
					shadowUrl: false,
				    }
				  },
		       ).addTo(map);

     var new_bbox = gpx.getBounds();

     if ('_northEast' in new_bbox === false) {
       alert(filename + "is not a valid GPX file");
       return false;
     }

     $('#step-location-bbox').tab('show') // Select geo location tab
     $('#id_maptitle').val(gpx.get_name());

     new_bbox = new_bbox.pad(0.1)
     map.fitBounds(new_bbox);
     locationFilter.setBounds(new_bbox);
     locationFilter.enable();
}


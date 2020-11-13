{% load i18n %}
{% load extratags %}

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
	alert(filename + " is not a valid XML file");
	return false;
      }
    }

    var color = file_colors[filenum % file_colors.length];
    var gpx_layer = new L.GPX(data_str, { async: false,
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

     var new_bbox = gpx_layer.getBounds();

     if ('_northEast' in new_bbox === false) {
       alert(filename + " is not a valid GPX file");
       return false;
     }

    if (gpx_layer.get_name() != '') {
	gpx_layer.maptitle = gpx_layer.get_name();
    }

    return gpx_layer;
}


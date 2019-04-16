{% load i18n %}
{% load extratags %}

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
				   wptIconUrls: false,
				   startIconUrl: false,
				   endIconUrl: false,
				   shadowUrl: false,
			       }
			     },
		       ).addTo(map);

     var new_bbox = gpx.getBounds();

     if ('_northEast' in new_bbox === false) {
       alert("Not a GPX file");
       $("#id_track")[0].value = '';
       return false;
     }

     $('#step-location-bbox').tab('show') // Select geo location tab
     $('#id_maptitle').val(gpx.get_name());

     new_bbox = new_bbox.pad(0.1)
     map.fitBounds(new_bbox);
     locationFilter.setBounds(new_bbox);
     locationFilter.enable();

     return true;
  });
});

{% load i18n %}
{% load extratags %}

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

	$('#step-location-bbox').tab('show') // Select geo location tab
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

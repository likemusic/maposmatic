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

function verify_umap_data(data_str, filename)
{
	var umap_json, layer, feature;
	var new_features = []

	try {
	    umap_json = JSON.parse(data_str);
	} catch(e) {
	    alert(filename + 'does not look like a valid GeoJson or Umap export file (json parse error)');
	    return false;
	}

        if (umap_json.type == 'umap') {
	    for (layer in umap_json.layers) {
		for (feature in umap_json.layers[layer].features) {
		    new_features.push(umap_json.layers[layer].features[feature]);
		}
	    }
	    
	    var new_geojson = {'type': 'FeatureCollection', 'features': new_features};
	    
	    var json_layer = L.geoJson(new_geojson);
	    var new_bbox = json_layer.getBounds();
	    
	    if ('_northEast' in new_bbox === false) {
		alert(filename + ' does not seem to contain geometry data');
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
		// TODO: add a proper function for this
		$("input:radio[name=stylesheet][value='"+umap_style_mapping[umap_title]+"']").prop("checked",true);
	    }

	    return json_layer;
	} else if (umap_json.type == 'FeatureCollection') {
	    var json_layer = L.geoJson(umap_json);
	    var new_bbox = json_layer.getBounds();
	    
	    if ('_northEast' in new_bbox === false) {
		alert(filename + ' does not seem to contain geometry data');
		return false;
	    }
	    
	    $('#step-location-bbox').tab('show') // Select geo location tab
	    	    
	    return json_layer;
	}
    
        alert(filename + ' does not look like a valid GeoJson or Umap export file (wrong or missing type info)');

	return false;
}

{% load i18n %}
{% load extratags %}

var papersize_prepared = false;

function clearPaperSize() {
    papersize_prepared = false;
}

function preparePaperSize() {
  if (papersize_prepared) {
    $('#nextlink').show();
    return;
  }
    
  $('#paper-wait').show();
  $('#paper-size').hide();
  $('#paper-orientation').hide();
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
  if (!args['stylesheet']) {
      args['stylesheet'] = $('#id_stylesheet :selected').val();
  }
  args['overlay'] = $('input[name=overlay]:checked').val();
  if (!args['overlay']) {
      args['overlay'] = $('#id_overlay :selected').val();
  }

  $.ajax('/apis/papersize/', { type: 'post', data: args })
    .fail(function() { $('#paper-size-loading-error').show(); })
    .always(function() { $('#paper-size-loading').hide(); })
    .done(function(data) {

      function get_paper_def(paper) {
        for (i in data) {
          if (paper == data[i]['name']) {
            return data[i];
          }
        }

        return null;
      }

    function handle_paper_size_click(w, h, p_ok, l_ok, l_preferred) {
	if (w == 0 && h == 0) { // Custom
            $('label input', custom_paper_size).prop('checked', true);
	    custom_size();
	    $('#id_custom_width').prop( "disabled", false);
	    $('#id_custom_height').prop( "disabled", false);
	    $('input[value=portrait]').prop("disabled", true);
	    $('input[value=landscape]').prop("disabled", true);
	    return;
	}
	else
	{
	    $('#id_custom_width').prop( "disabled", true);
	    $('#id_custom_height').prop( "disabled", true);
	    $('input[value=portrait]').prop("disabled", false);
	    $('input[value=landscape]').prop("disabled", false);
	}
	
	var l = $('#paper-orientation input[value=landscape]');
        var p = $('#paper-orientation input[value=portrait]');

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
        $('#id_paper_width_mm').val(w.toFixed(0));
        $('#id_paper_height_mm').val(h.toFixed(0));
      }

      var preferrred_paper_size = null;
      var custom_paper_size = null;
      var default_paper_size    = null;
      var default_paper_orientation = 'landscape';

      $.each($('#paper-size ul li'), function(i, item) {
        $(item).hide();
        var input = $('label input[value]', item);
        var paper = input.val();
        var def = get_paper_def(paper);
        if (def) {
          $('label', item).bind('click', function() {
            handle_paper_size_click(def['width'], def['height'], def['portrait_ok'], def['landscape_ok'], def['landscape_preferred']);
          });

          if (def['default']) { // preferred paper size returned by API
            preferrred_paper_size = $(item);
          }
          if ($('#id_default_papersize').val() == paper) {
            default_paper_size = $(item);
            default_paper_orientation = $('#id_default_paperorientation').val();
          }

          $(item).show();

          // TODO: fix for i18n
          if (paper == 'Best fit') {
            w = def['width'];
	    w = w.toFixed(0);

            h = def['height'];
	    h = h.toFixed(0);

	    $('label em.papersize', item).html('(' + w + ' &times; ' + h + ' mm²)');
 	    $("#id_custom_width").val(w);
	    $("#id_custom_height").val(h);

	    $("#id_custom_width").prop('min',w);
	    $("#id_custom_height").prop('min',h);
          }

	  if (paper == 'Custom') {
	    custom_paper_size = $(item);
	  }
        }
      });

      if (default_paper_size) {
        $('label input', default_paper_size).click();
	// TODO: really remember orientation? or go with aspect ratio?
	if (default_paper_orientation) { 
          $('#paper-selection input[value='+default_paper_orientation+']').click();
	}
      } else if(preferrred_paper_size) {
        $('label input', preferrred_paper_size).click();
      }

      $('#paper-wait').hide();
      $('#paper-size').show();
      $('#paper-orientation').show();
      papersize_prepared=true;
      $('#nextlink').show();

    });
}

function custom_size()
{
    w = $("#id_custom_width");
    h = $("#id_custom_height");
    
    if (w.val() < w.prop('min')) {
	w.val(w.prop('min'));
    }

    if (h.val() < h.prop('min')) {
	h.val(h.prop('min'));
    }

    if (w.val() > h.val()) {
	$('input[value=landscape]').prop('checked', true);
	$("#id_paper_width_mm").val(h.val());
	$("#id_paper_height_mm").val(w.val());
    } else {
	$('input[value=portrait]').prop('checked', true);
	$("#id_paper_width_mm").val(w.val());
	$("#id_paper_height_mm").val(h.val());
    }
}

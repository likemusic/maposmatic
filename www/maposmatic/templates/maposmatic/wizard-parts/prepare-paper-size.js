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

      var preferrred_paper_size = null;
      var default_paper_size    = null;
        var default_paper_orientation = 'landscape';

      $.each($('#paper-size ul li'), function(i, item) {
        $(item).hide();
        var input = $('label input[value]', item);
        var paper = input.val();
        var def = get_paper_def(paper);
        if (def) {
          $('label', item).bind('click', function() {
            handle_paper_size_click(def[1], def[2], def[3], def[4], def[6]);
          });

          if (def[5]) { // preferred paper size returned by API
            preferrred_paper_size = $(item);
          }
          if ($('#id_default_papersize').val() == paper) {
            default_paper_size = $(item);
            default_paper_orientation = $('#id_default_paperorientation').val();
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

      if (default_paper_size) {
        $('label input', default_paper_size).click();
	// TODO: really remember orientation? or go with aspect ratio?
        $('#paper-selection input[value='+default_paper_orientation+']').click();
      } else {
        $('label input', preferrred_paper_size).click();
      }

      $('#paper-selection').show();
      papersize_prepared=true;
      $('#nextlink').show();
    });
}


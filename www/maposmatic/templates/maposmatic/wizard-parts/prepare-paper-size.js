{% load i18n %}
{% load extratags %}

var papersize_prepared = false;

function clearPaperSize() {
    papersize_prepared = false;
}

var best_fit_width  = 0;
var best_fit_height = 0;
var best_fit_scale  = 0;

function preparePaperSize() {
  if (papersize_prepared) {
    $('#nextlink').show();
    return;
  }
    
  $('#paper-wait').show();
  $('#paper-size').hide();
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
       var i;

       disable_all_papersizes();

       for (i in data) {
	   var w = data[i]['width'];
	   var h = data[i]['height'];

	   if (data[i]['name'] == 'Best fit') {
	       // update min width/height input limits
	       $('#id_paper_width_mm').attr("min", w);
	       $('#id_paper_height_mm').attr("min", h);

	       best_fit_width  = parseInt(w);
	       best_fit_height = parseInt(h);
	       best_fit_scale  = parseInt( data[i][(data[i]['portrait_ok']) ? 'portrait_scale' : 'landscape_scale']); 
	       
	       $("#best_width").text(w);
	       $("#best_height").text(h);

	       // if current values are below limits -> enforce min size
	       if (w > parseInt($('#id_paper_width_mm').val())
		   || h > parseInt($('#id_paper_height_mm').val())) {
		   $('#id_paper_width_mm').val(w);
		   $('#id_paper_height_mm').val(h);
	       }

	       w = h = 0;
	   }

	   if (data[i]['portrait_ok']) {
	       var scale = Math.round(parseInt(data[i]['portrait_scale']));
	       var scale_txt = "Scale ca. 1:" + scale + "; zoom factor " + data[i]['portrait_zoom'];
	       enable_papersize(w, h, scale_txt);
	   }
	   if (data[i]['landscape_ok']) {
	       var scale = Math.round(parseInt(data[i]['landscape_scale']));
	       var scale_txt = "Scale ca. 1:" + scale + "; zoom factor " + data[i]['landscape_zoom'];
	       enable_papersize(h,w, scale_txt);
	   }
       }

       set_papersize($('#id_paper_width_mm').val(),$('#id_paper_height_mm').val());

       $('#paper-wait').hide();
       $('#paper-size').show();

       return null;
    });
}

function change_papersize()
{
    w = parseInt($('#id_paper_width_mm').val());
    h = parseInt($('#id_paper_height_mm').val());

    wmin = parseInt($('#id_paper_width_mm').attr('min'));
    hmin = parseInt($('#id_paper_height_mm').attr('min'));

    if (w < wmin) {
	w = wmin;
    }

    if (h < hmin) {
	h = hmin;
    }
    
    set_papersize(w,h);
}

function set_papersize(w,h)
{
    // remove existing button mark (if any)
    $('.papersize:enabled').each(function(index) {
	unmark_button($(this));
    });

    // mark button that matches this size (if any)
    var id;

    if (w == 0 && h == 0) {
	id = "#paper_best_fit";
	w = parseInt($("#best_width").text());
	h = parseInt($("#best_height").text());
    } else if (w == parseInt($("#best_width").text())
	       && h == parseInt($("#best_height").text())) {
	id = "#paper_best_fit";
    } else {
	id = "#paper_" + w + "_" + h;
    }

    var button = $(id);

    if (button.length) {
	mark_button(button);
    }

    $("#id_paper_width_mm").val(w);
    $("#id_paper_height_mm").val(h);

    // show preview in HTMK canvas
    var scale = Math.floor(best_fit_scale / Math.min(w / best_fit_width, h / best_fit_height));
    show_paper_preview('paper_canvas', w, h, scale);

    // we can now proceed to next step
    $('#nextlink').show();
}

function show_paper_preview(canvas_name, w, h, scale)
{
    var canvas = document.getElementById(canvas_name);
    var ctx = canvas.getContext("2d");
    var cw = canvas.width;
    var ch = canvas.height;

    w = parseInt(w);
    h = parseInt(h);

    if (w > h) {
	tw = (cw - 20)
	dw = 20;
	th = tw * (h/w);
	dh = (ch-th)/2;
    } else {
	th = (ch - 20)
	dh = 20;
	tw = th * (w/h);
	dw = (cw-tw)/2;
    }

    ctx.save();
    ctx.clearRect(0, 0, cw, ch);
    ctx.strokeStyle = "#000000";
    ctx.setLineDash([]);

    // the actual paper size rectangle
    ctx.strokeRect(dw, dh, tw, th);

    ctx.strokeStyle = "#00007F";
    ctx.fillStyle = "#00007F";

    // height scale

    // top edge
    ctx.beginPath();
    ctx.moveTo(dw - 20, dh);
    ctx.lineTo(dw - 10, dh);
    ctx.stroke();

    // top arrow tip
    ctx.beginPath();
    ctx.moveTo(dw - 15, dh);
    ctx.lineTo(dw - 20, dh+10);
    ctx.lineTo(dw - 10, dh+10);
    ctx.fill();

    // upper half of height bar
    ctx.beginPath();
    ctx.moveTo(dw - 15, dh+10);
    ctx.lineTo(dw - 15, dh+th/2-20);
    ctx.stroke();

    // height text
    ctx.font = '10px serif';
    ctx.textAlign = 'center';
    ctx.save();
    ctx.translate(dw-10, dh+th/2);
    ctx.rotate(-Math.PI/2);
    ctx.fillText(h, 0, 0);
    ctx.restore();

    // lower half of height bar
    ctx.beginPath();
    ctx.moveTo(dw - 15, dh+th-10);
    ctx.lineTo(dw - 15, dh+th/2+20);
    ctx.stroke();

    // bottom arrow tip
    ctx.beginPath();
    ctx.moveTo(dw - 15, dh+th);
    ctx.lineTo(dw - 20, dh+th-10);
    ctx.lineTo(dw - 10, dh+th-10);
    ctx.fill();

    // bottom edge
    ctx.beginPath();
    ctx.moveTo(dw - 20, dh+th);
    ctx.lineTo(dw - 10, dh+th);
    ctx.stroke();

    // left edge
    ctx.beginPath();
    ctx.moveTo(dw, dh-20);
    ctx.lineTo(dw, dh-10);
    ctx.stroke();

    // left arrow tip
    ctx.beginPath();
    ctx.moveTo(dw, dh - 15);
    ctx.lineTo(dw+10, dh - 20);
    ctx.lineTo(dw+10, dh - 10);
    ctx.fill();

    // left half of width bar
    ctx.beginPath();
    ctx.moveTo(dw+10, dh - 15);
    ctx.lineTo(dw+tw/2-20, dh - 15);
    ctx.stroke();

    // width text
    ctx.font = '10px serif';
    ctx.textAlign = 'center';
    ctx.fillText(w, dw+tw/2, dh - 10);

    // right half of width bar
    ctx.beginPath();
    ctx.moveTo(dw+tw-10, dh - 15);
    ctx.lineTo(dw+tw/2+20, dh - 15);
    ctx.stroke();

    // right arrow tip
    ctx.beginPath();
    ctx.moveTo(dw+tw, dh - 15);
    ctx.lineTo(dw+tw-10, dh - 20);
    ctx.lineTo(dw+tw-10, dh - 10);
    ctx.fill();

    // right edge
    ctx.beginPath();
    ctx.moveTo(dw+tw, dh - 20);
    ctx.lineTo(dw+tw, dh - 10);
    ctx.stroke();

    // dashed paper diagonals
    ctx.beginPath();
    ctx.strokeStyle = "#000000";
    ctx.setLineDash([4, 2]);
    ctx.moveTo(dw, dh);
    ctx.lineTo(dw+tw, dh+th);
    ctx.moveTo(dw, dh+th);
    ctx.lineTo(dw+tw, dh);
    ctx.stroke();

    ctx.font = '10px serif';
    ctx.textAlign = 'center';
    ctx.strokeStyle = "#00007F";
    ctx.fillStyle = "#00007F";
    ctx.fillText('ca. 1:' + scale, dw+tw/2, dh+th/4);
    ctx.fillText('zoom '+ scaleDenominator2zoom(scale), dw+tw/2, dh+3*th/4);

    ctx.restore();
}

function enable_button(b, txt)
{
    b[0].classList.remove("btn-success");
    b[0].classList.remove("btn-outline-secondary");
    b[0].classList.add("btn-primary");

    b[0].removeAttribute("disabled");

    b.attr("title", txt);
}

function disable_button(b)
{
    b[0].classList.remove("btn-primary");
    b[0].classList.remove("btn-success");
    b[0].classList.add("btn-outline-secondary");
    
    b[0].setAttribute("disabled", "");

    b.attr("title", "");
}

function mark_button(b)
{
    b[0].classList.remove("btn-primary");
    b[0].classList.add("btn-success");
}

function unmark_button(b)
{
    b[0].classList.remove("btn-success");
    b[0].classList.add("btn-primary");
}

function disable_all_papersizes()
{
    $('.papersize:enabled').each(function(index) {
	disable_button($(this));
    });
}

function disable_papersize(w,h)
{
    var id = "#paper_" + w + "_" + h;

    var button = $(id);

    if (button.length) {
	disable_button(b);
    }
}

function enable_papersize(w, h, txt)
{
    var id;

    if (w >0 && h>0) {
	id = "#paper_" + w + "_" + h;
    } else {
	id = "#paper_best_fit";
	w = parseInt($("#best_width").text());
	h = parseInt($("#best_height").text());
    }

    var button = $(id);

    if (button.length) {
	enable_button(button, txt);
    }
}


function scaleDenominator2zoom(scale_denom)
{
    if (scale_denom < 500)       return 20;
    if (scale_denom < 1250)      return 19;
    if (scale_denom < 2500)      return 18;
    if (scale_denom < 5000)      return 17;
    if (scale_denom < 12500)     return 16;
    if (scale_denom < 25000)     return 15;
    if (scale_denom < 50000)     return 14;
    if (scale_denom < 100000)    return 13;
    if (scale_denom < 200000)    return 12;
    if (scale_denom < 400000)    return 11;
    if (scale_denom < 750000)    return 10;
    if (scale_denom < 1500000)   return 9;
    if (scale_denom < 3000000)   return 8;
    if (scale_denom < 6500000)   return 7;
    if (scale_denom < 12500000)  return 6;
    if (scale_denom < 25000000)  return 5;
    if (scale_denom < 50000000)  return 4;
    if (scale_denom < 100000000) return 3;
    if (scale_denom < 200000000) return 2;
    if (scale_denom < 500000000) return 1;
    return 0;
}

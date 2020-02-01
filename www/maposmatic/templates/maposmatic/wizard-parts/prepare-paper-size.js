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

	       $("#ww").text(w);
	       $("#hh").text(h);

	       enable_papersize(0,0);

	       // if current values are below limits -> enforce min size
	       if (w > parseInt($('#id_paper_width_mm').val())
		   || h > parseInt($('#id_paper_height_mm').val())) {
		   $('#id_paper_width_mm').val(w);
		   $('#id_paper_height_mm').val(h);
	       }
	       continue;
	   }

	   if (data[i]['portrait_ok']) {
	       enable_papersize(w,h);
	   }
	   if (data[i]['landscape_ok']) {
	       enable_papersize(h,w);
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
	h = hmin;
    }

    if (h < hmin) {
	h = hmin;
    }
    
    set_papersize(w,h);
}

function set_papersize(w,h)
{
    $('.papersize:enabled').each(function(index) {
	$(this)[0].classList.remove("btn-success");
	$(this)[0].classList.add("btn-primary");
    });

    var id;

    if (w >0 && h>0) {
	id = "#paper_" + w + "_" + h;
    } else {
	id = "#paper_best_fit";
	w = parseInt($("#ww").text());
	h = parseInt($("#hh").text());
    }

    var button = $(id);

    if (button.length) {
	button[0].classList.remove("btn-primary");
	button[0].classList.add("btn-success");
    }

    $("#id_paper_width_mm").val(w);
    $("#id_paper_height_mm").val(h);

    var canvas = document.getElementById('paper_canvas');
    // canvas.width = canvas.height * (canvas.clientWidth / canvas.clientHeight);
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

    $('#nextlink').show();
}

function disable_all_papersizes()
{
    $('.papersize:enabled').each(function(index) {
	$(this)[0].classList.remove("btn-success");
	$(this)[0].classList.remove("btn-primary");
	$(this)[0].classList.add("btn-outline-secondary");

	$(this)[0].setAttribute("disabled", "");
    });
}

function disable_papersize(w,h)
{
    var id = "#paper_" + w + "_" + h;

    var button = $(id);

    if (button.length) {
	button[0].classList.remove("btn-primary");
	button[0].classList.remove("btn-success");
	button[0].classList.add("btn-outline-secondary");

	button[0].setAttribute("disabled", "");
    }
}

function enable_papersize(w,h)
{
    var id;

    if (w >0 && h>0) {
	id = "#paper_" + w + "_" + h;
    } else {
	id = "#paper_best_fit";
	w = parseInt($("#ww").text());
	h = parseInt($("#hh").text());
    }

    var button = $(id);

    if (button.length) {
	button[0].classList.remove("btn-success");
	button[0].classList.remove("btn-outline-secondary");
	button[0].classList.add("btn-primary");

	button[0].removeAttribute("disabled");
    }
}

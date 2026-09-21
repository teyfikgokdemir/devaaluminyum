$(document).ready(function(){
						   $( ".ucak").css({ left : '2920px',top:'400px'});
						   
///////////////////////////////// FORM //////////////////////////////						   
///////////////////////////////// iletisim //////////////////////////////
  $(".iletisimbuton").click(function(){  
								$('#ibugitsin').fadeOut(1); 
								$('#ibugelsin').fadeIn("slow");
								$('#sonuc2').fadeIn('slow');
								setTimeout( function(){ $('#ibugelsin').fadeOut('slow'); $('#sonuc2').fadeOut('slow'); $('#ibugitsin').delay(1000).fadeIn('slow'); },4100);
								
								
  });
  
$('#ibugelsin').hide();
$('#isonuc').hide();
///////////////////////////////// iletisim //////////////////////////////


$(".ackapa").click( function() {   
  
    $me = $(this);
    $me.toggleClass('off');
    if($me.is(".off")){
		$(".k1").removeClass( "havuz1" );
		$(".k1").addClass( "havuz2" );

    }else {
		$(".k1").removeClass( "havuz2" );
		$(".k1").addClass( "havuz1" );       

    }
	
});



$( ".b1" )
  .mouseover(function() {
    $( ".b1").css({top:'400px'});
  })
  .mouseout(function() {
    $( ".b1").css({top:'410px'});
});


$( ".b2" )
  .mouseover(function() {
    $( ".b2").css({top:'380px'});
  })
  .mouseout(function() {
    $( ".b2").css({top:'390px'});
});



$( document ).on( "mousemove", function( event ) {
  $( ".test" ).text( "pageX: " + event.pageX + ", pageY: " + event.pageY );
  PX = event.pageX / 30;
  PY = event.pageY / 30;
  $( ".dallar1").css({ left : '-'+PX+'px'});
});




//////////////////////////////////////////////
var div = $('#yukari');
var start = $(div).offset().top;
$.event.add(window, "scroll", function() {
var p = $(window).scrollTop();
 $(div).css('position',((p)>start) ? 'fixed' : 'static');
 $(div).css('bottom',((p)>start) ? '10px' : '');
 $(div).css('right',((p)>start) ? '10px' : '');
 $(div).css('z-index',((p)>start) ? '5000' : '');
 $(div).css('display',((p)>start) ? 'block' : '');
});
//////////////////////////////////////////////

      $(function() {
          $("#yukari").click(function() {
              $("html,body").stop().animate({ scrollTop: "0" }, 1000);
          });
      });
      //$(window).scroll(function() {
          //var uzunluk = $(document).scrollTop();
          // 300 degeri sabit bir uzunluk
          // herhangi bir elemente göre yukari elementini 
          // aktiflestirmek istersek o elementin top degerini bulup
          // bu degere göre yukari elementini aktiflestirebiliriz.
          // if(uzunluk < $("#alanId").position().top) gibi.
          //if (uzunluk > 300) $("#yukari").fadeIn(500);
          //else { $("#yukari").fadeOut(500); }
      //});

//////////////////////////////////////////////
function aliver( isim )
{
    alert('merhaba ' + isim);
}
}); //document end
//////////////////////////////////////////////
function sayfagizle(sayfaId){
if(
$("." + sayfaId + "").is(":visible")) {
$("." + sayfaId + "").slideUp(1000); // .fadeOut
} else {
$("." + sayfaId + "").slideDown(1000); // .fadeIn
}	
return false;
}
//////////////////////////////////////////////
$(function() {
$(".img").lazyload({
placeholder : "images/lazy.gif",
effect : "fadeIn"
});
});
///////////////////////////////////////////////////////////////////////
Shadowbox.init({handleOversize: "resize",modal: true,enableKeys:true});
///////////////////////////////////////////////////////////////////////
  $(function(){
     var $container = $('#listele');
     $container.imagesLoaded( function(){
       $container.masonry({
         itemSelector : '.listele'
       });
     });
 
  });
///////////////////////////////////////////////////////////////////////


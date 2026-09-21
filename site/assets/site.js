(function(){
  function ready(fn){
    if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",fn);
    else fn();
  }
  ready(function(){
    const banner=document.getElementById("cookie-banner");
    const accept=document.getElementById("cookie-accept");
    const reject=document.getElementById("cookie-reject");
    try{
      const consent=localStorage.getItem("deva_cookie_consent");
      if(consent && banner) banner.remove();
      if(accept) accept.addEventListener("click",function(){
        localStorage.setItem("deva_cookie_consent","accepted");
        if(banner) banner.remove();
      });
      if(reject) reject.addEventListener("click",function(){
        localStorage.setItem("deva_cookie_consent","rejected");
        if(banner) banner.remove();
      });
    }catch(e){}

    const interactiveCards=document.querySelectorAll(".service-card,.blog-card,.card");
    interactiveCards.forEach(function(card){
      card.addEventListener("pointermove",function(e){
        const r=card.getBoundingClientRect();
        card.style.setProperty("--mx",(e.clientX-r.left)+"px");
        card.style.setProperty("--my",(e.clientY-r.top)+"px");
      });
    });

    const backToTop=document.getElementById("back-to-top");
    let scrollTimer=null;
    function updateScrollControl(){
      if(!backToTop) return;
      if(window.scrollY>320){
        backToTop.classList.add("is-active");
        backToTop.setAttribute("aria-hidden","false");
        clearTimeout(scrollTimer);
        scrollTimer=setTimeout(function(){
          backToTop.classList.remove("is-active");
          backToTop.setAttribute("aria-hidden","true");
        },850);
      }else{
        backToTop.classList.remove("is-active");
        backToTop.setAttribute("aria-hidden","true");
      }
    }
    window.addEventListener("scroll",updateScrollControl,{passive:true});
    if(backToTop) backToTop.addEventListener("click",function(){
      window.scrollTo({top:0,behavior:"smooth"});
    });

    const items=document.querySelectorAll(".card,.gallery a,.section-head,.meta-strip,.article-section");
    if("IntersectionObserver" in window){
      const io=new IntersectionObserver(function(entries){
        entries.forEach(function(entry){
          if(entry.isIntersecting){
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },{threshold:0.12,rootMargin:"0px 0px -24px 0px"});
      items.forEach(function(el){
        el.classList.add("reveal");
        io.observe(el);
      });
    }else{
      items.forEach(function(el){el.classList.add("is-visible");});
    }
  });
})();
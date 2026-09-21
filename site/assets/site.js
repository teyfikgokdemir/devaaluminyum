(function(){
  function ready(fn){
    if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",fn);
    else fn();
  }
  ready(function(){
    const banner=document.getElementById("cookie-banner");
    const ok=document.getElementById("cookie-ok");
    try{
      if(localStorage.getItem("deva_cookie_ok")==="1" && banner) banner.remove();
      if(ok) ok.addEventListener("click",function(){
        localStorage.setItem("deva_cookie_ok","1");
        if(banner) banner.remove();
      });
    }catch(e){}

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
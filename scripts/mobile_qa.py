#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import json, sys

BASE="http://127.0.0.1:4173"
CORE=[
 ("/","home"),("/hizmetler/","services"),("/referanslar/","references"),
 ("/blog/","blog"),("/hakkimizda/","about"),("/iletisim/","contact"),
]
SERVICES=[
 "aluminyum-kompozit-kaplama","bina-giris-kompozit-kaplama",
 "fabrika-yonetim-binasi-kompozit-kaplama","aluminyum-dograma",
 "silikon-cephe-kaplama","fransiz-balkon-korkuluklari",
 "balkon-korkuluklari","merdiven-korkuluklari","bina-giris-kapilari",
 "aluminyum-ofis-bolme","fotoselli-otomatik-kapi","cam-balkon-sistemleri",
]
BLOGS=[
 "kayseri-cam-balkon-fiyatlari-2026",
 "katlanir-mi-surgulu-mu-cam-balkon-sistem-secim-rehberi",
 "kompozit-cephe-kaplama-nedir-avantajlari-ve-secim-kriterleri",
 "aluminyum-dograma-nedir-pvc-ile-farklari",
 "balkon-korkuluk-secimi-guvenlik-ve-estetik",
 "fotoselli-otomatik-kapi-sistemleri-secim-rehberi",
 "aluminyum-ofis-bolme-sistemleri",
 "silikon-cephe-sistemleri-nedir",
]
PAGES=CORE+[(f"/{s}/",f"svc-{i}") for i,s in enumerate(SERVICES,1)]+[(f"/blog/{s}/",f"blog-{i}") for i,s in enumerate(BLOGS,1)]
issues=[]
results=[]

with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1)
    for path,name in PAGES:
        resp=page.goto(BASE+path,wait_until="networkidle")
        if not resp or resp.status>=400:
            issues.append(f"{path}: bad response {resp.status if resp else 'none'}")
            continue
        metrics=page.evaluate("""() => ({
          sw: document.documentElement.scrollWidth,
          cw: document.documentElement.clientWidth,
          iw: window.innerWidth,
          menu: getComputedStyle(document.querySelector('.mobile-nav')).display,
          desktop: getComputedStyle(document.querySelector('.menu')).display,
          h1w: document.querySelector('h1')?.getBoundingClientRect().width || 0,
          bodyw: document.body.getBoundingClientRect().width,
          footerMobile: getComputedStyle(document.querySelector('.footer-v2-mobile')).display,
          footerDesktop: getComputedStyle(document.querySelector('.footer-v2-nav')).display,
          logoW: document.querySelector('.brand-new img')?.getBoundingClientRect().width || 0,
          tickerGroups: document.querySelectorAll('.footer-marquee-group').length,
          favicon: document.querySelector('link[rel="icon"]')?.getAttribute('href') || ''
        })""")
        if metrics["sw"] > metrics["iw"] + 2:
            issues.append(f"{path}: horizontal overflow {metrics['sw']} > {metrics['iw']}")
        if metrics["menu"]=="none":
            issues.append(f"{path}: mobile menu hidden")
        if metrics["desktop"]!="none":
            issues.append(f"{path}: desktop nav visible on mobile")
        if metrics["footerMobile"]=="none":
            issues.append(f"{path}: mobile footer accordion hidden")
        if metrics["footerDesktop"]!="none":
            issues.append(f"{path}: desktop footer nav visible on mobile")
        if metrics["h1w"] > metrics["iw"] - 12:
            issues.append(f"{path}: h1 too wide ({metrics['h1w']})")
        if not (80 <= metrics["logoW"] <= 220):
            issues.append(f"{path}: mobile logo width suspicious ({metrics['logoW']})")
        if metrics["tickerGroups"] != 2:
            issues.append(f"{path}: footer ticker group count {metrics['tickerGroups']}")
        if metrics["favicon"] != "/assets/deva-mark.svg":
            issues.append(f"{path}: favicon mismatch {metrics['favicon']}")
        page.locator(".mobile-nav summary").click()
        if not page.locator(".mobile-nav-panel").is_visible():
            issues.append(f"{path}: mobile menu panel did not open")
        # Footer accordion must be operable.
        first=page.locator(".footer-v2-mobile details").first
        first.locator("summary").click()
        if not first.get_attribute("open"):
            issues.append(f"{path}: footer accordion did not open")
        if name in {"home","services","references","blog","about","contact"}:
            page.screenshot(path=f"qa/mobile-{name}.png",full_page=True)
        results.append({"path":path,**metrics})

    page.set_viewport_size({"width":1440,"height":900})
    for path,name in CORE:
        page.goto(BASE+path,wait_until="networkidle")
        desktop=page.evaluate("""() => ({
          menu: getComputedStyle(document.querySelector('.menu')).display,
          mobile: getComputedStyle(document.querySelector('.mobile-nav')).display,
          footerMobile: getComputedStyle(document.querySelector('.footer-v2-mobile')).display,
          footerDesktop: getComputedStyle(document.querySelector('.footer-v2-nav')).display,
          sw: document.documentElement.scrollWidth,
          iw: window.innerWidth
        })""")
        if desktop["menu"]=="none": issues.append(f"{path}: desktop menu hidden")
        if desktop["mobile"]!="none": issues.append(f"{path}: mobile menu visible on desktop")
        if desktop["footerMobile"]!="none": issues.append(f"{path}: mobile footer visible on desktop")
        if desktop["footerDesktop"]=="none": issues.append(f"{path}: desktop footer hidden")
        if desktop["sw"]>desktop["iw"]+2: issues.append(f"{path}: desktop horizontal overflow")
    browser.close()

report={"issues":issues,"tested_mobile_pages":len(results),"mobile_pages":results}
open("qa/mobile-audit.json","w",encoding="utf-8").write(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({"issues":issues,"tested_mobile_pages":len(results)},ensure_ascii=False))
sys.exit(1 if issues else 0)

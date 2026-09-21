#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import json, sys

BASE="http://127.0.0.1:4173"
PAGES=[
 ("/","home"),
 ("/blog/","blog"),
 ("/blog/kayseri-cam-balkon-fiyatlari-2026/","article"),
 ("/aluminyum-kompozit-kaplama/","service"),
 ("/referanslar/","references"),
 ("/iletisim/","contact"),
]
issues=[]
results=[]

with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1)
    for path,name in PAGES:
        page.goto(BASE+path,wait_until="networkidle")
        metrics=page.evaluate("""() => ({
          sw: document.documentElement.scrollWidth,
          cw: document.documentElement.clientWidth,
          iw: window.innerWidth,
          menu: getComputedStyle(document.querySelector('.mobile-nav')).display,
          desktop: getComputedStyle(document.querySelector('.menu')).display,
          h1w: document.querySelector('h1')?.getBoundingClientRect().width || 0,
          bodyw: document.body.getBoundingClientRect().width
        })""")
        if metrics["sw"] > metrics["iw"] + 2:
            issues.append(f"{path}: horizontal overflow {metrics['sw']} > {metrics['iw']}")
        if metrics["menu"]=="none":
            issues.append(f"{path}: mobile menu hidden")
        if metrics["desktop"]!="none":
            issues.append(f"{path}: desktop nav visible on mobile")
        if metrics["h1w"] > metrics["iw"] - 12:
            issues.append(f"{path}: h1 too wide ({metrics['h1w']})")
        page.locator(".mobile-nav summary").click()
        panel=page.locator(".mobile-nav-panel")
        if not panel.is_visible():
            issues.append(f"{path}: mobile menu panel did not open")
        page.screenshot(path=f"qa/mobile-{name}.png",full_page=True)
        results.append({"path":path,**metrics})
    page.set_viewport_size({"width":1440,"height":900})
    page.goto(BASE+"/",wait_until="networkidle")
    desktop=page.evaluate("""() => ({
      menu: getComputedStyle(document.querySelector('.menu')).display,
      mobile: getComputedStyle(document.querySelector('.mobile-nav')).display,
      sw: document.documentElement.scrollWidth,
      iw: window.innerWidth
    })""")
    if desktop["menu"]=="none": issues.append("/: desktop menu hidden")
    if desktop["mobile"]!="none": issues.append("/: mobile menu visible on desktop")
    if desktop["sw"]>desktop["iw"]+2: issues.append("/: desktop horizontal overflow")
    browser.close()

report={"issues":issues,"mobile_pages":results,"desktop":desktop}
open("qa/mobile-audit.json","w",encoding="utf-8").write(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
sys.exit(1 if issues else 0)

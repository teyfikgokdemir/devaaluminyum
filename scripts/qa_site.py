#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import csv, json, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
QA=ROOT/"qa"
QA.mkdir(exist_ok=True)

subprocess.run([sys.executable, str(ROOT/"scripts"/"build_site.py")], check=True)

# Image quality inventory
img_rows=[]
for p in sorted((DIST/"assets"/"recovered").rglob("*")):
    if not p.is_file() or p.suffix.lower() not in {".jpg",".jpeg",".png",".webp",".gif"}:
        continue
    try:
        with Image.open(p) as im:
            w,h=im.size
            mp=(w*h)/1_000_000
            size=p.stat().st_size
            if w>=1600 and h>=900: grade="A"
            elif w>=1200 and h>=675: grade="B"
            elif w>=800 and h>=450: grade="C"
            elif w>=500 and h>=300: grade="D"
            else: grade="E"
            img_rows.append([str(p.relative_to(ROOT)),w,h,round(mp,3),size,grade])
    except Exception:
        img_rows.append([str(p.relative_to(ROOT)),0,0,0,p.stat().st_size,"ERR"])

with (QA/"image-quality.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["path","width","height","megapixels","bytes","grade"]); w.writerows(img_rows)

# Site QA
html_files=sorted(DIST.rglob("index.html"))
issues=[]
pages=[]
for p in html_files:
    rel="/"+str(p.parent.relative_to(DIST)).replace("\\","/").strip("/")
    if rel=="/.": rel="/"
    if rel!="/" and not rel.endswith("/"): rel+="/"
    soup=BeautifulSoup(p.read_text(encoding="utf-8"),"html.parser")
    title=soup.title.get_text(strip=True) if soup.title else ""
    desc=soup.find("meta",attrs={"name":"description"})
    canonical=soup.find("link",attrs={"rel":"canonical"})
    h1=soup.find_all("h1")
    schemas=soup.find_all("script",attrs={"type":"application/ld+json"})
    og_title=soup.find("meta",attrs={"property":"og:title"})
    og_desc=soup.find("meta",attrs={"property":"og:description"})
    og_img=soup.find("meta",attrs={"property":"og:image"})
    twitter=soup.find("meta",attrs={"name":"twitter:card"})
    favicon=soup.find("link",attrs={"rel":"icon"})
    if not title: issues.append([rel,"missing_title"])
    if not desc or not desc.get("content","").strip(): issues.append([rel,"missing_description"])
    if not canonical or not canonical.get("href","").startswith("https://devaaluminyum.com.tr"): issues.append([rel,"bad_canonical"])
    if len(h1)!=1: issues.append([rel,f"h1_count_{len(h1)}"])
    if not schemas: issues.append([rel,"missing_schema"])
    for idx,schema in enumerate(schemas):
        try: json.loads(schema.string or schema.get_text())
        except Exception: issues.append([rel,f"invalid_schema_{idx}"])
    if not og_title or not og_title.get("content","").strip(): issues.append([rel,"missing_og_title"])
    if not og_desc or not og_desc.get("content","").strip(): issues.append([rel,"missing_og_description"])
    if not og_img or not og_img.get("content","").startswith("https://devaaluminyum.com.tr/"): issues.append([rel,"bad_og_image"])
    if not twitter or twitter.get("content")!="summary_large_image": issues.append([rel,"bad_twitter_card"])
    if not favicon or favicon.get("href")!="/assets/deva-mark.svg": issues.append([rel,"bad_favicon"])
    # Internal absolute links
    for a in soup.find_all("a",href=True):
        href=a["href"]
        if href.startswith("/") and not href.startswith("//"):
            clean=href.split("#")[0].split("?")[0]
            if not clean: continue
            target=DIST/clean.lstrip("/")
            ok=False
            if target.is_file(): ok=True
            elif (target/"index.html").exists(): ok=True
            elif clean=="/" and (DIST/"index.html").exists(): ok=True
            if not ok:
                issues.append([rel,"broken_link:"+href])
    pages.append({"path":rel,"title":title,"h1_count":len(h1),"canonical":canonical.get("href","") if canonical else ""})

# sitemap, robots, redirects and critical brand assets
sitemap=(DIST/"sitemap.xml").read_text(encoding="utf-8") if (DIST/"sitemap.xml").exists() else ""
robots=(DIST/"robots.txt").read_text(encoding="utf-8") if (DIST/"robots.txt").exists() else ""
if "User-agent: *" not in robots or "Sitemap: https://devaaluminyum.com.tr/sitemap.xml" not in robots:
    issues.append(["robots.txt","invalid_or_missing_directives"])
for asset in ["assets/deva-logo.svg","assets/deva-mark.svg","assets/styles.css","assets/site.js"]:
    if not (DIST/asset).exists(): issues.append(["assets","missing:"+asset])
for pg in pages:
    if pg["path"]=="/": expected="https://devaaluminyum.com.tr/"
    else: expected="https://devaaluminyum.com.tr"+pg["path"]
    if expected not in sitemap:
        issues.append([pg["path"],"missing_from_sitemap"])

redirects=(DIST/"_redirects").read_text(encoding="utf-8") if (DIST/"_redirects").exists() else ""
required=[
"/Hakkimizda.html","/Sayfa/56/hizmetlerimiz","/Sayfa/72/referanslarimiz","/iletisim.html",
"/Detay/56/153/kayseri--aluminyum-kompozit-kaplama/",
"/Detay/56/167/bina-giris-kompozit-kaplama/",
"/Detay/56/168/fabrika-yonetim-binasi-kompozit-kaplama/",
"/Detay/56/156/kayseri-aluminyum-dograma/",
"/Detay/56/157/kayseri-slikon-cephe-kaplama/",
"/Detay/56/171/fransiz-balkon-korkuluklari/",
"/Detay/56/170/balkon-korkuluklari/",
"/Detay/56/169/merdiven-korkuluklari/",
"/Detay/56/162/kayseri--bina-giris-kapisi/",
"/Detay/56/163/kayseri-aluminyum-ofis-bolmeleri/",
"/Detay/56/164/kayseri--fotoselli-otomatik-kapi-sistemleri-/",
"/Detay/56/158/kayseri-cam-balkon-imalati-ve-montaj/"
]
for old in required:
    if old not in redirects: issues.append(["_redirects","missing:"+old])

grades={}
for r in img_rows: grades[r[-1]]=grades.get(r[-1],0)+1
report={
    "html_pages":len(html_files),
    "expected_min_pages":26,
    "issues":len(issues),
    "issue_list":[{"page":a,"issue":b} for a,b in issues],
    "images":len(img_rows),
    "image_grades":grades,
    "preview_bytes":sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file()),
}
if len(html_files) < 26:
    issues.append(["site",f"too_few_html_pages:{len(html_files)}"])

report["issues"]=len(issues)
report["issue_list"]=[{"page":a,"issue":b} for a,b in issues]
(QA/"site-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(report,ensure_ascii=False))
if issues:
    sys.exit(2)

#!/usr/bin/env python3
import csv, json, re, hashlib, time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

BASE="https://devaaluminyum.com/"
SNAPS=["20250711185606","20250124062100"]
PAGES=[
 "/",
 "/Hakkimizda.html",
 "/Sayfa/56/hizmetlerimiz",
 "/Sayfa/72/referanslarimiz",
 "/iletisim.html",
 "/Sayfa/153/kayseri--aluminyum-kompozit-kaplama",
 "/Sayfa/167/bina-giris-kompozit-kaplama",
 "/Sayfa/168/fabrika-yonetim-binasi-kompozit-kaplama",
 "/Sayfa/156/kayseri-aluminyum-dograma",
 "/Sayfa/157/kayseri-slikon-cephe-kaplama",
 "/Sayfa/171/fransiz-balkon-korkuluklari",
 "/Sayfa/170/balkon-korkuluklari",
 "/Sayfa/169/merdiven-korkuluklari",
 "/Sayfa/162/kayseri--bina-giris-kapisi",
 "/Sayfa/163/kayseri-aluminyum-ofis-bolmeleri",
 "/Sayfa/164/kayseri--fotoselli-otomatik-kapi-sistemleri-",
 "/Sayfa/158/kayseri-cam-balkon-imalati-ve-montaj",
 "/rss.php",
 "/xml.php",
]
OUT=Path("archive/targeted"); INV=Path("archive/inventory")
OUT.mkdir(parents=True,exist_ok=True); INV.mkdir(parents=True,exist_ok=True)
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 DevaRecovery/1.0"})
TIMEOUT=12; MAX_FILE=25*1024*1024
records=[]; assets=set()

def replay(ts,url): return f"https://web.archive.org/web/{ts}id_/{url}"

def absu(u):
    if not u: return None
    u=u.strip()
    if u.startswith(("data:","mailto:","tel:","javascript:","#")): return None
    if u.startswith("//"): u="https:"+u
    u=urljoin(BASE,u)
    return urldefrag(u)[0]

def same(u):
    return (urlparse(u).hostname or "").lower() in {"devaaluminyum.com","www.devaaluminyum.com"}

def safe(u):
    x=urlparse(u); p=x.path or "/index.html"
    if p.endswith("/"): p+="index.html"
    if not Path(p).suffix: p+=".html"
    if x.query:
        p=str(Path(p).with_name(Path(p).stem+"__"+hashlib.sha1(x.query.encode()).hexdigest()[:8]+Path(p).suffix))
    return Path(*[re.sub(r"[^A-Za-z0-9._-]+","_",z) for z in Path(p.lstrip("/")).parts])

def fetch_best(url):
    last=None
    for ts in SNAPS:
        try:
            r=S.get(replay(ts,url),timeout=TIMEOUT,allow_redirects=True)
            if r.status_code==200 and len(r.content)>0:
                return ts,r
            last=(ts,r.status_code)
        except Exception as e: last=(ts,type(e).__name__)
    return None,None

# Pages
for path in PAGES:
    url=urljoin(BASE,path.lstrip("/"))
    ts,r=fetch_best(url)
    if not r:
        records.append(["page",url,"",0,0,"failed"]); continue
    data=r.content
    target=OUT/"pages"/ts/safe(url); target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
    ctype=r.headers.get("content-type","")
    title=""; h1=""
    if "html" in ctype.lower() or data.lstrip().startswith(b"<"):
        text=data.decode(r.encoding or "utf-8","ignore")
        soup=BeautifulSoup(text,"html.parser")
        title=soup.title.get_text(" ",strip=True) if soup.title else ""
        h1=" | ".join(x.get_text(" ",strip=True) for x in soup.find_all("h1")[:5])
        for tag,attr in [("img","src"),("script","src"),("link","href"),("source","src"),("video","src")]:
            for el in soup.find_all(tag):
                u=absu(el.get(attr))
                if u: assets.add(u)
        for el in soup.find_all(["img","source"]):
            ss=el.get("srcset")
            if ss:
                for part in ss.split(","):
                    u=absu(part.strip().split(" ")[0])
                    if u: assets.add(u)
        for m in re.finditer(r"url\((['\"]?)(.*?)\1\)",text,re.I):
            u=absu(m.group(2))
            if u: assets.add(u)
    records.append(["page",url,ts,200,len(data),f"title={title}; h1={h1}"])
    time.sleep(.05)

# Seed known gallery + hero from Jan/Jul root.
known=[
"resimler/aaaaaa6c7857455dcedbfa96584abd609a9dde.68d2f5.jpg",
"resimler/aaaaaaa8231de42756dcfe6afbe96dc1b0a2b2.e20428.jpg",
"resimler/aaaaaadf847ee6ffe705b5c65e68d86b1278d6.fd9072.jpg",
"resimler/aaaaaa2614c0c06ceda22c96e9b6de0893de7f.203318.jpg",
"resimler/aaaaaafe70d1b41e921fc3bb9d3d79399c44f6.93ba17.jpg",
"Tema/logo.png",
]
for k in known: assets.add(urljoin(BASE,k))

# Add all gallery urls from Jan probe HTML if present.
probe=Path("archive/probe/20250124062100.html")
if probe.exists():
    txt=probe.read_text(encoding="utf-8",errors="ignore")
    for m in re.finditer(r'(?:src|href)=["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp|svg|pdf))["\']',txt,re.I):
        u=absu(m.group(1))
        if u: assets.add(u)

asset_results=[]
for i,url in enumerate(sorted(assets)):
    if i>=700: break
    ts,r=fetch_best(url)
    if not r:
        asset_results.append([url,"",0,0,"failed"]); continue
    data=r.content
    if len(data)>MAX_FILE:
        asset_results.append([url,ts,200,len(data),"skip_large"]); continue
    target=OUT/"assets"/ts/safe(url); target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
    asset_results.append([url,ts,200,len(data),r.headers.get("content-type","")])
    # CSS dependencies
    if urlparse(url).path.lower().endswith(".css"):
        txt=data.decode("utf-8","ignore")
        for m in re.finditer(r"url\((['\"]?)(.*?)\1\)",txt,re.I):
            u=absu(urljoin(url,m.group(2)))
            if u: assets.add(u)
    time.sleep(.04)

with (INV/"targeted_pages.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["kind","url","snapshot","status","bytes","note"]); w.writerows(records)
with (INV/"targeted_assets.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["url","snapshot","status","bytes","content_type"]); w.writerows(asset_results)

summary={
 "pages_recovered":sum(r[3]==200 for r in records),
 "pages_failed":sum(r[3]!=200 for r in records),
 "assets_discovered":len(assets),
 "assets_recovered":sum(r[2]==200 and r[4]!="skip_large" for r in asset_results),
 "assets_failed":sum(r[2]!=200 for r in asset_results),
 "bytes":sum(r[3] for r in asset_results if isinstance(r[3],int))
}
(INV/"targeted_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False))

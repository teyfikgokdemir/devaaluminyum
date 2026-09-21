#!/usr/bin/env python3
import csv, json, re, hashlib, time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

ITEMS=[
("20250124052125","https://devaaluminyum.com/Sayfa/72/referanslarimiz/","referanslar"),
("20250124052916","https://devaaluminyum.com/Hakkimizda.html","hakkimizda"),
("20250124053400","https://devaaluminyum.com/Sayfa/56/hizmetlerimiz/","hizmetler"),
("20250124060751","https://devaaluminyum.com/Detay/56/153/kayseri--aluminyum-kompozit-kaplama/","kompozit-kaplama"),
("20250124062500","https://devaaluminyum.com/Detay/56/167/bina-giris-kompozit-kaplama/","bina-giris-kompozit"),
("20250124065406","https://devaaluminyum.com/Detay/56/168/fabrika-yonetim-binasi-kompozit-kaplama/","fabrika-yonetim-kompozit"),
("20250124061120","https://devaaluminyum.com/Detay/56/156/kayseri-aluminyum-dograma/","aluminyum-dograma"),
("20250124063340","https://devaaluminyum.com/Detay/56/171/fransiz-balkon-korkuluklari/","fransiz-balkon"),
("20250124072853","https://devaaluminyum.com/Detay/56/170/balkon-korkuluklari/","balkon-korkuluk"),
("20250124054130","https://devaaluminyum.com/Detay/56/169/merdiven-korkuluklari/","merdiven-korkuluk"),
("20250124072352","https://devaaluminyum.com/Detay/56/162/kayseri--bina-giris-kapisi/","bina-giris-kapisi"),
("20250124060157","https://devaaluminyum.com/Detay/56/163/kayseri-aluminyum-ofis-bolmeleri/","ofis-bolmeleri"),
("20250124062922","https://devaaluminyum.com/Detay/56/164/kayseri--fotoselli-otomatik-kapi-sistemleri-/","fotoselli-kapi"),
("20250124063214","https://devaaluminyum.com/Detay/56/158/kayseri-cam-balkon-imalati-ve-montaj/","cam-balkon"),
("20250124061252","https://devaaluminyum.com/iletisim.html","iletisim"),
("20250711185606","https://devaaluminyum.com/","anasayfa-2025-07"),
]

OUT=Path("archive/supplied-snapshots")
INV=Path("archive/inventory")
OUT.mkdir(parents=True,exist_ok=True); INV.mkdir(parents=True,exist_ok=True)
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 DevaRecovery/1.0"})
TIMEOUT=20
MAX_FILE=30*1024*1024
records=[]
asset_refs={}

def replay(ts,url): return f"https://web.archive.org/web/{ts}id_/{url}"
def absu(base,u):
    if not u: return None
    u=u.strip()
    if u.startswith(("data:","mailto:","tel:","javascript:","#")): return None
    if u.startswith("//"): u="https:"+u
    return urldefrag(urljoin(base,u))[0]
def safe(u):
    x=urlparse(u); p=x.path or "/index.html"
    if p.endswith("/"): p+="index.html"
    if not Path(p).suffix: p+=".html"
    if x.query:
        p=str(Path(p).with_name(Path(p).stem+"__"+hashlib.sha1(x.query.encode()).hexdigest()[:8]+Path(p).suffix))
    return Path(*[re.sub(r"[^A-Za-z0-9._-]+","_",z) for z in Path(p.lstrip("/")).parts])

for ts,url,label in ITEMS:
    try:
        r=S.get(replay(ts,url),timeout=TIMEOUT,allow_redirects=True)
        data=r.content
        p=OUT/label/"page.html"; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
        ctype=r.headers.get("content-type","")
        note=""
        if r.status_code==200 and data:
            text=data.decode(r.encoding or "utf-8","ignore")
            soup=BeautifulSoup(text,"html.parser")
            title=soup.title.get_text(" ",strip=True) if soup.title else ""
            h1=" | ".join(x.get_text(" ",strip=True) for x in soup.find_all("h1")[:5])
            note=f"title={title}; h1={h1}"
            assets=set()
            for tag,attr in [("img","src"),("script","src"),("link","href"),("source","src"),("video","src"),("a","href")]:
                for el in soup.find_all(tag):
                    u=absu(url,el.get(attr))
                    if not u: continue
                    ext=Path(urlparse(u).path).suffix.lower()
                    if tag!="a" or ext in {".jpg",".jpeg",".png",".gif",".webp",".svg",".ico",".pdf",".css",".js",".woff",".woff2",".ttf",".eot",".mp4",".webm"}:
                        assets.add(u)
            for el in soup.find_all(["img","source"]):
                ss=el.get("srcset")
                if ss:
                    for part in ss.split(","):
                        u=absu(url,part.strip().split(" ")[0])
                        if u: assets.add(u)
            for m in re.finditer(r"url\((['\"]?)(.*?)\1\)",text,re.I):
                u=absu(url,m.group(2))
                if u: assets.add(u)
            asset_refs[label]=sorted(assets)
            # fetch assets at the exact page timestamp
            for au in sorted(assets):
                try:
                    ar=S.get(replay(ts,au),timeout=TIMEOUT,allow_redirects=True)
                    if ar.status_code!=200 or not ar.content:
                        records.append([label,ts,"asset",au,ar.status_code,0,"failed"])
                        continue
                    if len(ar.content)>MAX_FILE:
                        records.append([label,ts,"asset",au,200,len(ar.content),"skip_large"])
                        continue
                    ap=OUT/label/"assets"/safe(au); ap.parent.mkdir(parents=True,exist_ok=True); ap.write_bytes(ar.content)
                    records.append([label,ts,"asset",au,200,len(ar.content),ar.headers.get("content-type","")])
                except Exception as e:
                    records.append([label,ts,"asset",au,0,0,"error:"+type(e).__name__])
                time.sleep(.03)
        records.append([label,ts,"page",url,r.status_code,len(data),note])
    except Exception as e:
        records.append([label,ts,"page",url,0,0,"error:"+type(e).__name__])

with (INV/"supplied_snapshot_recovery.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["label","timestamp","kind","url","status","bytes","note"]); w.writerows(records)
(INV/"supplied_snapshot_assets.json").write_text(json.dumps(asset_refs,ensure_ascii=False,indent=2),encoding="utf-8")
summary={
 "pages_total":len(ITEMS),
 "pages_recovered":sum(r[2]=="page" and r[4]==200 for r in records),
 "assets_recovered":sum(r[2]=="asset" and r[4]==200 and r[6]!="skip_large" for r in records),
 "assets_failed":sum(r[2]=="asset" and r[4]!=200 for r in records),
}
(INV/"supplied_snapshot_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False))

#!/usr/bin/env python3
import csv, re, time
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

ROOT="https://devaaluminyum.com/"
SRC=Path("archive/supplied-snapshots")
OUT=Path("archive/recovered-root-assets")
INV=Path("archive/inventory")
OUT.mkdir(parents=True,exist_ok=True); INV.mkdir(parents=True,exist_ok=True)
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 DevaRecovery/1.0"})
rows=[]
seen=set()
EXTS={".jpg",".jpeg",".png",".gif",".webp",".svg",".ico",".pdf",".css",".js",".woff",".woff2",".ttf",".eot",".mp4",".webm"}

for page in SRC.glob("*/page.html"):
    label=page.parent.name
    text=page.read_text(encoding="utf-8",errors="ignore")
    soup=BeautifulSoup(text,"html.parser")
    base=ROOT
    b=soup.find("base",href=True)
    if b: base=b["href"]
    urls=set()
    for tag,attr in [("img","src"),("script","src"),("link","href"),("source","src"),("video","src"),("a","href")]:
        for el in soup.find_all(tag):
            v=el.get(attr)
            if not v or v.startswith(("data:","mailto:","tel:","javascript:","#")): continue
            u=urljoin(base,v)
            ext=Path(urlparse(u).path).suffix.lower()
            if tag!="a" or ext in EXTS: urls.add(u)
    for m in re.finditer(r"url\((['\"]?)(.*?)\1\)",text,re.I):
        v=m.group(2).strip()
        if v and not v.startswith("data:"): urls.add(urljoin(base,v))
    # infer original page timestamp from folder's page inventory when possible
    ts=None
    inv=INV/"supplied_snapshot_recovery.csv"
    if inv.exists():
        for line in inv.read_text(encoding="utf-8",errors="ignore").splitlines()[1:]:
            if line.startswith(label+",") and ",page," in line:
                ts=line.split(",")[1]; break
    if not ts: continue
    for u in sorted(urls):
        key=(ts,u)
        if key in seen: continue
        seen.add(key)
        if (urlparse(u).hostname or "").lower() not in {"devaaluminyum.com","www.devaaluminyum.com"}: 
            continue
        wb=f"https://web.archive.org/web/{ts}id_/{u}"
        try:
            r=S.get(wb,timeout=15,allow_redirects=True)
            data=r.content
            status=r.status_code
            if status==200 and data:
                rel=Path(urlparse(u).path.lstrip("/"))
                if not rel.name: rel=rel/"index.html"
                p=OUT/label/rel
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_bytes(data)
                rows.append([label,ts,u,status,len(data),str(p)])
            else:
                rows.append([label,ts,u,status,0,""])
        except Exception as e:
            rows.append([label,ts,u,0,0,type(e).__name__])
        time.sleep(.025)

with (INV/"root_asset_recovery.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["label","timestamp","url","status","bytes","path"]); w.writerows(rows)
print("recovered",sum(r[3]==200 and r[4]>0 for r in rows),"of",len(rows))

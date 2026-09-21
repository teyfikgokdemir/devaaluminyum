#!/usr/bin/env python3
import csv, hashlib, json, re, time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

SNAPSHOTS=["20250124062100","20250711185606"]
ROOT="https://devaaluminyum.com/"
OUT=Path("archive/exact-wayback")
INV=Path("archive/inventory")
OUT.mkdir(parents=True,exist_ok=True); INV.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 DevaAluminyum-Recovery/1.0"})
TIMEOUT=25
MAX_PAGES=180
MAX_ASSETS=1200
MAX_FILE=30*1024*1024

def replay(ts,url):
    return f"https://web.archive.org/web/{ts}id_/{url}"

def same_domain(url):
    h=(urlparse(url).hostname or "").lower()
    return h in {"devaaluminyum.com","www.devaaluminyum.com"}

def safe_rel(url):
    u=urlparse(url)
    p=u.path or "/index.html"
    if p.endswith("/"): p+="index.html"
    if not Path(p).suffix: p+=".html"
    if u.query:
        q=hashlib.sha1(u.query.encode()).hexdigest()[:10]
        p=str(Path(p).with_name(Path(p).stem+"__q_"+q+Path(p).suffix))
    parts=[re.sub(r"[^A-Za-z0-9._-]+","_",x) for x in Path(p.lstrip("/")).parts]
    return Path(*parts)

def get(ts,url,binary=False):
    rr=replay(ts,url)
    r=S.get(rr,timeout=TIMEOUT,allow_redirects=True,stream=binary)
    return r,rr

asset_ext={".jpg",".jpeg",".png",".gif",".webp",".svg",".ico",".pdf",".css",".js",".woff",".woff2",".ttf",".eot",".mp4",".webm",".zip"}

def classify(url,ctype=""):
    ext=Path(urlparse(url).path).suffix.lower()
    c=(ctype or "").lower()
    if c.startswith("image/") or ext in {".jpg",".jpeg",".png",".gif",".webp",".svg",".ico"}: return "image"
    if "pdf" in c or ext==".pdf": return "pdf"
    if "css" in c or ext==".css": return "css"
    if "javascript" in c or ext==".js": return "js"
    if "font" in c or ext in {".woff",".woff2",".ttf",".eot"}: return "font"
    if "html" in c or ext in {"",".html",".htm",".php",".asp",".aspx"}: return "html"
    if ext in {".mp4",".webm"}: return "video"
    return "other"

def norm(base,u):
    if not u or u.startswith(("data:","mailto:","tel:","javascript:","#")): return None
    u=u.strip()
    if u.startswith("//"): u="https:"+u
    u=urljoin(base,u)
    u=urldefrag(u)[0]
    return u

def extract(html,base):
    soup=BeautifulSoup(html,"html.parser")
    links=set(); assets=set()
    for tag,attr in [("a","href"),("img","src"),("script","src"),("link","href"),("source","src"),("video","src")]:
        for el in soup.find_all(tag):
            u=norm(base,el.get(attr))
            if not u: continue
            if tag=="a":
                if same_domain(u): links.add(u)
            else:
                assets.add(u)
    for el in soup.find_all(["img","source"]):
        ss=el.get("srcset")
        if ss:
            for part in ss.split(","):
                u=norm(base,part.strip().split(" ")[0])
                if u: assets.add(u)
    for m in re.finditer(r'url\((["\']?)(.*?)\1\)',html,re.I):
        u=norm(base,m.group(2))
        if u: assets.add(u)
    return links,assets,soup

records=[]
for ts in SNAPSHOTS:
    base_dir=OUT/ts
    pages_dir=base_dir/"pages"; assets_dir=base_dir/"assets"
    pages_dir.mkdir(parents=True,exist_ok=True); assets_dir.mkdir(parents=True,exist_ok=True)
    queue=[ROOT]; seen=set(); assets=set()
    page_count=0
    while queue and page_count<MAX_PAGES:
        url=queue.pop(0)
        if url in seen or not same_domain(url): continue
        seen.add(url)
        try:
            r,rr=get(ts,url)
            ctype=r.headers.get("content-type","")
            if r.status_code!=200:
                records.append([ts,"page",url,rr,r.status_code,ctype,0,"failed"])
                continue
            text=r.text
            target=pages_dir/safe_rel(url)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(text,encoding="utf-8",errors="ignore")
            page_count+=1
            links,newassets,soup=extract(text,url)
            for l in sorted(links):
                if l not in seen and len(queue)<MAX_PAGES*2: queue.append(l)
            assets.update(newassets)
            title=(soup.title.get_text(" ",strip=True) if soup.title else "")
            h1=" | ".join(x.get_text(" ",strip=True) for x in soup.find_all("h1")[:3])
            records.append([ts,"page",url,rr,200,ctype,len(text.encode()),f"title={title} ; h1={h1}"])
        except Exception as e:
            records.append([ts,"page",url,replay(ts,url),0,"",0,"error:"+type(e).__name__])
        time.sleep(.08)

    # Also harvest URLs embedded in downloaded CSS later.
    asset_queue=list(sorted(assets))[:MAX_ASSETS]
    seen_assets=set()
    i=0
    while i<len(asset_queue) and i<MAX_ASSETS:
        url=asset_queue[i]; i+=1
        if url in seen_assets: continue
        seen_assets.add(url)
        try:
            r,rr=get(ts,url,binary=True)
            ctype=r.headers.get("content-type","")
            if r.status_code!=200:
                records.append([ts,"asset",url,rr,r.status_code,ctype,0,"failed"])
                continue
            data=b""
            for chunk in r.iter_content(256*1024):
                if chunk:
                    data+=chunk
                    if len(data)>MAX_FILE: break
            if len(data)>MAX_FILE:
                records.append([ts,"asset",url,rr,200,ctype,len(data),"skip_too_large"])
                continue
            target=assets_dir/safe_rel(url)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
            k=classify(url,ctype)
            records.append([ts,k,url,rr,200,ctype,len(data),"recovered"])
            if k=="css":
                try:
                    css=data.decode("utf-8","ignore")
                    for m in re.finditer(r'url\((["\']?)(.*?)\1\)',css,re.I):
                        u=norm(url,m.group(2))
                        if u and u not in seen_assets and len(asset_queue)<MAX_ASSETS:
                            asset_queue.append(u)
                except: pass
        except Exception as e:
            records.append([ts,"asset",url,replay(ts,url),0,"",0,"error:"+type(e).__name__])
        time.sleep(.05)

with (INV/"exact_wayback_recovery.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["timestamp","kind","original","replay","status","content_type","bytes","note"]); w.writerows(records)

summary={}
for ts in SNAPSHOTS:
    rs=[r for r in records if r[0]==ts]
    summary[ts]={
      "pages_recovered":sum(r[1]=="page" and r[4]==200 for r in rs),
      "images_recovered":sum(r[1]=="image" and r[4]==200 and r[7]=="recovered" for r in rs),
      "pdf_recovered":sum(r[1]=="pdf" and r[4]==200 and r[7]=="recovered" for r in rs),
      "assets_recovered":sum(r[1] not in {"page"} and r[4]==200 and r[7]=="recovered" for r in rs),
      "failed":sum(r[4]!=200 for r in rs)
    }
(INV/"exact_wayback_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))

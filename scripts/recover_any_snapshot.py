#!/usr/bin/env python3
import csv, json, re, time
from pathlib import Path
from urllib.parse import urlparse, quote
import requests

ROOT=Path(__file__).resolve().parents[1]
INV=ROOT/"archive"/"inventory"
OUT=ROOT/"archive"/"any-snapshot"
OUT.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 DevaRecovery/1.1"})
TIMEOUT=15
MAX_FILE=30*1024*1024

def is_deva(url):
    return (urlparse(url).hostname or "").lower() in {"devaaluminyum.com","www.devaaluminyum.com"}

def safe_rel(url):
    u=urlparse(url)
    p=u.path or "/index.html"
    if p.endswith("/"): p+="index.html"
    if not Path(p).suffix: p+=".html"
    parts=[re.sub(r"[^A-Za-z0-9._-]+","_",x) for x in Path(p.lstrip("/")).parts]
    return Path(*parts)

def available(url):
    api="https://archive.org/wayback/available"
    r=S.get(api,params={"url":url},timeout=TIMEOUT)
    r.raise_for_status()
    snap=r.json().get("archived_snapshots",{}).get("closest",{})
    if not snap or not snap.get("available"): return None
    return snap

def raw_url(timestamp,original):
    return f"https://web.archive.org/web/{timestamp}id_/{original}"

candidates=set()
targeted=INV/"targeted_assets.csv"
if targeted.exists():
    with targeted.open(encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f):
            if row.get("status")!="200" and is_deva(row.get("url","")):
                candidates.add(row["url"])

# Missing service page
candidates.add("https://devaaluminyum.com/Sayfa/168/fabrika-yonetim-binasi-kompozit-kaplama")
candidates.add("https://devaaluminyum.com/Detay/56/168/fabrika-yonetim-binasi-kompozit-kaplama/")

rows=[]
for i,url in enumerate(sorted(candidates),1):
    try:
        snap=available(url)
        if not snap:
            rows.append([url,"","",0,0,"no_snapshot"])
            continue
        ts=snap.get("timestamp","")
        original=snap.get("url") or url
        r=S.get(raw_url(ts,original),timeout=TIMEOUT,allow_redirects=True,stream=True)
        if r.status_code!=200:
            rows.append([url,ts,original,r.status_code,0,"replay_failed"])
            continue
        buf=bytearray()
        too_large=False
        for chunk in r.iter_content(256*1024):
            if not chunk: continue
            buf.extend(chunk)
            if len(buf)>MAX_FILE:
                too_large=True; break
        if too_large:
            rows.append([url,ts,original,200,len(buf),"too_large"])
            continue
        target=OUT/safe_rel(url)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(bytes(buf))
        rows.append([url,ts,original,200,len(buf),r.headers.get("content-type","")])
    except Exception as e:
        rows.append([url,"","",0,0,"error:"+type(e).__name__])
    if i%20==0: print(i,"/",len(candidates))
    time.sleep(.08)

out=INV/"any_snapshot_recovery.csv"
with out.open("w",encoding="utf-8",newline="") as f:
    w=csv.writer(f); w.writerow(["requested","timestamp","archived_url","status","bytes","note"]); w.writerows(rows)

summary={
    "candidates":len(rows),
    "recovered":sum(r[3]==200 and r[5]!="too_large" for r in rows),
    "no_snapshot":sum(r[5]=="no_snapshot" for r in rows),
    "failed":sum(r[3]!=200 and r[5]!="no_snapshot" for r in rows),
    "bytes":sum(r[4] for r in rows if r[3]==200 and r[5]!="too_large"),
}
(INV/"any_snapshot_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False))

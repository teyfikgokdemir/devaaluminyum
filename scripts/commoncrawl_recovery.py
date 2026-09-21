#!/usr/bin/env python3
import csv, io, json, os, re, time
from pathlib import Path
from urllib.parse import urlparse
import requests
from warcio.archiveiterator import ArchiveIterator

DOMAIN="devaaluminyum.com"
OUT=Path("archive")
INV=OUT/"inventory"
REC=OUT/"commoncrawl"
INV.mkdir(parents=True,exist_ok=True)
REC.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"DevaAluminyum-Recovery/1.0"})
TIMEOUT=10
MAX_FILE=25*1024*1024
MAX_TOTAL=430*1024*1024

def safe_path(url, ts):
    u=urlparse(url)
    host=(u.netloc or "unknown").replace(":","_")
    p=u.path or "/index.html"
    if p.endswith("/"): p += "index.html"
    if not Path(p).suffix: p += ".html"
    parts=[re.sub(r"[^A-Za-z0-9._-]+","_",x) for x in Path(p.lstrip("/")).parts]
    return REC/ts/host/Path(*parts)

def kind(url,mime):
    ext=Path(urlparse(url).path).suffix.lower()
    mime=(mime or "").lower()
    if mime.startswith("image/") or ext in {".jpg",".jpeg",".png",".gif",".webp",".svg",".ico"}: return "image"
    if mime=="application/pdf" or ext==".pdf": return "pdf"
    if "html" in mime or ext in {"",".html",".htm",".php",".asp",".aspx"}: return "html"
    if "css" in mime or ext==".css": return "css"
    if "javascript" in mime or ext==".js": return "js"
    if ext in {".mp4",".webm"}: return "video"
    return "other"

def indexes():
    r=S.get("https://index.commoncrawl.org/collinfo.json",timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def query_index(api):
    params={"url":DOMAIN+"/*","output":"json","filter":"status:200"}
    r=S.get(api,params=params,timeout=TIMEOUT)
    if r.status_code==404: return []
    r.raise_for_status()
    out=[]
    for line in r.text.splitlines():
        line=line.strip()
        if not line: continue
        try: out.append(json.loads(line))
        except: pass
    return out

def recover(entry, used):
    length=int(entry.get("length") or 0)
    offset=int(entry.get("offset") or 0)
    if not length or length>MAX_FILE or used+length>MAX_TOTAL:
        return used,"skip_size",0
    url="https://data.commoncrawl.org/"+entry["filename"]
    r=S.get(url,headers={"Range":f"bytes={offset}-{offset+length-1}"},timeout=TIMEOUT)
    if r.status_code not in (200,206): return used,f"http_{r.status_code}",0
    try:
        record=next(ArchiveIterator(io.BytesIO(r.content)))
        body=record.content_stream().read(MAX_FILE+1)
        if len(body)>MAX_FILE or used+len(body)>MAX_TOTAL: return used,"skip_body_size",len(body)
        target=safe_path(entry["url"],entry.get("timestamp","unknown"))
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(body)
        return used+len(body),"recovered",len(body)
    except Exception as e:
        return used,"error:"+type(e).__name__,0

idx=indexes()
all_entries={}
index_hits=[]
for i,item in enumerate(idx[:8]):
    api=item.get("cdx-api")
    if not api: continue
    try:
        rows=query_index(api)
        index_hits.append({"index":item.get("id",""),"count":len(rows)})
        print(item.get("id"),len(rows))
        for x in rows:
            key=(x.get("url"),x.get("digest"))
            if key not in all_entries:
                all_entries[key]=x
    except Exception as e:
        index_hits.append({"index":item.get("id",""),"count":-1,"error":type(e).__name__})
    time.sleep(.06)

entries=list(all_entries.values())
entries.sort(key=lambda x:(x.get("url",""),x.get("timestamp","")))
with (INV/"commoncrawl_index.csv").open("w",newline="",encoding="utf-8") as f:
    fields=["timestamp","url","status","mime","digest","length","offset","filename","kind"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for e in entries:
        w.writerow({**{k:e.get(k,"") for k in fields[:-1]},"kind":kind(e.get("url",""),e.get("mime",""))})
(INV/"commoncrawl_indexes.json").write_text(json.dumps(index_hits,indent=2),encoding="utf-8")

used=0
results=[]
priority={"html":0,"image":1,"pdf":2,"css":3,"js":4,"video":5,"other":6}
entries.sort(key=lambda e:(priority[kind(e.get("url",""),e.get("mime",""))],e.get("url","")))
for n,e in enumerate(entries,1):
    k=kind(e.get("url",""),e.get("mime",""))
    if k=="other":
        results.append({**e,"kind":k,"result":"skip_type","bytes":0})
        continue
    used,status,b=recover(e,used)
    results.append({**e,"kind":k,"result":status,"bytes":b})
    if n%25==0: print("recover",n,"/",len(entries),"MB",round(used/1024/1024,1))
    time.sleep(.05)

with (INV/"commoncrawl_recovery.csv").open("w",newline="",encoding="utf-8") as f:
    fields=["timestamp","url","status","mime","digest","length","offset","filename","kind","result","bytes"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for r in results: w.writerow({k:r.get(k,"") for k in fields})

summary={
 "indexed_objects":len(entries),
 "recovered":sum(r.get("result")=="recovered" for r in results),
 "images":sum(r.get("result")=="recovered" and r.get("kind")=="image" for r in results),
 "html":sum(r.get("result")=="recovered" and r.get("kind")=="html" for r in results),
 "pdf":sum(r.get("result")=="recovered" and r.get("kind")=="pdf" for r in results),
 "bytes":used
}
(INV/"commoncrawl_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary))

#!/usr/bin/env python3
import csv, hashlib, json, os, re, sys, time
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import requests

DOMAINS = ["devaaluminyum.com", "www.devaaluminyum.com"]
OUT = Path("archive")
REC = OUT / "recovered"
INV = OUT / "inventory"
INV.mkdir(parents=True, exist_ok=True)
REC.mkdir(parents=True, exist_ok=True)

S = requests.Session()
S.headers.update({"User-Agent":"DevaAluminyum-Recovery/1.0 (+https://github.com/teyfikgokdemir/devaaluminyum)"})

MAX_FILE = 25 * 1024 * 1024
MAX_TOTAL = 450 * 1024 * 1024
TIMEOUT = 35
ALLOWED_MIME_PREFIX = ("text/","image/","application/pdf","application/javascript","application/json","application/xml","font/")
ALLOWED_EXT = {".html",".htm",".php",".asp",".aspx",".jpg",".jpeg",".png",".gif",".webp",".svg",".ico",".pdf",".css",".js",".json",".xml",".txt",".woff",".woff2",".ttf",".eot",".mp4",".webm"}

def cdx(domain):
    url="https://web.archive.org/cdx/search/cdx"
    params={
        "url": domain+"/*",
        "output":"json",
        "fl":"timestamp,original,statuscode,mimetype,digest,length",
        "filter":"statuscode:200",
        "collapse":"digest",
        "filter":"statuscode:200",
    }
    r=S.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    data=r.json()
    if not data: return []
    hdr=data[0]
    return [dict(zip(hdr,row)) for row in data[1:]]

def safe_path(original, ts):
    u=urlparse(original)
    host=(u.netloc or "unknown-host").replace(":","_")
    p=u.path or "/index.html"
    if p.endswith("/"): p += "index.html"
    ext=Path(p).suffix.lower()
    if not ext:
        p += ".html"
    if u.query:
        h=hashlib.sha1(u.query.encode()).hexdigest()[:10]
        stem=Path(p).stem
        suff=Path(p).suffix
        p=str(Path(p).with_name(f"{stem}__q_{h}{suff}"))
    parts=[re.sub(r'[^A-Za-z0-9._-]+','_',x) for x in Path(p.lstrip("/")).parts]
    return REC / ts / host / Path(*parts)

def classify(row):
    mt=(row.get("mimetype") or "").lower()
    ext=Path(urlparse(row.get("original","")).path).suffix.lower()
    if mt.startswith("image/") or ext in {".jpg",".jpeg",".png",".gif",".webp",".svg",".ico"}: return "image"
    if mt=="application/pdf" or ext==".pdf": return "pdf"
    if "html" in mt or ext in {".html",".htm",".php",".asp",".aspx",""}: return "html"
    if "css" in mt or ext==".css": return "css"
    if "javascript" in mt or ext==".js": return "js"
    if mt.startswith("font/") or ext in {".woff",".woff2",".ttf",".eot"}: return "font"
    if ext in {".mp4",".webm"}: return "video"
    return "other"

def recover(row, used):
    original=row["original"]
    ts=row["timestamp"]
    target=safe_path(original,ts)
    target.parent.mkdir(parents=True, exist_ok=True)
    raw=f"https://web.archive.org/web/{ts}id_/{original}"
    try:
        r=S.get(raw, timeout=TIMEOUT, stream=True, allow_redirects=True)
        if r.status_code != 200:
            return used, "http_"+str(r.status_code), raw, 0
        clen=int(r.headers.get("content-length") or 0)
        if clen and clen > MAX_FILE:
            return used, "skip_file_too_large", raw, clen
        if clen and used + clen > MAX_TOTAL:
            return used, "skip_repo_budget", raw, clen
        n=0
        with open(target,"wb") as f:
            for chunk in r.iter_content(1024*256):
                if not chunk: continue
                n += len(chunk)
                if n > MAX_FILE or used+n > MAX_TOTAL:
                    f.close()
                    target.unlink(missing_ok=True)
                    return used, "skip_size_limit", raw, n
                f.write(chunk)
        return used+n, "recovered", raw, n
    except Exception as e:
        return used, "error:"+type(e).__name__, raw, 0

rows=[]
for d in DOMAINS:
    try:
        got=cdx(d)
        print("CDX",d,len(got))
        rows.extend(got)
    except Exception as e:
        print("CDX ERROR",d,repr(e), file=sys.stderr)

# De-duplicate exact snapshot-original pairs
uniq={}
for r in rows:
    uniq[(r.get("timestamp"),r.get("original"),r.get("digest"))]=r
rows=list(uniq.values())
rows.sort(key=lambda x:(x.get("original",""),x.get("timestamp","")))

all_csv=INV/"all_snapshots.csv"
with all_csv.open("w",newline="",encoding="utf-8") as f:
    fields=["timestamp","original","statuscode","mimetype","digest","length","kind"]
    w=csv.DictWriter(f,fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow({**{k:r.get(k,"") for k in fields[:-1]},"kind":classify(r)})

# Recover every unique archived object that looks useful.
used=0
results=[]
for i,row in enumerate(rows,1):
    kind=classify(row)
    mt=(row.get("mimetype") or "").lower()
    ext=Path(urlparse(row.get("original","")).path).suffix.lower()
    useful = kind in {"image","pdf","html","css","js","font","video"} or mt.startswith(ALLOWED_MIME_PREFIX) or ext in ALLOWED_EXT
    if not useful:
        results.append({**row,"kind":kind,"result":"skip_type","raw_url":"","bytes":0})
        continue
    used,status,raw,n=recover(row,used)
    results.append({**row,"kind":kind,"result":status,"raw_url":raw,"bytes":n})
    if i % 50 == 0:
        print(f"{i}/{len(rows)} used={used/1024/1024:.1f}MB")
    time.sleep(0.08)

res_csv=INV/"recovery_results.csv"
with res_csv.open("w",newline="",encoding="utf-8") as f:
    fields=["timestamp","original","statuscode","mimetype","digest","length","kind","result","raw_url","bytes"]
    w=csv.DictWriter(f,fieldnames=fields)
    w.writeheader(); w.writerows(results)

summary={
    "snapshots":len(rows),
    "recovered":sum(1 for r in results if r["result"]=="recovered"),
    "images":sum(1 for r in results if r["kind"]=="image" and r["result"]=="recovered"),
    "html":sum(1 for r in results if r["kind"]=="html" and r["result"]=="recovered"),
    "pdf":sum(1 for r in results if r["kind"]=="pdf" and r["result"]=="recovered"),
    "video":sum(1 for r in results if r["kind"]=="video" and r["result"]=="recovered"),
    "bytes":used
}
(INV/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False))

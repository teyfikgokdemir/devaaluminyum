#!/usr/bin/env python3
from pathlib import Path
import csv, requests, time, re

BASE="https://devaaluminyum.com/"
SNAPS=["20250711185606","20250124062100"]
TARGETS=[
"resimler/0-791943236158-814cbe2a8dd11b2dbe4b1926c5e6cfcb.png",
"resimler/0-692121284241-d3d9446802a44259755d38e6d163e820a.jpg",
"resimler/0-738995457426-98f13708210194c475687be6106a3b84a.jpeg",
"resimler/0-462234708188-e4da3b7fbbce2345d7772b0674a318d5a.jpg",
"resimler/0-364913338130-c81e728d9d4c2f636f067f89cc14862ca.jpg",
]
OUT=Path("archive/known-assets")
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 DevaRecovery/1.0"})
rows=[]

def variants(rel):
    p=Path(rel)
    stem=p.stem
    ext=p.suffix
    out=[rel]
    if stem.endswith("a"):
        out.append(str(p.with_name(stem[:-1]+ext)))
    for e in [".jpg",".jpeg",".png"]:
        out.append(str(p.with_suffix(e)))
        if stem.endswith("a"):
            out.append(str(p.with_name(stem[:-1]+e)))
    return list(dict.fromkeys(out))

for requested in TARGETS:
    found=False
    for candidate in variants(requested):
        original=BASE+candidate
        for ts in SNAPS:
            replay=f"https://web.archive.org/web/{ts}id_/{original}"
            try:
                r=S.get(replay,timeout=10,allow_redirects=True)
                if r.status_code==200 and r.content:
                    target=OUT/candidate
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(r.content)
                    rows.append([requested,candidate,ts,200,len(r.content),r.headers.get("content-type","")])
                    found=True
                    break
            except Exception:
                pass
        if found: break
    if not found:
        rows.append([requested,"","",0,0,"failed"])
    time.sleep(.05)

inv=Path("archive/inventory/missing_asset_recovery.csv")
with inv.open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["requested","recovered_as","snapshot","status","bytes","content_type"]); w.writerows(rows)
print(rows)

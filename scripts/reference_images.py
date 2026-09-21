#!/usr/bin/env python3
import csv, os, requests
from pathlib import Path
TS="20250124052125"
BASE="https://devaaluminyum.com/resimler/"
NAMES=["0-620694757554-b6d767d2f8ed5d21a44b0e5886680cb9","0-620694757554-3c59dc048e8850243be8079a5c74d079","0-620694757554-37693cfc748049e45d87b8c7d8b9aacd","0-761997625541-1f0e3dad99908345f7439f8ffabdffc4","0-761997625541-6f4922f45568161a8cdf4ad2299f6d23","0-761997625541-70efdf2ec9b086079795c442636b55fb","0-761997625541-c74d97b01eae257e44aa9d5bade97baf","0-761997625541-9bf31c7ff062936a96d3c8bd1f8f2ff3","0-761997625541-aab3238922bcc25a6f606eb525ffdc56","0-761997625541-c51ce410c124a10e0db5e4b97fc2af39","0-761997625541-c20ad4d76fe97759aa27a0c99bff6710","0-761997625541-6512bd43d9caa6e02c990b0a82652dca","0-761997625541-98f13708210194c475687be6106a3b84","0-648675657737-d3d9446802a44259755d38e6d163e820","0-648675657737-45c48cce2e2d7fbdea1afc51c7c6ad26","0-648675657737-c9f0f895fb98ab9159f51fd0297e236d","0-648675657737-8f14e45fceea167a5a36dedd4bea2543","0-648675657737-1679091c5a880faf6fb5e6087eb1b2dc","0-648675657737-e4da3b7fbbce2345d7772b0674a318d5","0-648675657737-a87ff679a2f3e71d9181a67b7542122c","0-648675657737-eccbc87e4b5ce2fe28308fd9f2a7baf3","0-648675657737-c81e728d9d4c2f636f067f89cc14862c","0-648675657737-c4ca4238a0b923820dcc509a6f75849b"]
OUT=Path("archive/references-images"); OUT.mkdir(parents=True,exist_ok=True)
S=requests.Session(); S.headers.update({"User-Agent":"Mozilla/5.0 DevaRecovery/1.0"})
rows=[]
for name in NAMES:
    for suffix,kind in [(".jpg","full"),("a.jpg","thumb")]:
        src=BASE+name+suffix
        wb=f"https://web.archive.org/web/{TS}id_/{src}"
        try:
            r=S.get(wb,timeout=15,allow_redirects=True)
            p=OUT/(name+suffix)
            if r.status_code==200 and r.content:
                p.write_bytes(r.content)
                rows.append([name,kind,src,200,len(r.content),str(p)])
            else:
                rows.append([name,kind,src,r.status_code,0,""])
        except Exception as e:
            rows.append([name,kind,src,0,0,type(e).__name__])
with open("archive/inventory/reference_images.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["id","kind","source","status","bytes","path"]); w.writerows(rows)
print("full",sum(r[1]=="full" and r[3]==200 for r in rows),"thumb",sum(r[1]=="thumb" and r[3]==200 for r in rows))

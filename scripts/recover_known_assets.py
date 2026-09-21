#!/usr/bin/env python3
from pathlib import Path
import csv, requests, time

BASE="https://devaaluminyum.com/"
SNAPS=["20250711185606","20250124062100"]
OUT=Path("archive/known-assets")
OUT.mkdir(parents=True,exist_ok=True)
S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 DevaRecovery/1.0"})
TIMEOUT=12

assets = [
"Tema/logo.png",
"resimler/aaaaaa6c7857455dcedbfa96584abd609a9dde.68d2f5.jpg",
"resimler/aaaaaaa8231de42756dcfe6afbe96dc1b0a2b2.e20428.jpg",
"resimler/aaaaaadf847ee6ffe705b5c65e68d86b1278d6.fd9072.jpg",
"resimler/aaaaaa2614c0c06ceda22c96e9b6de0893de7f.203318.jpg",
"resimler/aaaaaafe70d1b41e921fc3bb9d3d79399c44f6.93ba17.jpg",
"resimler/0-791943236158-814cbe2a8dd11b2dbe4b1926c5e6cfcb.png",
"resimler/0-692121284241-d3d9446802a44259755d38e6d163e820a.jpg",
"resimler/0-433146404453-45c48cce2e2d7fbdea1afc51c7c6ad26a.jpg",
"resimler/0-738995457426-98f13708210194c475687be6106a3b84a.jpeg",
"resimler/0-992801538758-c9f0f895fb98ab9159f51fd0297e236da.jpeg",
"resimler/0-446567936662-c4ca4238a0b923820dcc509a6f75849ba.jpg",
"resimler/0-214725407200-639245830c396b4594c4edb07b08e22da.jpg",
"resimler/0-462234708188-e4da3b7fbbce2345d7772b0674a318d5a.jpg",
"resimler/0-364913338130-c81e728d9d4c2f636f067f89cc14862ca.jpg",
"resimler/0-913389889372-76b1a56588660586c5835c37378ad644a.jpg",
"resimler/0-802471866709-0eaab519d7112be59f099bf8e4c33903a.jpg",
"resimler/0-511705664519-f28875dc837fbf7ae4776e5948af7a65a.jpg",
"resimler/0-770471526169-1679091c5a880faf6fb5e6087eb1b2dca.jpg",
]
# Existing full-size reference images.
refs = [
"0-620694757554-37693cfc748049e45d87b8c7d8b9aacd.jpg",
"0-620694757554-3c59dc048e8850243be8079a5c74d079.jpg",
"0-620694757554-b6d767d2f8ed5d21a44b0e5886680cb9.jpg",
"0-648675657737-1679091c5a880faf6fb5e6087eb1b2dc.jpg",
"0-648675657737-45c48cce2e2d7fbdea1afc51c7c6ad26.jpg",
"0-648675657737-8f14e45fceea167a5a36dedd4bea2543.jpg",
"0-648675657737-a87ff679a2f3e71d9181a67b7542122c.jpg",
"0-648675657737-c4ca4238a0b923820dcc509a6f75849b.jpg",
"0-648675657737-c81e728d9d4c2f636f067f89cc14862c.jpg",
"0-648675657737-c9f0f895fb98ab9159f51fd0297e236d.jpg",
"0-648675657737-d3d9446802a44259755d38e6d163e820.jpg",
"0-648675657737-e4da3b7fbbce2345d7772b0674a318d5.jpg",
"0-648675657737-eccbc87e4b5ce2fe28308fd9f2a7baf3.jpg",
"0-761997625541-1f0e3dad99908345f7439f8ffabdffc4.jpg",
"0-761997625541-6512bd43d9caa6e02c990b0a82652dca.jpg",
"0-761997625541-6f4922f45568161a8cdf4ad2299f6d23.jpg",
"0-761997625541-70efdf2ec9b086079795c442636b55fb.jpg",
"0-761997625541-98f13708210194c475687be6106a3b84.jpg",
"0-761997625541-9bf31c7ff062936a96d3c8bd1f8f2ff3.jpg",
"0-761997625541-aab3238922bcc25a6f606eb525ffdc56.jpg",
"0-761997625541-c20ad4d76fe97759aa27a0c99bff6710.jpg",
"0-761997625541-c51ce410c124a10e0db5e4b97fc2af39.jpg",
"0-761997625541-c74d97b01eae257e44aa9d5bade97baf.jpg",
]
assets += ["resimler/"+x for x in refs]

rows=[]
for rel in assets:
    original=BASE+rel
    ok=False
    for ts in SNAPS:
        replay=f"https://web.archive.org/web/{ts}id_/{original}"
        try:
            r=S.get(replay,timeout=TIMEOUT,allow_redirects=True)
            if r.status_code==200 and r.content:
                target=OUT/rel
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(r.content)
                rows.append([rel,ts,200,len(r.content),r.headers.get("content-type","")])
                ok=True
                break
        except Exception:
            pass
    if not ok:
        rows.append([rel,"",0,0,"failed"])
    time.sleep(.04)

inv=Path("archive/inventory/known_assets.csv")
inv.parent.mkdir(parents=True,exist_ok=True)
with inv.open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["asset","snapshot","status","bytes","content_type"]); w.writerows(rows)
print("recovered",sum(x[2]==200 for x in rows),"of",len(rows))

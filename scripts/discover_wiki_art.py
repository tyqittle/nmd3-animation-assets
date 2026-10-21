#!/usr/bin/env python3
"""Discover and verify character / skin artwork from specific NMD3 BWIKI pages.

Only archive images explicitly labeled 立绘 (illustration), not thumbnails or avatar icons.
Missing or blocked pages are reported; they do not generate fake catalog entries.
"""
from __future__ import annotations
import hashlib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from urllib import error, parse, request
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog/assets.json"
TARGETS_PATH = ROOT / "catalog/wiki_illustration_targets.json"
REPORT_PATH = ROOT / "reports/wiki_discovery.json"
HOSTS = {"patchwiki.biligame.com"}
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_CANDIDATES = 4

def get(url, referer=None, timeout=17, max_bytes=MAX_IMAGE_BYTES):
    headers = {"User-Agent":"Mozilla/5.0 (compatible; NMD3-asset-reference/1.0)",
               "Accept":"text/html,application/xhtml+xml,image/png,image/webp,image/jpeg;q=0.9,*/*;q=0.7"}
    if referer: headers["Referer"] = referer
    with request.urlopen(request.Request(url, headers=headers), timeout=timeout) as resp:
        if resp.status != 200: raise ValueError("HTTP status "+str(resp.status))
        data=resp.read(max_bytes+1)
        if len(data)>max_bytes: raise ValueError("response too big")
        return data

def original_image_url(raw):
    if not raw: return None
    raw=raw.strip()
    if raw.startswith("//"): raw="https:"+raw
    if raw.startswith("/"): raw=parse.urljoin("https://wiki.biligame.com",raw)
    p=parse.urlsplit(raw)
    if p.hostname not in HOSTS or p.scheme!="https": return None
    path=parse.unquote(p.path)
    if "/images/nmd3/" not in path: return None
    path=re.sub(r"/images/nmd3/thumb/([^/]+/[^/]+/[^/]+\.(?:png|jpg|jpeg|webp))/[^/]+$",r"/images/nmd3/\1",path,flags=re.I)
    m=re.search(r"^/images/nmd3/[a-z0-9]/[a-z0-9]{2}/[A-Za-z0-9]+\.(?:png|jpg|jpeg|webp)$",path,re.I)
    if not m: return None
    return "https://patchwiki.biligame.com"+parse.quote(path,safe="/.")

def candidate_image_urls(html, name, page_url):
    soup=BeautifulSoup(html,"html.parser")
    wanted=name.replace(" ","").replace("（皮肤）","").replace("(皮肤)","").lower()
    result=[]
    for el in soup.select("img"):
        alt=(el.get("alt") or "").replace(" ","").lower()
        if "立绘" not in alt or wanted not in alt: continue
        for attr in ("data-src","data-original","data-lazy-src","src","data-actualsrc"):
            u=original_image_url(el.get(attr))
            if u and u not in result: result.append(u)
        if el.parent and el.parent.name=="a":
            u=original_image_url(el.parent.get("href"))
            if u and u not in result: result.insert(0,u)
    # Wiki file pages can carry the full artwork link even when lazy images differ.
    return result[:MAX_CANDIDATES]

def valid_art(data):
    with Image.open(BytesIO(data)) as im:
        im.verify()
    with Image.open(BytesIO(data)) as im:
        w,h=im.size
        if im.format not in ("PNG","JPEG","WEBP"): raise ValueError("not an image")
        if w<420 or h<450: raise ValueError(f"low resolution {w}x{h}")
        if not 0.35<=w/h<=1.50: raise ValueError(f"not character-portrait shape {w}x{h}")
        # A portrait archive entry must be an isolated character layer rather than a full poster.
        if "A" not in im.getbands():
            raise ValueError("no transparency: likely a full promotional image, not an isolated portrait")
        alpha=im.getchannel("A")
        # 620x780 opaque images occasionally turned out to be complete posters with a logo.
        hist=alpha.histogram()
        transparent=sum(hist[:64])
        if transparent < w*h*0.06:
            raise ValueError(f"insufficient transparent canvas: {transparent/(w*h):.1%}; requires manual review")
        return w,h,im.format,True

def discover(target):
    name=target["name"]
    page="https://wiki.biligame.com/nmd3/"+parse.quote(name,safe="")
    row={"name":name,"source_page":page,"status":"skipped"}
    try:
        html=get(page,timeout=18,max_bytes=3*1024*1024)
        urls=candidate_image_urls(html,name,page)
        if not urls:
            row.update(status="no_explicit_illustration",html_bytes=len(html))
            return row
        for url in urls:
            try:
                data=get(url,referer=page)
                w,h,fmt,alpha=valid_art(data)
                sha=hashlib.sha256(data).hexdigest()
                extension={"PNG":"png","JPEG":"jpg","WEBP":"webp"}[fmt]
                row.update(status="ready",image_url=url,sha256=sha,width=w,height=h,format=fmt,has_alpha=alpha,bytes=len(data),
                           filename=f"skin_{target['slug']}.{extension}",data=data)
                return row
            except Exception as exc:
                row["last_image_error"]=str(exc)[:180]
        row["status"]="all_candidates_invalid"
    except Exception as exc:
        row.update(status="page_error",error=str(exc)[:230])
    return row

def main():
    catalog=json.loads(CATALOG_PATH.read_text("utf-8"))
    targets=json.loads(TARGETS_PATH.read_text("utf-8"))["targets"]
    old_ids={a["id"] for a in catalog["assets"]}
    old_urls={a["image_url"] for a in catalog["assets"]}
    old_hashes={a.get("sha256") for a in catalog["assets"] if a.get("sha256")}
    report=[]; added=[]
    print("Checking",len(targets),"wiki art pages",flush=True)
    # Keep traffic moderate for a community-maintained wiki.
    with ThreadPoolExecutor(max_workers=3) as pool:
        tasks={pool.submit(discover,t):t for t in targets}
        for future in as_completed(tasks):
            row=future.result()
            if row["status"]!="ready":
                print("SKIP",row["name"],row["status"],row.get("error",row.get("last_image_error","")),flush=True)
                report.append(row)
                continue
            t=tasks[future]
            name=row["name"]; id="skin_"+t["slug"]
            if id in old_ids or row["image_url"] in old_urls or row["sha256"] in old_hashes:
                print("DUP",name,flush=True)
                report.append({k:v for k,v in row.items() if k!="data"}|{"status":"duplicate"})
                continue
            path="assets/characters/skins/"+row["filename"]
            (ROOT/path).parent.mkdir(parents=True,exist_ok=True)
            (ROOT/path).write_bytes(row["data"])
            catalog["assets"].append({
                "id":id,"name":name,"category":"characters",
                "subcategory":t.get("asset_type","unreviewed_portrait"),"character":t.get("character","待核对"),
                "image_url":row["image_url"],"source_page":row["source_page"],
                "local_path":path,"download_status":"downloaded",
                "width":row["width"],"height":row["height"],"sha256":row["sha256"],
                "bytes":row["bytes"],"has_alpha":row["has_alpha"],
                "source_verified":"downloaded_from_wiki_page",
                "copyright":"third_party_review_needed","animation_use":"character_layer",
                "quality_tier":"reference_low_res" if row["height"]<700 else "standard_character",
                "classification_source":"wiki_target_metadata", "visual_review":"pending",
                "variant_kind":"combat_style" if t.get("asset_type")=="style_portrait" else ("costume" if t.get("asset_type")=="costume_portrait" else "reference")
            })
            old_ids.add(id);old_urls.add(row["image_url"]);old_hashes.add(row["sha256"])
            added.append(name)
            print("SAVED",name,row["width"],row["height"],row["bytes"],flush=True)
            report.append({k:v for k,v in row.items() if k!="data"})
    catalog["as_of"]="2026-10-21"
    CATALOG_PATH.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT_PATH.parent.mkdir(parents=True,exist_ok=True)
    REPORT_PATH.write_text(json.dumps({"added":added,"attempted":len(targets),"results":report},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("DISCOVERY SUMMARY:",len(added),"new downloaded images out of",len(targets),"pages",flush=True)

if __name__=="__main__": main()

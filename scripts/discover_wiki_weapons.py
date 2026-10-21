#!/usr/bin/env python3
"""Fetch only labeled NMD3 weapon artwork from BWIKI, commit via GitHub Actions.

A source target is not an asset until a real image is downloaded and verified.
"""
from __future__ import annotations
import hashlib, json, re, time
from io import BytesIO
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib import parse, request
from bs4 import BeautifulSoup
from PIL import Image
from discover_wiki_art import original_image_url

# BWIKI displays a generic WuqiBG ring BEFORE the actual weapon. Never index it.
INVALID_SHARED_BG = 'https://patchwiki.biligame.com/images/nmd3/9/98/qt7fjkkslu3cxkr4n9p28kv12cwcihz.png'


def get(url, referer=None, timeout=17, max_bytes=12*1024*1024):
    safe=parse.quote(url,safe=':/?&=%+#')
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
             'Accept':'image/avif,image/webp,image/apng,image/png,image/*;q=0.8,text/html;q=0.7,*/*;q=0.5',
             'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.7',
             'Referer':'https://wiki.biligame.com/nmd3/'}
    with request.urlopen(request.Request(safe,headers=headers),timeout=timeout) as response:
        raw=response.read(max_bytes+1)
        if len(raw)>max_bytes:raise ValueError('Response exceeds maximum bytes')
        return raw


ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"catalog/assets.json"
TARGETS=ROOT/"catalog/wiki_weapon_targets.json"
REPORT=ROOT/"reports/weapon_discovery.json"

def norm(s):
    return re.sub(r"\s+|\.(?:png|jpg|webp)$","",s or "",flags=re.I).lower()

def options(html,name):
    soup=BeautifulSoup(html,"html.parser")
    key=norm(name)
    result=[]
    for im in soup.select("img"):
        alt=norm(im.get("alt") or im.get("title") or "")
        # Weapon variants are different objects. Do not rename a skin as the base weapon.
        valid={key, norm("Wuqi"+name),norm("武器"+name),norm(name+"图鉴")}
        if alt not in valid:
            continue
        for attr in ("data-src","data-original","data-lazy-src","src","data-actualsrc"):
            raw=im.get(attr)
            # The ring is labeled as the weapon in the alt attribute but is NOT artwork.
            if raw and 'wuqibg.' in parse.unquote(raw).lower():
                continue
            url=original_image_url(raw)
            if url and url!=INVALID_SHARED_BG and url not in result:
                result.append(url)
        if im.parent and im.parent.name=="a":
            raw=im.parent.get('href')
            if raw and 'wuqibg.' in parse.unquote(raw).lower():
                continue
            url=original_image_url(raw)
            if url and url!=INVALID_SHARED_BG and url not in result:
                result.insert(0,url)
    return result[:4]

def inspect(data):
    with Image.open(BytesIO(data)) as im: im.verify()
    with Image.open(BytesIO(data)) as im:
        w,h=im.size
        if im.format not in ("PNG","JPEG","WEBP"): raise ValueError("not a supported image")
        if min(w,h)<290: raise ValueError("low resolution %sx%s"%(w,h))
        if not 0.4<=w/h<=2.5: raise ValueError("bad weapon image aspect %sx%s"%(w,h))
        return w,h,im.format,"A" in im.getbands()

def discover(t):
    page=t["page"]
    row={"name":t["name"],"source_page":page}
    try:
        html=get(page,timeout=15,max_bytes=4*1024*1024)
        choices=options(html,t["name"])
        if not choices: return {**row,"status":"no_matching_weapon_art"}
        for url in choices:
            try:
                raw=get(url,referer=page,timeout=16)
                w,h,fmt,alpha=inspect(raw)
                return {**row,"status":"ready","image_url":url,"raw":raw,
                        "sha256":hashlib.sha256(raw).hexdigest(),
                        "width":w,"height":h,"bytes":len(raw),"has_alpha":alpha,
                        "extension":{"PNG":"png","JPEG":"jpg","WEBP":"webp"}[fmt]}
            except Exception as e: row["last_image_error"]=str(e)[:160]
        return {**row,"status":"all_candidates_invalid"}
    except Exception as e:
        return {**row,"status":"page_error","error":str(e)[:180]}

def main():
    doc=json.loads(CATALOG.read_text("utf-8"))
    targets=json.loads(TARGETS.read_text("utf-8"))["targets"]
    ids={a["id"] for a in doc["assets"]}
    by_id={a["id"]:a for a in doc["assets"]}
    urls={a.get("image_url") for a in doc["assets"]}
    hashes={a.get("sha256") for a in doc["assets"] if a.get("sha256")}
    report=[]; added=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(discover,t):t for t in targets}
        for fut in as_completed(futures):
            t=futures[fut]; x=fut.result()
            if x["status"]!="ready":
                report.append(x);print("SKIP",t["name"],x["status"],x.get("error",x.get("last_image_error","")),flush=True);continue
            aid="wiki_weapon_"+t["slug"]
            previous=by_id.get(aid)
            repairing=previous is not None and previous.get("image_url")==INVALID_SHARED_BG
            if ((aid in ids and not repairing) or
                x["image_url"] in urls or x["sha256"] in hashes):
                report.append({k:v for k,v in x.items() if k!="raw"}|{"status":"duplicate"})
                print("DUP",t["name"],x["image_url"],flush=True);continue
            out=f"assets/weapons/wiki/{aid}.{x['extension']}"
            path=ROOT/out;path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(x["raw"])
            info={
                "id":aid,"name":t["name"],"category":"weapons",
                "subcategory":t.get("asset_type","weapon_art"),
                "weapon_family":t.get("weapon_family",t["name"]),
                "variant_kind":"appearance" if t.get("asset_type")=="weapon_appearance" else "original",
                "classification_source":"wiki_labeled_weapon_image", "visual_review":"pending",
                "review_status":"categorized",
                "image_url":x["image_url"],
                "source_page":x["source_page"],"local_path":out,
                "download_status":"downloaded","source_verified":"weapon_image_label_on_wiki_page",
                "copyright":"third_party_review_needed",
                "animation_use":"prop_layer" if x["has_alpha"] else "weapon_reference_only",
                "quality_tier":"standard_weapon" if x["width"]>=450 else "reference_low_res",
                "width":x["width"],"height":x["height"],"has_alpha":x["has_alpha"],
                "bytes":x["bytes"],"sha256":x["sha256"]}
            if repairing:
                # Replace only the confirmed mislabeled circular UI background record.
                previous.update(info)
                print("REPAIRED WuqiBG as",t["name"],flush=True)
            else:
                doc["assets"].append(info)
            ids.add(aid);urls.add(x["image_url"]);hashes.add(x["sha256"]);added.append(t["name"])
            report.append({k:v for k,v in x.items() if k!="raw"})
            print("SAVED",t["name"],x["width"],x["height"],flush=True)
    doc["as_of"]="2026-10-21"
    CATALOG.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n","utf-8")
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps({"attempted":len(targets),"added":added,"results":report},ensure_ascii=False,indent=2)+"\n","utf-8")
    print("WEAPON DISCOVERY:",len(added),"downloaded of",len(targets),"targets",flush=True)

if __name__=="__main__": main()

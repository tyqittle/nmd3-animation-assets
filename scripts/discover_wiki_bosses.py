#!/usr/bin/env python3
"""Archive real BWIKI boss images only after validating binary identity and dimensions.

A target page does NOT become a gallery item unless a matching image was downloaded.
"""
from __future__ import annotations
import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from urllib import parse, request

from bs4 import BeautifulSoup
from PIL import Image

from discover_wiki_art import get, original_image_url


def fetch_image(url: str, page: str) -> bytes:
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept':'image/avif,image/webp,image/apng,image/png,image/*;q=0.8,*/*;q=0.5',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.7',
        'Referer':'https://wiki.biligame.com/nmd3/',
    }
    with request.urlopen(request.Request(url,headers=headers),timeout=18) as response:
        if response.status != 200:
            raise ValueError('HTTP '+str(response.status))
        data=response.read(12*1024*1024+1)
        if len(data)>12*1024*1024:
            raise ValueError('Image larger than 12MB')
        return data


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/assets.json"
TARGETS = ROOT / "catalog/wiki_boss_targets.json"
REPORT = ROOT / "reports/boss_discovery.json"


def matching_images(html: bytes, name: str) -> list[str]:
    """Only use image links in the monster's content, not wiki chrome or icons."""
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one(".mw-parser-output") or soup
    sources = []
    for img in content.select("img"):
        alt = (img.get("alt") or img.get("title") or "").strip()
        # Do not confuse boss artwork with icons, generic backgrounds or other monsters.
        if name not in alt or ("系" in alt and alt != name):
            continue
        for attr in ("data-original", "data-src", "data-lazy-src", "src"):
            url = original_image_url(img.get(attr))
            if url and url not in sources:
                sources.append(url)
        link = img.find_parent("a")
        if link:
            url = original_image_url(link.get("href"))
            if url and url not in sources:
                sources.insert(0, url)
    # Most monster articles include a naked full-image link immediately after the
    # named heading. Its IMG alt can be blank, so we also inspect that narrow region.
    heading=next((h for h in content.find_all(['h2','h3'])
                  if name in h.get_text(' ',strip=True)),None)
    if heading is not None:
        for el in heading.next_elements:
            if getattr(el,'name',None) in ('h2','h3'):
                break
            if getattr(el,'name',None) != 'a':
                continue
            raw=el.get('href')
            candidate=original_image_url(raw)
            if candidate and candidate not in sources:
                # Do not use generic MonsterFrontPage/other wiki UI thumbnails.
                if raw and not any(x in parse.unquote(raw).lower() for x in ('monsterfrontpage','breadimg','wiki')):
                    sources.append(candidate)
            if len(sources)>=4:
                break
    return sources[:4]


def inspect(raw: bytes):
    with Image.open(BytesIO(raw)) as image:
        image.verify()
    with Image.open(BytesIO(raw)) as image:
        width, height = image.size
        fmt = image.format
        if fmt not in ("PNG", "JPEG", "WEBP"):
            raise ValueError("Unsupported image format")
        if min(width, height) < 180 or max(width, height) < 300:
            raise ValueError(f"Image too small for Boss card: {width}x{height}")
        if width * height > 24_000_000:
            raise ValueError("Image too large to decode safely")
        if not 0.25 <= width / height <= 4:
            raise ValueError(f"Suspicious aspect ratio {width}x{height}")
        return width, height, "A" in image.getbands(), {"PNG":"png","JPEG":"jpg","WEBP":"webp"}[fmt]


def discover(target: dict):
    result={"name":target["name"],"source_page":target["page"]}
    try:
        direct=target.get("direct_image")
        if direct:
            url=original_image_url(direct)
            if url!=direct:
                return {**result,"status":"unsafe_image_url"}
            candidates=[direct]
        else:
            page=get(parse.quote(target["page"],safe=":/?&=%+#"),timeout=14,max_bytes=3*1024*1024)
            candidates=matching_images(page,target["name"])
        if not candidates:
            return {**result,"status":"no_matching_boss_image"}
        for url in candidates:
            try:
                raw=fetch_image(url,target["page"])
                w,h,alpha,extension=inspect(raw)
                return {**result,"status":"ready","image_url":url,"data":raw,
                        "width":w,"height":h,"bytes":len(raw),"has_alpha":alpha,
                        "sha256":hashlib.sha256(raw).hexdigest(),"extension":extension}
            except Exception as exc:
                result["last_image_error"]=str(exc)[:180]
        return {**result,"status":"image_download_or_validation_failed"}
    except Exception as exc:
        return {**result,"status":"page_error","error":str(exc)[:180]}


def main():
    doc=json.loads(CATALOG.read_text("utf-8"))
    targets=json.loads(TARGETS.read_text("utf-8"))["targets"]
    known_ids={a["id"] for a in doc["assets"]}
    known_urls={a.get("image_url") for a in doc["assets"]}
    known_hashes={a.get("sha256") for a in doc["assets"] if a.get("sha256")}
    reported=[]
    added=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        results={pool.submit(discover,t):t for t in targets}
        for future in as_completed(results):
            t=results[future]
            record=future.result()
            if record["status"]!="ready":
                reported.append(record)
                print("SKIP",t["name"],record["status"],record.get("last_image_error",record.get("error","")),flush=True)
                continue
            ident="wiki_boss_"+t["slug"]
            if ident in known_ids or record["image_url"] in known_urls or record["sha256"] in known_hashes:
                reported.append({k:v for k,v in record.items() if k!="data"} | {"status":"duplicate"})
                print("DUP",t["name"],flush=True)
                continue
            path=f"assets/bosses/wiki/{ident}.{record['extension']}"
            file=ROOT/path
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_bytes(record["data"])
            doc["assets"].append({
                "id":ident,"name":t["name"],"category":"bosses","subcategory":"boss_art",
                "image_url":record["image_url"],"source_page":t["page"],
                "local_path":path,"download_status":"downloaded",
                "source_verified":"matching_bwiki_monster_page","copyright":"third_party_review_needed",
                "animation_use":"boss_reference_only" if not record["has_alpha"] else "boss_layer",
                "width":record["width"],"height":record["height"],
                "has_alpha":record["has_alpha"],"bytes":record["bytes"],
                "sha256":record["sha256"],
                "classification_source":"wiki_monster_page",
                "visual_review":"pending","review_status":"categorized",
                "classification_note":"图片来自对应怪物百科页；人物身份仍待逐图人工复核"
            })
            known_ids.add(ident)
            known_urls.add(record["image_url"])
            known_hashes.add(record["sha256"])
            added.append(t["name"])
            reported.append({k:v for k,v in record.items() if k!="data"})
            print("SAVED",t["name"],record["width"],record["height"],flush=True)
    doc["as_of"]="2026-10-21"
    CATALOG.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n","utf-8")
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps({"attempted":len(targets),"added":added,"results":reported},ensure_ascii=False,indent=2)+"\n","utf-8")
    print(f"BOSS DISCOVERY: {len(added)} real images downloaded of {len(targets)} targets",flush=True)


if __name__=="__main__":
    main()

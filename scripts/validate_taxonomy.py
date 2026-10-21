#!/usr/bin/env python3
"""Strict, read-only check of NMD3 gallery category metadata and CSV export."""
from __future__ import annotations
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"catalog/assets.json"
CSV=ROOT/"catalog/assets.csv"
TYPES={
    "characters":{"base_portrait","style_portrait","costume_portrait","pose_reference",
                  "alternate_portrait","character_reference","unreviewed_portrait","awakening_portrait"},
    "weapons":{"weapon_art","weapon_appearance"},
    "bosses":{"boss_art","monster_group_reference"},
    "scenes":{"scene_reference"},
    "wallpapers":{"wallpaper_composite","unverified_wallpaper"},
    "promos":{"event_promo","promo_composite"},
    "effects":{"skill_effect_reference"},
}

def check():
    data=json.loads(CATALOG.read_text(encoding="utf-8"))
    rows=data["assets"]
    problems=[]
    ids=set()
    paths=set()
    for x in rows:
        ident=x.get("id","")
        category=x.get("category","")
        subtype=x.get("subcategory","")
        if not ident or ident in ids:problems.append(f"duplicate/empty id {ident!r}")
        ids.add(ident)
        if category not in TYPES or subtype not in TYPES.get(category,set()):
            problems.append(f"{ident}: invalid category/subtype {category}/{subtype}")
        if category=="characters" and not x.get("character"):
            problems.append(f"{ident}: missing parent ninja")
        if category=="weapons" and not x.get("weapon_family"):
            problems.append(f"{ident}: missing weapon family")
        if not x.get("local_path","").startswith("assets/"):
            problems.append(f"{ident}: path outside assets")
        if not x.get("source_page","").startswith("https://"):
            problems.append(f"{ident}: no original HTTPS source")
        if x.get("visual_review") not in {"pending","verified","type_reviewed_identity_pending"}:
            problems.append(f"{ident}: visual review must be explicit")
        if x.get("review_status") not in {"categorized","quarantined"}:
            problems.append(f"{ident}: missing/invalid review status")
        if x.get("review_status")=="quarantined" and not x.get("classification_note"):
            problems.append(f"{ident}: quarantined item needs an explanation")
        if x.get("download_status")=="downloaded":
            for k in ("bytes","width","height"):
                if not isinstance(x.get(k),int) or x[k]<=0:
                    problems.append(f"{ident}: invalid verified field {k}")
            if len(x.get("sha256",""))!=64:problems.append(f"{ident}: missing sha256")
            if x.get("local_path") in paths:problems.append(f"{ident}: duplicate file path")
            paths.add(x.get("local_path"))
        elif x.get("download_status") not in {"not_downloaded","failed","candidate"}:
            problems.append(f"{ident}: invalid download status")
    taxonomy=data.get("taxonomy",{})
    if set(taxonomy.get("categories",{}))!=set(TYPES):
        problems.append("catalog.taxonomy category map out of sync")
    missing_sub=set.union(*TYPES.values())-set(taxonomy.get("subcategories",{}))
    if missing_sub:problems.append("unlisted subcategories: "+repr(sorted(missing_sub)))
    with CSV.open(encoding="utf-8",newline="") as handle:
        reader=csv.DictReader(handle)
        export=list(reader)
        if len(export)!=len(rows):problems.append("CSV length differs from JSON")
        if "subcategory" not in (reader.fieldnames or []):problems.append("CSV missing subtype column")
        for i,(x,y) in enumerate(zip(rows,export)):
            for key in ("id","name","category","subcategory","character","weapon_family","review_status","download_status"):
                expected=str(x.get(key,""))
                if y.get(key)!=expected:problems.append(f"CSV row {i+2}, {key}: {y.get(key)!r} != {expected!r}")
    stats=Counter(a["category"] for a in rows if a.get("download_status")=="downloaded")
    print("downloaded",sum(stats.values()),"category counts",dict(stats),"unarchived",len(rows)-sum(stats.values()))
    if problems:
        for p in problems:print("ERROR:",p)
        raise SystemExit(f"Taxonomy validation failed: {len(problems)} issue(s)")
    print("Taxonomy and CSV: PASS")

if __name__=="__main__":check()

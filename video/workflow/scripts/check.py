#!/usr/bin/env python3
"""Check a Ninja 3 storyboard before trying to render."""
import json,sys
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
KINDS={"intro","dialogue","system","outro"}
EFFECTS={"normal","disconnect","panic","boss"}
def asset(path):
    if not isinstance(path,str) or not path.startswith("assets/"):
        raise ValueError("only repository assets/ paths are allowed")
    p=(ROOT/path).resolve()
    if not p.is_relative_to((ROOT/"assets").resolve()):
        raise ValueError("unsafe relative path")
    return p

def load(path):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    errors=[]
    if data.get("schema_version")!="1.0":errors.append("expected schema_version 1.0")
    if not isinstance(data.get("duration"),(int,float)) or data["duration"]<=0:
        errors.append("invalid duration")
    people=data.get("characters",{})
    if not isinstance(people,dict) or not people:errors.append("characters empty")
    def check_file(name):
        try:
            p=asset(name)
            if not p.is_file():errors.append("missing: "+str(name))
            else:
                with Image.open(p) as im:im.verify()
        except Exception as exc:errors.append(f"invalid image {name}: {exc}")
    check_file(data.get("background"))
    for name,char in people.items():
        if not char.get("name") or not char.get("color","").startswith("#"):
            errors.append("missing name/color: "+name)
        check_file(char.get("path"))
    shots=data.get("shots",[])
    if not shots:errors.append("no shots")
    previous=0.
    for n,shot in enumerate(shots):
        try:
            start,end=float(shot["start"]),float(shot["end"])
            if abs(start-previous)>.002:errors.append(f"gap or overlap before shot {n}: {previous} / {start}")
            if end<=start:errors.append(f"shot {n}: end <= start")
            if shot.get("kind") not in KINDS:errors.append(f"shot {n}: invalid kind")
            if shot.get("effect","normal") not in EFFECTS:errors.append(f"shot {n}: unknown effect")
            if shot.get("kind")=="dialogue" and shot.get("speaker") not in people:
                errors.append(f"shot {n}: unknown speaker")
            if not isinstance(shot.get("lines"),list) or not shot["lines"] or not all(isinstance(x,str) and x.strip() for x in shot["lines"]):
                errors.append(f"shot {n}: missing subtitle lines")
            if any(len(x)>33 for x in shot.get("lines",[])):
                print("WARN: very long subtitle line in shot",n)
            previous=end
        except Exception as exc:errors.append(f"shot {n}: {exc}")
    if abs(previous-data.get("duration",0))>.002:errors.append("timeline does not cover duration")
    if errors:raise ValueError("\n".join(errors))
    print(f"PASS: {len(shots)} shots, {len(people)} actors, {previous:.2f}s, local assets verified")
    return data

if __name__=="__main__":
    if len(sys.argv)!=2:sys.exit("Usage: check.py video/workflow/episodes/name.json")
    load(sys.argv[1])

#!/usr/bin/env python3
"""Download openly licensed video clips from Wikimedia Commons."""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"assets"/"footage"
OUT.mkdir(parents=True,exist_ok=True)
UA="FactsEmpireScienceShorts/1.0 (educational production)"
def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))
def allowed(meta):
    name=meta.get("LicenseShortName",{}).get("value","").lower()
    link=meta.get("LicenseUrl",{}).get("value","").lower()
    return ("public domain" in name or "cc0" in name or
            ("cc by" in name and "nc" not in name and "nd" not in name) or
            "creativecommons.org/licenses/by/" in link or
            "creativecommons.org/licenses/by-sa/" in link)
def main():
    topic=sys.argv[1] if len(sys.argv)>1 else "auto"
    queries=["water droplets macro","hydrophobic water repellent surface","water splash close up","waterproof seal gasket","water on phone screen"]
    manifest=[]
    for i,q in enumerate(queries):
        params={"action":"query","format":"json","generator":"search","gsrsearch":"filetype:video "+q,"gsrnamespace":6,"gsrlimit":15,"prop":"imageinfo","iiprop":"url|extmetadata"}
        try:
            data=get_json("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params))
        except Exception as e:
            print("Search failed:",q,e); continue
        pages=data.get("query",{}).get("pages",{})
        for page in pages.values():
            info=(page.get("imageinfo") or [{}])[0]
            meta=info.get("extmetadata") or {}
            url=info.get("url","")
            if not url.lower().split("?")[0].endswith((".mp4",".webm",".ogv")) or not allowed(meta):
                continue
            label=page.get("title","clip").split(":",1)[-1]
            safe=re.sub(r"[^A-Za-z0-9_-]+","_",label)[:50] or "clip"
            suffix=Path(urllib.parse.urlparse(url).path).suffix
            dest=OUT/(f"scene_{i:02}_{safe}{suffix}")
            try:
                req=urllib.request.Request(url,headers={"User-Agent":UA})
                with urllib.request.urlopen(req,timeout=60) as response:
                    content=response.read(25*1024*1024+1)
                if len(content)>25*1024*1024: continue
                dest.write_bytes(content)
                manifest.append({"file":str(dest.relative_to(ROOT)),"title":page.get("title",""),"source_url":info.get("descriptionurl",""),"creator":meta.get("Artist",{}).get("value",""),"license":meta.get("LicenseShortName",{}).get("value",""),"license_url":meta.get("LicenseUrl",{}).get("value",""),"attribution":meta.get("Attribution",{}).get("value","")})
                print("Downloaded:",dest.name)
                break
            except Exception as e:
                print("Skipped candidate:",e)
        time.sleep(0.25)
    (ROOT/"output").mkdir(exist_ok=True)
    (ROOT/"output"/"asset_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print("Openly licensed video files downloaded:",len(manifest))
if __name__=="__main__": main()

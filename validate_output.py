#!/usr/bin/env python3
"""Basic render preflight for the generated Shorts package."""
import json, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/"output"
videos=list(out.glob("*_science_short.mp4"))
if not videos:
    raise SystemExit("FAIL: no rendered MP4 found")
video=videos[-1]
probe=subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(video)],text=True)
data=json.loads(probe)
streams=data.get("streams",[])
v=next((s for s in streams if s.get("codec_type")=="video"),None)
a=next((s for s in streams if s.get("codec_type")=="audio"),None)
if not v or (v.get("width"),v.get("height"))!=(1080,1920):
    raise SystemExit("FAIL: expected 1080x1920 video stream")
if not a:
    raise SystemExit("FAIL: no audio stream")
duration=float(data.get("format",{}).get("duration",0))
if duration<15 or duration>60:
    raise SystemExit(f"FAIL: unexpected duration {duration:.1f}s")
if not (out/"captions.srt").exists():
    raise SystemExit("FAIL: captions.srt missing")
manifest=out/"asset_manifest.json"
if manifest.exists():
    assets=json.loads(manifest.read_text(encoding="utf-8"))
    print("Licensed video assets listed:",len(assets))
else:
    print("WARNING: no asset manifest found")
print(f"PASS: {video.name}, 1080x1920, {duration:.1f}s, audio and captions present")

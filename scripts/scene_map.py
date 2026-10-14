#!/usr/bin/env python3
"""Generate candidate visual edit boundaries; candidates require human/LLM review."""
from __future__ import annotations
import argparse, json, re, shutil, subprocess
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('input',type=Path); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--threshold',type=float,default=.35); a=ap.parse_args()
    src=a.input.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    if not src.is_file(): ap.error(f'not a file: {src}')
    if not shutil.which('ffmpeg'): ap.error('ffmpeg is required')
    vf=f"select='gt(scene,{a.threshold})',showinfo"
    p=subprocess.run(['ffmpeg','-hide_banner','-i',str(src),'-vf',vf,'-an','-f','null','-'],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    times=[]
    for line in p.stderr.splitlines():
        m=re.search(r'pts_time:([0-9.]+)',line)
        if m: times.append(float(m.group(1)))
    result={'schema':'video-origin-forensics/scene-map','threshold':a.threshold,'candidate_cut_times_seconds':times,'limitations':['Scene detection can miss soft cuts, rapid motion, flashes, caption changes, and audio-only edits.','Every candidate must be reviewed against frames and audio.']}
    (out/'scene-map.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()

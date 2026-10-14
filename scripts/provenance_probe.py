#!/usr/bin/env python3
"""Probe an authorized media file for provenance and encoder clues without altering it."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('input',type=Path); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    src=a.input.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    if not src.is_file(): ap.error(f'not a file: {src}')
    h=hashlib.sha256(src.read_bytes()).hexdigest()
    probes={}
    if shutil.which('ffprobe'):
        p=run(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-show_programs','-of','json',str(src)])
        probes['ffprobe']={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    for tool in ('exiftool','mediainfo'):
        if shutil.which(tool):
            cmd=[tool,'-j',str(src)] if tool=='exiftool' else [tool,'--Output=JSON',str(src)]
            p=run(cmd); probes[tool]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    raw=src.read_bytes()
    needles=(b'c2pa',b'jumbf',b'contentcredentials',b'xmp',b'encoder',b'lavf',b'premiere',b'after effects',b'avid',b'davinci',b'capcut',b'final cut',b'canva',b'handbrake',b'ffmpeg')
    hits=[]
    lower=raw.lower()
    for n in needles:
        pos=0
        while True:
            pos=lower.find(n,pos)
            if pos<0: break
            hits.append({'needle':n.decode(errors='replace'),'offset':pos,'context':raw[max(0,pos-80):pos+len(n)+80].decode('utf-8','replace')}); pos+=len(n)
    result={'schema':'video-origin-forensics/provenance','file':str(src),'sha256':h,'bytes':len(raw),'tool_probes':probes,'byte_signatures':hits,'interpretation_rules':['A hit is a clue, not proof of the editing application.','C2PA presence must be cryptographically validated; string presence alone is insufficient.','Platform transcodes can replace original metadata.']}
    (out/'provenance-probe.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(out/'provenance-probe.json'),'sha256':h,'signature_hits':len(hits),'probes':list(probes)},indent=2))
if __name__=='__main__': main()

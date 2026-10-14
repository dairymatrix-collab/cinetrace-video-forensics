#!/usr/bin/env python3
"""Run CineTrace's deterministic local probes and write one run manifest."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(1024*1024): h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path); ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--frame-interval',type=float,default=5.0)
    ap.add_argument('--scene-threshold',type=float,default=.35)
    a=ap.parse_args(); src=a.input.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    if not src.is_file(): ap.error(f'input is not a file: {src}')
    here=Path(__file__).resolve().parent
    jobs=[('video', [here/'video_forensics.py',src,'--out',out/'video','--interval',str(a.frame_interval)]),
          ('provenance',[here/'provenance_probe.py',src,'--out',out/'provenance']),
          ('audio',[here/'audio_forensics.py',src,'--out',out/'audio']),
          ('scene-map',[here/'scene_map.py',src,'--out',out/'scene-map','--threshold',str(a.scene_threshold)])]
    results=[]
    for name,cmd in jobs:
        p=subprocess.run([sys.executable,*map(str,cmd)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
        (out/f'{name}.stdout.log').write_text(p.stdout,encoding='utf-8')
        (out/f'{name}.stderr.log').write_text(p.stderr,encoding='utf-8')
        results.append({'name':name,'returncode':p.returncode,'stdout_log':f'{name}.stdout.log','stderr_log':f'{name}.stderr.log'})
    run={'schema':'cinetrace/run','started_epoch':time.time(),'input':str(src),'sha256':sha256(src),'bytes':src.stat().st_size,'parameters':{'frame_interval':a.frame_interval,'scene_threshold':a.scene_threshold},'tools':{x:shutil.which(x) for x in ('ffmpeg','ffprobe','exiftool','mediainfo')},'jobs':results,'next_step':'Review probe JSON and run multimodal analysis; candidate measurements are not final conclusions.'}
    (out/'run-manifest.json').write_text(json.dumps(run,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(out),'jobs':results,'sha256':run['sha256']},indent=2))
    return 0 if all(x['returncode']==0 for x in results) else 2
if __name__=='__main__': raise SystemExit(main())

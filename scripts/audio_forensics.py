#!/usr/bin/env python3
"""Extract reproducible audio measurements for an authorized video."""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path

def run(cmd): return subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('input',type=Path); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    src=a.input.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    if not src.is_file(): ap.error(f'not a file: {src}')
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'): ap.error('ffmpeg and ffprobe are required')
    probe=run(['ffprobe','-v','error','-select_streams','a:0','-show_streams','-of','json',str(src)])
    (out/'audio-stream.json').write_text(probe.stdout+'\n',encoding='utf-8')
    if not json.loads(probe.stdout).get('streams'):
        (out/'audio-measurements.json').write_text(json.dumps({'has_audio':False},indent=2)+'\n'); print('no audio stream'); return
    commands={
      'loudness':['ffmpeg','-hide_banner','-i',str(src),'-map','0:a:0','-af','ebur128=framelog=verbose','-f','null','-'],
      'silence':['ffmpeg','-hide_banner','-i',str(src),'-map','0:a:0','-af','silencedetect=noise=-35dB:d=0.25','-f','null','-'],
      'stats':['ffmpeg','-hide_banner','-i',str(src),'-map','0:a:0','-af','astats=metadata=1:reset=1','-f','null','-']}
    logs={}
    for name,cmd in commands.items():
        p=run(cmd); logs[name]={'returncode':p.returncode,'stderr':p.stderr,'stdout':p.stdout}
    (out/'audio-measurements.json').write_text(json.dumps({'has_audio':True,'logs':logs},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(out),'has_audio':True,'measurements':['loudness','silence','stats']},indent=2))
if __name__=='__main__': main()

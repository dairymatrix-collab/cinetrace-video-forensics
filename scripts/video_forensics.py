#!/usr/bin/env python3
"""Create a deterministic local evidence bundle for an authorized video."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path

def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        while chunk := f.read(1024 * 1024): h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--interval', type=float, default=5.0, help='seconds between representative frames')
    args = ap.parse_args()
    src = args.input.resolve()
    if not src.is_file(): ap.error(f'input is not a file: {src}')
    if shutil.which('ffprobe') is None: ap.error('ffprobe is required')
    if shutil.which('ffmpeg') is None: ap.error('ffmpeg is required for frame extraction')
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    frames = out / 'frames'; frames.mkdir(exist_ok=True)
    probe = run(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(src)])
    if probe.returncode: print(probe.stderr, file=sys.stderr); return probe.returncode
    (out/'ffprobe.json').write_text(probe.stdout + '\n', encoding='utf-8')
    meta = json.loads(probe.stdout)
    duration = float(meta.get('format', {}).get('duration') or 0)
    interval = max(0.5, args.interval)
    frame_result = run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(src),'-vf',f"fps=1/{interval}",'-frames:v','200',str(frames/'frame_%04d.jpg')])
    if frame_result.returncode: print(frame_result.stderr, file=sys.stderr); return frame_result.returncode
    manifest = {
        'schema':'video-origin-forensics', 'input':str(src), 'sha256':sha256(src),
        'bytes':src.stat().st_size, 'duration_seconds':duration, 'sample_interval_seconds':interval,
        'ffprobe':'ffprobe.json', 'frames_directory':'frames',
        'streams':meta.get('streams', []), 'format':meta.get('format', {}),
        'notes':['Frame samples are evidence aids, not a complete frame-by-frame inspection.', 'Platform transcodes may have replaced original encoder metadata.']
    }
    (out/'evidence-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps({'out':str(out), 'duration_seconds':duration, 'sha256':manifest['sha256'], 'frames':len(list(frames.glob('*.jpg')))}, indent=2))
    return 0
if __name__ == '__main__': raise SystemExit(main())

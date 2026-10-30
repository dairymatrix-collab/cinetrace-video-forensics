#!/usr/bin/env python3
"""Probe an authorized media file for provenance and encoder clues without altering it."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


NEEDLES = (
    b"c2pa", b"jumbf", b"contentcredentials", b"xmp", b"encoder", b"lavf",
    b"premiere", b"after effects", b"avid", b"davinci", b"capcut",
    b"final cut", b"canva", b"handbrake", b"ffmpeg",
)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Hash a media file without loading it all into memory."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def scan_byte_signatures(
    path: Path,
    needles: tuple[bytes, ...] = NEEDLES,
    chunk_size: int = 1024 * 1024,
    context_bytes: int = 80,
) -> list[dict[str, object]]:
    """Find case-insensitive byte signatures with bounded read buffers.

    At most ``chunk_size`` new bytes plus the longest-needle overlap are held
    for scanning. Context is sought and read only for each reported hit.
    Results retain the legacy ordering: configured needle order, then offset.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    if context_bytes < 0:
        raise ValueError("context_bytes cannot be negative")
    normalized = tuple(bytes(needle).lower() for needle in needles)
    if any(not needle for needle in normalized):
        raise ValueError("needles must not be empty")
    if not normalized:
        return []

    longest = max(len(needle) for needle in normalized)
    hits_by_needle: list[list[dict[str, object]]] = [[] for _ in normalized]
    next_allowed_offset = [0 for _ in normalized]
    tail = b""
    total_read = 0
    with path.open("rb") as stream, path.open("rb") as context_stream:
        while True:
            chunk = stream.read(chunk_size)
            at_eof = not chunk
            data = tail + chunk
            base_offset = total_read - len(tail)
            total_read += len(chunk)
            scan_limit = len(data) if at_eof else max(0, len(data) - longest + 1)
            lowered = data.lower()

            for index, needle in enumerate(normalized):
                position = 0
                while True:
                    position = lowered.find(needle, position)
                    if position < 0 or position >= scan_limit:
                        break
                    absolute = base_offset + position
                    if absolute < next_allowed_offset[index]:
                        position += 1
                        continue
                    context_start = max(0, absolute - context_bytes)
                    context_stream.seek(context_start)
                    context = context_stream.read(context_bytes * 2 + len(needle))
                    hits_by_needle[index].append({
                        "needle": needle.decode(errors="replace"),
                        "offset": absolute,
                        "context": context.decode("utf-8", "replace"),
                    })
                    next_allowed_offset[index] = absolute + len(needle)
                    position += len(needle)

            if at_eof:
                break
            tail = data[scan_limit:]

    return [hit for group in hits_by_needle for hit in group]


def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('input',type=Path); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    src=a.input.resolve(); out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    if not src.is_file(): ap.error(f'not a file: {src}')
    h=sha256_file(src)
    probes={}
    if shutil.which('ffprobe'):
        p=run(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-show_programs','-of','json',str(src)])
        probes['ffprobe']={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    for tool in ('exiftool','mediainfo'):
        if shutil.which(tool):
            cmd=[tool,'-j',str(src)] if tool=='exiftool' else [tool,'--Output=JSON',str(src)]
            p=run(cmd); probes[tool]={'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    size=src.stat().st_size
    hits=scan_byte_signatures(src)
    result={'schema':'video-origin-forensics/provenance','file':str(src),'sha256':h,'bytes':size,'tool_probes':probes,'byte_signatures':hits,'interpretation_rules':['A hit is a clue, not proof of the editing application.','C2PA presence must be cryptographically validated; string presence alone is insufficient.','Platform transcodes can replace original metadata.']}
    (out/'provenance-probe.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(out/'provenance-probe.json'),'sha256':h,'signature_hits':len(hits),'probes':list(probes)},indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
"""Generate candidate visual edit boundaries; candidates require human/LLM review."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--threshold", type=float, default=0.35)
    args = ap.parse_args()

    src = args.input.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not src.is_file():
        ap.error("input is not a file")
    if not shutil.which("ffmpeg"):
        ap.error("ffmpeg is required")

    vf = f"select='gt(scene,{args.threshold})',showinfo"
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(src), "-vf", vf, "-an", "-f", "null", "-"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    common = {
        "schema": "video-origin-forensics/scene-map",
        "threshold": args.threshold,
        "limitations": [
            "Scene detection can miss soft cuts, rapid motion, flashes, caption changes, and audio-only edits.",
            "Every candidate must be reviewed against frames and audio.",
        ],
    }
    if result.returncode != 0:
        payload = {
            **common,
            "status": "failed",
            "error_code": "FFMPEG_SCENE_MAP_FAILED",
            "returncode": result.returncode,
            "candidate_cut_times_seconds": [],
        }
        _write_json(out / "scene-map.json", payload)
        print(json.dumps({"status": "failed", "error_code": payload["error_code"], "returncode": result.returncode}))
        return 2

    times = []
    for line in result.stderr.splitlines():
        match = re.search(r"pts_time:([0-9.]+)", line)
        if match:
            times.append(float(match.group(1)))
    payload = {**common, "status": "complete", "candidate_cut_times_seconds": times}
    _write_json(out / "scene-map.json", payload)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

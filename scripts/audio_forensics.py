#!/usr/bin/env python3
"""Extract reproducible audio measurements for an authorized video."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    src = args.input.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if not src.is_file():
        ap.error("input is not a file")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        ap.error("ffmpeg and ffprobe are required")

    probe = run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_streams", "-of", "json", str(src)])
    (out / "audio-stream.json").write_text(probe.stdout + "\n", encoding="utf-8")
    try:
        probe_data = json.loads(probe.stdout)
    except (json.JSONDecodeError, TypeError):
        probe_data = None

    if probe.returncode != 0 or not isinstance(probe_data, dict) or not isinstance(probe_data.get("streams"), list):
        code = "FFPROBE_FAILED" if probe.returncode != 0 else "FFPROBE_OUTPUT_INVALID"
        _write_json(out / "audio-measurements.json", {
            "has_audio": None,
            "status": "failed",
            "error_code": code,
            "returncode": probe.returncode,
        })
        print(json.dumps({"status": "failed", "error_code": code, "returncode": probe.returncode}))
        return 2

    if not probe_data["streams"]:
        _write_json(out / "audio-measurements.json", {"has_audio": False, "status": "complete"})
        print(json.dumps({"status": "complete", "has_audio": False}))
        return 0

    commands = {
        "loudness": ["ffmpeg", "-hide_banner", "-i", str(src), "-map", "0:a:0", "-af", "ebur128=framelog=verbose", "-f", "null", "-"],
        "silence": ["ffmpeg", "-hide_banner", "-i", str(src), "-map", "0:a:0", "-af", "silencedetect=noise=-35dB:d=0.25", "-f", "null", "-"],
        "stats": ["ffmpeg", "-hide_banner", "-i", str(src), "-map", "0:a:0", "-af", "astats=metadata=1:reset=1", "-f", "null", "-"],
    }
    logs: dict[str, dict[str, Any]] = {}
    failed = []
    for name, command in commands.items():
        result = run(command)
        logs[name] = {"returncode": result.returncode, "stderr": result.stderr, "stdout": result.stdout}
        if result.returncode != 0:
            failed.append(name)

    status = "partial" if failed and len(failed) < len(commands) else "failed" if failed else "complete"
    payload = {"has_audio": True, "status": status, "logs": logs}
    if failed:
        payload["error_code"] = "FFMPEG_MEASUREMENTS_FAILED"
        payload["failed_measurements"] = failed
    _write_json(out / "audio-measurements.json", payload)
    print(json.dumps({"status": status, "has_audio": True, "failed_measurements": failed}))
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

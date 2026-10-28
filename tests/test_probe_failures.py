from __future__ import annotations

from contextlib import redirect_stdout
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from io import StringIO

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audio_forensics  # noqa: E402
import run_cinetrace  # noqa: E402
import scene_map  # noqa: E402


def completed(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


class AudioProbeTests(unittest.TestCase):
    def invoke(self, results: list[subprocess.CompletedProcess[str]]):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        source = root / "synthetic authorized video.mp4"
        source.write_bytes(b"synthetic fixture; subprocess is mocked")
        out = root / "audio evidence"
        with patch.object(audio_forensics.shutil, "which", return_value="/mock/ffmpeg"), \
             patch.object(audio_forensics, "run", side_effect=results), \
             patch.object(sys, "argv", ["audio_forensics.py", str(source), "--out", str(out)]), \
             redirect_stdout(StringIO()):
            code = audio_forensics.main()
        report = json.loads((out / "audio-measurements.json").read_text(encoding="utf-8"))
        return temporary, code, report

    def test_no_audio_is_a_successful_explicit_result(self):
        temporary, code, report = self.invoke([completed(0, '{"streams":[]}')])
        try:
            self.assertEqual(code, 0)
            self.assertEqual(report, {"has_audio": False, "status": "complete"})
        finally:
            temporary.cleanup()

    def test_failed_ffprobe_is_not_reported_as_no_audio(self):
        temporary, code, report = self.invoke([completed(1, '{"streams":[]}', "probe failed")])
        try:
            self.assertEqual(code, 2)
            self.assertIsNone(report["has_audio"])
            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["error_code"], "FFPROBE_FAILED")
        finally:
            temporary.cleanup()

    def test_invalid_ffprobe_json_fails_closed(self):
        temporary, code, report = self.invoke([completed(0, "not-json")])
        try:
            self.assertEqual(code, 2)
            self.assertEqual(report["error_code"], "FFPROBE_OUTPUT_INVALID")
            self.assertIsNone(report["has_audio"])
        finally:
            temporary.cleanup()

    def test_any_failed_measurement_propagates_failure_and_partial_status(self):
        temporary, code, report = self.invoke([
            completed(0, '{"streams":[{"codec_type":"audio"}]}'),
            completed(1, stderr="loudness failed"),
            completed(0),
            completed(0),
        ])
        try:
            self.assertEqual(code, 2)
            self.assertEqual(report["status"], "partial")
            self.assertEqual(report["failed_measurements"], ["loudness"])
            self.assertEqual(report["logs"]["loudness"]["returncode"], 1)
        finally:
            temporary.cleanup()

    def test_all_measurements_succeed(self):
        temporary, code, report = self.invoke([
            completed(0, '{"streams":[{"codec_type":"audio"}]}'),
            completed(0), completed(0), completed(0),
        ])
        try:
            self.assertEqual(code, 0)
            self.assertEqual(report["status"], "complete")
        finally:
            temporary.cleanup()


class SceneMapTests(unittest.TestCase):
    def invoke(self, result: subprocess.CompletedProcess[str]):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        source = root / "synthetic authorized video.mp4"
        source.write_bytes(b"synthetic fixture; subprocess is mocked")
        out = root / "scene evidence"
        with patch.object(scene_map.shutil, "which", return_value="/mock/ffmpeg"), \
             patch.object(scene_map.subprocess, "run", return_value=result), \
             patch.object(sys, "argv", ["scene_map.py", str(source), "--out", str(out)]), \
             redirect_stdout(StringIO()):
            code = scene_map.main()
        report = json.loads((out / "scene-map.json").read_text(encoding="utf-8"))
        return temporary, code, report

    def test_failed_ffmpeg_with_empty_stderr_is_not_successful_empty_scene_map(self):
        temporary, code, report = self.invoke(completed(1, stderr=""))
        try:
            self.assertEqual(code, 2)
            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["error_code"], "FFMPEG_SCENE_MAP_FAILED")
            self.assertEqual(report["candidate_cut_times_seconds"], [])
        finally:
            temporary.cleanup()

    def test_success_with_no_candidates_is_complete(self):
        temporary, code, report = self.invoke(completed(0, stderr=""))
        try:
            self.assertEqual(code, 0)
            self.assertEqual(report["status"], "complete")
            self.assertEqual(report["candidate_cut_times_seconds"], [])
        finally:
            temporary.cleanup()

    def test_success_parses_candidate_times(self):
        temporary, code, report = self.invoke(completed(0, stderr="[Parsed_showinfo] pts_time:12.5\n"))
        try:
            self.assertEqual(code, 0)
            self.assertEqual(report["candidate_cut_times_seconds"], [12.5])
        finally:
            temporary.cleanup()


class RunnerPropagationTests(unittest.TestCase):
    def test_child_nonzero_exit_is_recorded_and_propagated(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        source = root / "synthetic authorized video.mp4"
        source.write_bytes(b"synthetic fixture; subprocess is mocked")
        out = root / "runner evidence"
        results = [completed(0, "video ok"), completed(0, "probe ok"), completed(2, "audio failed"), completed(0, "scene ok")]
        with patch.object(run_cinetrace.shutil, "which", return_value="/mock/tool"), \
             patch.object(run_cinetrace.subprocess, "run", side_effect=results), \
             patch.object(sys, "argv", ["run_cinetrace.py", str(source), "--out", str(out)]), \
             redirect_stdout(StringIO()):
            code = run_cinetrace.main()
        try:
            manifest = json.loads((out / "run-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(code, 2)
            self.assertEqual([job["returncode"] for job in manifest["jobs"]], [0, 0, 2, 0])
        finally:
            temporary.cleanup()


if __name__ == "__main__":
    unittest.main()

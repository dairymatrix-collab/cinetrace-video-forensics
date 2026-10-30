# CineTrace Video Forensics

> Evidence-first forensic reconstruction of how YouTube and social-media videos were made.

**Maintainer:** Arifmughal

CineTrace helps analyze authorized YouTube, TikTok, Instagram, Facebook, X, and local videos as production artifacts. Its CLI creates deterministic probe artifacts, logs, and a run manifest; it does **not** compose the completed timestamped forensic report. That report requires reviewing the evidence with the Skill workflow and filling the report template.

## Why CineTrace is different

It does not turn visual style into fake certainty. Exact editing software, AI model, private prompt, source clip, plugin settings, or creation time is marked **not determinable** unless direct evidence exists. Every finding carries an Evidence ID, timestamp or file path, status, confidence, limitation, and alternative explanation where needed.

## Core capabilities

- SHA-256-preserved source and reproducible probe manifest
- FFprobe stream and container metadata in JSON
- encoder, XMP, MP4 UUID/JUMBF/C2PA clue inspection
- loudness, silence, dynamics, and audio-stream measurements
- candidate scene-cut and edit-boundary mapping
- timestamped shot, caption, overlay, transition, tracking, masking, and compositing analysis
- stage-by-stage tool-family ranking with confidence and alternatives
- public platform metadata separated from file provenance
- Markdown report template and evidence schema for the agent/human review workflow
- clean-room recreation workflow using user-owned assets

## Quick start

Requirements for local media probes: Python 3.8 or newer plus `ffmpeg` and `ffprobe` on `PATH`. Install FFmpeg from the [official FFmpeg download page](https://ffmpeg.org/download.html) or a trusted OS distributor, then confirm both commands with `ffmpeg -version` and `ffprobe -version`. The source minimum is based on syntax; no minimum FFmpeg version is asserted. The audited public tree has no GitHub Actions CI workflow; test commands are local contributor checks. This run's local tests executed on Linux x86_64/Python 3.12.3; other operating systems and Python runtimes are unverified. There is no pip package or installation manifest; run from a repository checkout.

```bash
python3 scripts/run_cinetrace.py /absolute/path/video.mp4 --out ./cinetrace-evidence
```

Load `SKILL.md` into an AI agent. Use `SKILL-ROMAN-URDU.md` for the complete Roman Urdu translation and `templates/video-origin-report.md` for the final report. Run output is probe evidence, not a finished forensic report.

## Local tests

Run the standard-library unit suite and compile checks with `python3 -m unittest discover -s tests -v` and `python3 -m compileall -q scripts tests`. The unit tests mock FFmpeg subprocesses and do not need media files or FFmpeg execution. A real end-to-end media probe is a separate integration check: use only an authorized synthetic or user-owned video.

## Search keywords

video forensics, video origin analysis, how was this video made, social media video metadata, identify video editing software, identify AI video tool, C2PA video provenance, YouTube production analysis, shot-by-shot video analysis, audio-video forensic analysis, encoder fingerprint, FFmpeg FFprobe media evidence, AI agent video analysis skill.

## Responsible use

Analyze only media you are authorized to inspect. Do not bypass private access, DRM, platform restrictions, watermark/provenance protections, or licensing controls. Do not clone a real person's voice or likeness without permission.

## References

The reverse-engineering integration is designed to work with [REA](https://github.com/morluto/rea). Provenance references cover [C2PA](https://spec.c2pa.org/specifications/specifications/2.4/explainer/Explainer.html), [FFprobe](https://ffmpeg.org/ffprobe.html), and [YouTube video metadata](https://developers.google.com/youtube/v3/docs/videos).

## License

MIT. Third-party tools, platform terms, and target-media rights remain separate.

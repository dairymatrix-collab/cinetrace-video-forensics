# Contributing to CineTrace Video Forensics

Contributions should improve evidence quality, deterministic media probes, portability, report clarity, safety, or AI-agent integration. Keep direct evidence separate from inference and add tests for code changes.

Do not add instructions for private-access bypass, DRM circumvention, watermark/provenance removal, credential theft, malware deployment, unauthorized voice/likeness cloning, or copying protected source media.

Before proposing a change, run the standard-library unit suite and compile check:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
```

If a local Skill Creator installation is available, run its validator with `python3 "<skill-creator-dir>/scripts/quick_validate.py" .` (Windows: `py "<skill-creator-dir>\scripts\quick_validate.py" .`); the validator is not bundled here. A real media integration smoke is separate from the mocked unit tests and must use only a synthetic or user-owned authorized video. Do not download platform media for tests. Do not commit private videos, credentials, or transcripts containing personal data.

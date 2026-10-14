# CineTrace Video Forensics — Agent Integration

## English

Load `SKILL.md` as the operational skill. Load `SKILL-ROMAN-URDU.md` when the user wants explanations in Roman Urdu/Hindi. Use `references/` for attribution limits and multimodal prompts, `templates/video-origin-report.md` for the report, and `scripts/run_cinetrace.py` for the deterministic local pass.

```bash
python3 scripts/run_cinetrace.py /absolute/path/video.mp4 --out ./cinetrace-evidence
```

Then analyze the original video and evidence folder with timestamped observations. Do not confuse candidate detections with conclusions.

## Roman Urdu

`SKILL.md` agent ka main operational file hai. Agar user Roman Urdu/Hindi mein report chahe to `SKILL-ROMAN-URDU.md` bhi load karein. Local file par yeh command chalayein:

```bash
python3 scripts/run_cinetrace.py /absolute/path/video.mp4 --out ./cinetrace-evidence
```

Report mein har claim ka timestamp, Evidence ID, confidence aur limitation likhein. Exact app ya exact AI model sirf direct saboot par report karein.

## Minimal prompt

Use CineTrace Video Forensics. Analyze this authorized video deeply. Run the deterministic probes, inspect provenance and platform context, create a timestamped shot/edit/audio map, rank tools by production stage, and produce the report template plus evidence JSON. Separate observed, inferred, and unknown facts. Never invent the private prompt, exact AI model, editor, or creation time.

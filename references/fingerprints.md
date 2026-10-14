# Production fingerprint reference

## Evidence tiers

| Tier | Examples | Identification strength |
|---|---|---|
| A: direct | project file, EDL/XML, creator statement, visible editor UI, export log | Can confirm a specific tool/version when unambiguous |
| B: technical | encoder tag, muxer/library tag, codec/profile, timebase, edit-list structure, audio encoder | Supports an export/capture family; rarely proves the editor |
| C: observable | caption geometry, transition behavior, keyframe cadence, UI capture, AI artifacts, audio processing | Supports a workflow hypothesis; cannot prove a vendor/model alone |
| D: style-only | font choice, color grade, pacing, generic zooms, viral format | Not sufficient for tool identification |

## Stage-specific hypotheses

| Stage | Look for | Safe conclusion |
|---|---|---|
| Capture/generation | screen-recording dimensions, cursor/UI, camera motion, synthetic texture, lip-sync mismatch, frame interpolation | classify source as camera, screen capture, animation, generated, or unknown; avoid naming a model without direct evidence |
| Editing | hard-cut cadence, J/L cuts, speed ramps, reframes, multicam changes, repeated templates | describe edit grammar and likely NLE class; do not equate it with Premiere/CapCut/Resolve |
| Motion graphics | layer-like reveals, masks, tracked labels, keyframed scale/position, particle/shape animation | identify compositing operations and likely motion-graphics class |
| Captions | word-level timing, karaoke fill, safe-area geometry, outline/shadow, emoji/sticker behavior | describe caption pipeline; app attribution is only possible with watermark/UI/metadata |
| Audio | LUFS-like leveling, ducking, denoise, compression, room tone, music stems, SFX sync | describe mix chain and likely processing stages, not a specific plugin unless disclosed |
| Publishing | platform transcode, thumbnail, title/description/hashtags, declared AI label | identify distribution context, not production software |

## Common false positives

- H.264/AAC metadata often comes from the platform transcode, not the creator's editor.
- A popular font, caption style, or transition belongs to many applications.
- AI-looking motion can be hand-animated, interpolated, filtered, or platform-compressed.
- Watermarks can be cropped, overlaid later, or copied; verify timing and consistency.
- A creator's tutorial or description may mention one tool while the final video uses several.
- Absence of a tag is not evidence that a tool was not used.

## Tool attribution language

Use: “compatible with,” “consistent with,” “strongly supports,” or “directly evidenced by.” Avoid: “definitely made in,” “must be,” or “the exact AI model is.” Include at least one alternative explanation whenever confidence is below confirmed.

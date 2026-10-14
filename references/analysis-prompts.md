# Analysis prompts

## Full-video forensic prompt

Analyze this video as a production artifact. Do not guess an exact app or AI model from style alone. Return timestamped evidence with confidence. Extract: (A) source/capture class, (B) shot boundaries and in/out times, (C) camera and motion, (D) cuts/transitions/speed changes, (E) captions/typography/overlays, (F) masking/tracking/compositing, (G) visible UI/watermarks/logos, (H) audio layers, speech/music/SFX/ducking, (I) generation or synthesis indicators, (J) contradictions and alternative explanations. For each claim include what is visible/audible, exact timestamp, evidence strength, and what remains unknown. Never claim a specific vendor or model unless the video directly shows or states it.

## Tool attribution prompt

For each production stage—capture/generation, editing, motion graphics, captions, audio, publishing—rank up to three plausible tool families. For each candidate list supporting observations, conflicting observations, direct evidence if any, and confidence from confirmed/strongly_supported/probable/possible/not_determinable. Explain why a visually similar alternative remains possible.

## Shot-map prompt

Create a table with segment number, start, end, duration, shot purpose, framing, camera movement, subject movement, background, transition, text/graphics, audio events, and evidence IDs. Split at every meaningful visual or audio edit. Mark uncertain boundaries as approximate.

## Recreation prompt

Using only the observed behavior and general techniques, write a clean-room recreation recipe for an original video: script/beat sheet, asset list, capture or generation options, edit timeline, graphics/caption recipe, audio mix, export settings, QA checklist, and platform adaptation. Do not copy protected footage, voices, faces, logos, scripts, or exact templates.

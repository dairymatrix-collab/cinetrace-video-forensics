# Provenance and exactness reference

## C2PA / Content Credentials

C2PA Content Credentials can carry signed provenance assertions about origin and edits. A valid manifest can prove that a credential is well-formed, bound to an asset, and tamper-evident; it does not by itself prove that the asserted story is truthful or complete. Check the manifest and signature with a validator. A string such as `c2pa` or `jumbf` in a file is only a clue.

Source: https://spec.c2pa.org/specifications/specifications/2.4/explainer/Explainer.html

## Container metadata

Use `ffprobe` in machine-readable JSON mode to inspect container and stream metadata, tags, timebase, duration, frame rate, codecs, chapters, timecode and format fields. Metadata may be stripped or rewritten by social platforms and therefore describes the analyzed file, not necessarily the original project.

Source: https://ffmpeg.org/ffprobe.html

## Public platform metadata

For YouTube, record public title, description, channel, public/published date, thumbnails, tags when available, category, duration, captions availability and live status. YouTube's `publishedAt` can differ from the original upload time when a private upload later becomes public. Do not report it as the file creation time.

Source: https://developers.google.com/youtube/v3/docs/videos

## What cannot be recovered from a final render alone

Usually not determinable without project/source evidence: the exact editor version, exact AI model, private prompt, original clip source, precise edit time, layer order, deleted takes, plugin settings, and the identity of every contributor. Report these as unknown unless direct evidence exists.

# Extracted pattern PNGs

2bpp art rendered from authentic TERSE `PATTERN` / `~` `^` sources (and GORF4A frames). Used by the pattern lab and as human-readable checks against `XC.PATTERNS` decode.

**Palette (lab hypothesis):** digit `0`=black, `1`=yellow, `2`=blue, `3`=red — same for every pattern.

Regenerate:

```bash
python3 tools/export_play_assets.py   # named {file}__{pattern}.png + play assets
python3 tools/extract_patterns.py     # gorf4a_*.png strip/frames
```

Metadata: `from_floppy_files.json`, `gorf4a_meta.json`.

Browse in-repo: open [`../../play/index.html`](../../play/index.html) after export.

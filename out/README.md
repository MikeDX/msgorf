# `out/` — build products

| Artifact | Meaning |
|----------|---------|
| `mvp_object.msgx` | Host MVP compile of demo colon defs (`tools/terse/mvp_compile.py`) |
| `mvp_compile_report.json` | Metadata for the last MVP compile |
| `pattern_object_manifest.json` | What a real `XCFSYSAVE FS.PAT` would be aiming at (from disk 0086) |
| `ROM_STATUS.md` | Why a full Ms. Gorf ROM is not here yet |

Do not treat `mvp_object.msgx` as an arcade ROM.

| `msgorf_patterns_at_4000.bin` | **Authentic** XC.PATTERNS placed at 0x4000 in a 64K image |
| `MSGORPAT_XC_PATTERNS` etc. | Raw object copies from Tim’s extract |
| `fload_chain.json` | Resolved XCLOAD dependency order |
| `bullets_fragment.msgx` | Host-MVP encoding of historical BULLETS fragment (stub opcodes) |

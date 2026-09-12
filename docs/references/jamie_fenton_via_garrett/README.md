# Jamie Fenton TERSE / IceBox manuals (via Matthew Garrett)

Source page: [professionalmagic.com/gorf](https://www.professionalmagic.com/gorf)  
Jamie sent these to Matthew; hosted as `/s/*.pdf` (Canon scanner / My Image Garden).  
Downloaded into this folder 2026-09-12. See `SHA256SUMS.txt`.

## Files (site link text → actual content)

| Site label | Filename | Pages | What it actually is |
|------------|----------|------:|---------------------|
| TERSE VOCAB PDF | `TERSE_VOCAB.pdf` | 24 | **TERSE Standard Glossary** (9/21/81) |
| TERSE MISC 6 PDF | `MISC6.pdf` | 14 | **ICE Monitor Commands** (+ key map) — *not* a “misc TERSE vocab” title on the cover |
| ICE5 PDF | `ICE5.pdf` | 10 | **DNA ICE hardware description** |
| GAS MONITOR PDF | `GAS_MONITOR4.pdf` | 6 | **GAS Monitor** v2.33 (9/21/81) |
| EDIT VOCAB PDF | `EDIT_VOCAB2.pdf` | 9 | **EDIT 81 Glossary** (9/21/81) |
| ASSEMBLER PDF | `ASSEMBLER3.pdf` | 9 | **Mislabelled:** same *EDIT 81 Glossary* family as `EDIT_VOCAB2` (not Z80 assembler opcodes) |

OCR text extract: `MISC6.txt` (noisy scan OCR).

## Relation to Bitsavers copies already in-repo

Same *editions* (matching page counts) exist under `docs/references/icebox/` from Bitsavers, but **different scans** (file sizes / SHA256 differ). Prefer either set for reading; cite SHA when quoting.

| This folder | Bitsavers twin (different scan) |
|-------------|-----------------------------------|
| `TERSE_VOCAB.pdf` | `docs/references/icebox/TERSE_VOCAB.pdf` |
| `ICE5.pdf` | `docs/references/icebox/ICE5.pdf` |
| `GAS_MONITOR4.pdf` | `docs/references/icebox/GAS_MONITOR4.pdf` |
| `EDIT_VOCAB2.pdf` | `docs/references/icebox/EDIT_VOCAB2.pdf` |
| `MISC6.pdf` | **No prior copy in this repo** (new to us) |
| `ASSEMBLER3.pdf` | Not an assembler manual — use `docs/references/terse/Z80_Asm.pdf` for opcode/asm forms |

## What these unlock for Ms. Gorf

- Dictionary / editor / monitor / ICE memory-map vocabulary for **toolchain and RE**
- Do **not** contain `XC.LOGIC` or application game screens

## Real assembler reference

Keep using `docs/references/terse/Z80_Asm.pdf` (Bitsavers / Fenton collection) until a correctly labelled assembler PDF appears.

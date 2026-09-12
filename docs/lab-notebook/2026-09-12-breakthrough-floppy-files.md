# 2026-09-12 — Breakthrough: MsGorf_floppy_files.zip

## Find

Bitsavers path (not under `/bits/`):

`https://bitsavers.org/pdf/nuttingAssoc/icebox/floppies/MsGorf_floppy_files.zip`

Tim’s Readme: extracted MSGORPAT + MSGPATLD files + listings; third floppy still needs reread; also includes Robby Roto disk extract.

## Impact

- Complete pattern FLOAD tree resolved from `XCLOAD` with no missing names.
- Authentic `XC.PATTERNS` packaged to `out/msgorf_patterns_at_4000.bin`.
- Enemy/player roster documented from `INDEX`.
- Gap clarified: need `XC.LOGIC` / app sources, not more pattern files.

## Commands run

```bash
curl … -o docs/references/bits/MsGorf_floppy_files.zip …
unzip … -d extracted/msgorf_floppy_files
python3 tools/terse/fload_chain.py XCLOAD
python3 tools/terse/package_patterns_rom.py
```

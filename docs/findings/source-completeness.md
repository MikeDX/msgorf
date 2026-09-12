# Source completeness gate

**Verdict: PARTIAL — but much stronger than the raw three-disk view.**

Updated: 2026-09-12 (after `MsGorf_floppy_files.zip`)

## Authentic assets we now have

1. Original dumps (`MSGORF/`, `MSGORPAT/`, `MSGPATLD/`) ≡ Bitsavers `MSGORF.zip`.
2. **Tim’s extract** [`MsGorf_floppy_files.zip`](https://bitsavers.org/pdf/nuttingAssoc/icebox/floppies/MsGorf_floppy_files.zip):
   - Per-file TERSE screens + `.lst` listings for MSGORPAT & MSGPATLD
   - Prebuilt binaries: `XC.PATTERNS`, `FS.PAT`, `FS.XC`
   - Complete `XCLOAD` FLOAD chain with **zero missing files** (patterns path)
3. IceBox firmware + CP/M disk (`Nutting_ICE.zip`), MAME `icebox.cpp` notes (Gorf LOAD path, Fasterse ≡ Gorf low ROM).
4. Gorf OS listing dump `docs/references/gorf/GORFOS.txt` (TERSE block dump, 14-Mar-79).

## What still blocks a full game ROM

| Missing | Why it matters |
|---------|----------------|
| Third floppy redump (GORF4A) | Tim: still needs reread; we have SCP/img but format differs |
| `XC.LOGIC` file/screens | Named in dictionary; not in Tim’s file set |
| Application LOAD disks beyond patterns | No mission/player loop sources found |
| Final dual-Z80 / collision hardware spec | Jamie: changed near cancel |

## What we can build today

- **Authentic pattern ROM fragment:** `out/msgorf_patterns_at_4000.bin` (XC.PATTERNS @ 0x4000)
- Host MVP compile of trivial / stubbed colon defs
- Full sprite sheet previews from pattern sources

## Shopping list (still)

1. Any disk/files containing `XC.LOGIC` or game LOOP/MISSION sources
2. Clean GORF4A IMD redump
3. Additional IceBox floppies from `icebox/floppies/128b/` if they hold Fasterse/XC tools
4. Local MAME Gorf ROMs for Rosetta (not redistributed here)

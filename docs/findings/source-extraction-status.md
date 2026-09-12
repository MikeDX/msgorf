# Source extraction status

## What these disks actually are

| Artifact | Content |
|----------|---------|
| MSGORF / GORF4A | Extra/large pattern (`GORF4A`) |
| MSGORPAT / MSGPATLD | TERSE **pattern toolchain** + animation tables + XC pattern object |
| Tim’s `MsGorf_floppy_files.zip` | Same, split into files + listings |

## Present in source (extractable)

- Full pattern set + `INDEX` + `ANIM-MAP` + `ANIM-VERBS` / table builders
- `PATTERN` / `QUADPAT` / `AT!` machinery
- Cross-compile driver `XCLOAD` → `CODE-LOAD` / `PAT-LOAD` → `XCFSYSAVE` → `XC.PATTERNS` / `FS.PAT`
- Tiny fragment in `FS.XC`: `: BULLETS  p-i @  -2 P-I ;  : ENDBULL  P-I ;`
- Loaders that expect a game file named **`XC.LOGIC`** (`BINLOAD` / `LLOAD`)

## Not present (so far)

- Application / mission / stick / collision **game loop** sources
- The binary `XC.LOGIC` itself
- Proven screen-mode init for Ms. Gorf specifically

Dictionary on MSGORPAT *names* `XC.LOGIC` as a cross-compile target — that file is what Jamie’s game would compile *to*, and what artists `BINLOAD`. It is not on the pattern disks.

## Extraction next steps

1. **Acquire missing media** — see `docs/findings/missing-files-hunt.md` (museum catalog, 8″ “RIP Ms. GORF” set, Garrett/Tim/Frank). Not findable inside current zips.
2. Continue CFA/dictionary RE on MSGORPAT kernel + `FS.XC` (Python TERSE tools)
3. Use Gorf `GORFOS.txt` + Roto sources as Rosetta for VGER verbs only — do not paste into Ms. Gorf as if authentic
4. Decode remaining XC animation tables so ROM fragment is fully interpretable

## Honesty bar

Until game screens / `XC.LOGIC` exist, **do not** ship a “Ms. Gorf game” UI that pretends to be the arcade logic. Pattern lab + toolchain only.

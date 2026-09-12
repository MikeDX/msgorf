# TERSE dictionary model (MSGORPAT)

## Method

Walked length-prefixed name fields in `work/MSGORPAT.img.corrected` (heuristic). Results in `extracted/dictionary/msgorpat_name_fields.txt` (**808** unique names).

Early kernel matches classic Forth/TERSE: `.NEXT.`, `LIT`, `BLIT`, `DUP`, `DROP`, `SWAP`, `LOAD`, `FLOAD`, `TERSE`, …

## Cross-compile vocabulary (offsets)

| Offset | Name |
|-------:|------|
| 00E802 | ROMSTART |
| 00E85C | xcsys |
| 00E9DA | XCFSYSAVE |
| 00EAC8 | BYTE-TERSE |
| 00EB58 | xc |
| 00EF8D | XCBEG |
| 0153CF | XCTERSE |
| 0153DB | ARC-TERSE |
| 0153E9 | ARCLOAD |
| 0153F5 | XCLOAD |
| 015C0D | XC.LOGIC |
| 015C2E | BINLOAD |
| 02640D | XC.PATTERNS |

`XC.LOGIC` is named in the dictionary — **no corresponding extracted file** in Tim’s MSGORPAT/MSGPATLD file set. That is the likely home of game logic still missing from these floppies.

## Linking model (working guess)

1. Text screens (`FLOAD` chains) compile into the host TERSE dictionary on IceBox.
2. `XCBEG` … `XCFSYSAVE` retarget DP/ROMSTART and emit an object file (`XC.PATTERNS` / `FS.PAT`).
3. Arcade runtime uses a stripped **Fasterse**/ARC-TERSE kernel (see MAME `icebox.cpp` notes + Gorf low ROM) plus the object.

Code field / threading details still need CFA-level RE against `Z80_Asm.pdf` and Gorf ROM; name-field scrape alone is not enough to emit authentic threaded code.

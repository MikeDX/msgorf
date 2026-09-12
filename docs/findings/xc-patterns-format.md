# XC.PATTERNS layout (working)

File: Tim extract `MSGORPAT_Disk/XC.PATTERNS` (20480 bytes), placed at `ROMSTART 0x4000` by XCLOAD.

## Observations

- Little-endian u16 words at start look like **pointers** into `0x4200–0x8900` and `0x8040` (DP / ATBL region from XCLOAD screen).
- XCLOAD sets `4000 C= ATBL` and `04200 PT-HERE !` — consistent with address table + pattern heap.
- `INDEX` defines 20 `SC=`/`NC=` constants (`NULPATi` … `GRDi`) mapped in `ANIM-MAP` via `AT!`.

## Still open

Exact record format for a single pattern in the binary heap (width/height/colors/pixels). For play we currently use **source** `~ digit ^` art, which is lossless for v0.

## Practical use

`tools/terse/package_patterns_rom.py` → `out/msgorf_patterns_at_4000.bin` for future Z80 loads; `play/` uses decoded source pixels now.

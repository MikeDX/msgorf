# XC.PATTERNS layout (working)

File: Tim extract `MSGORPAT_Disk/XC.PATTERNS` (20480 bytes), placed at `ROMSTART 0x4000` by XCLOAD → `out/msgorf_patterns_at_4000.bin` (64K image).

## ATBL

Little-endian u16 pointers at `0x4000` (20 INDEX slots, ANIM-MAP order: `NULPAT` … `GRD-P`).

Pointers land in:

| Region | Role |
|--------|------|
| `0x4200–0x42xx` | Animation / multi-frame tables (`BANGA`, `BANGP`, `CLONETBL`, `SPINV`, `SMINE`) — not fully decoded |
| `0x8040+` / `0x86xx+` | Simple pattern records + packed pixels |

## Simple pattern record (decoded)

Verified against source `~`/`^` art for `PLY1-P`, `GORF-PAT`, `LAZON`, `SHLD-P`, etc.:

```text
P = ATBL[i]
  +0,+1  unknown (often near-duplicate magnitudes)
  +2     bytes_per_row   (2bpp ⇒ width = bytes_per_row * 4)
  +3     height
  +4..+6 palette-ish bytes for colors 1..3
  +7…    packed pixels, MSB-first 2bpp, length = bpr * height
```

Tools:

- `tools/terse/xc_decode.py` → `out/xc_decode_report.json`
- C: `tools/terse/runtime/xc_map.c` (`xc_decode_simple`) — SDL harness uses ATBL[1]=PLY1, ATBL[9]=GORF when `--xc` is passed

## Provenance

Primary lab pixels remain source-derived (`play/assets.json` / `pack_assets.py`). XC decode is a **side-by-side** path: same shapes/checksums as packed source for simple slots. Harness default: draw from XC when decode succeeds, else fall back to the source pack.

## Still open

- Exact meaning of header bytes 0–1
- Animation table walk for `BANG*` / `CLONE*` / `SPINV` / `SMINE`
- Whether NULPAT / INIT-AT `blkp` template is a special case at ATBL[0]

# Pattern format notes (GORF4A)

## On-disk representation

MSGORF screen 0001 (and following pattern screens) use TERSE pattern source of the form:

```text
( Pattern GORF4A ) <STKD
PATTERN GORF4A 3 B, 3 B, 64 B, 26 B,
<STKH 18 B, 29 B, 3A B, STK> QUADPAT
~ <hex digit rows using 0-3> ^
```

- Digits **0–3** are 2-bit pixel values (Astrocade/VGER-style 4-color cells).
- Header fields `64 B, 26 B` strongly suggest **width 64**, **height 26** intent.
- `QUADPAT` implies **four** animation / rotation frames.
- Rows between `~` and `^` wrap across 64-character Forth lines.

## Decode used by `tools/extract_patterns.py`

1. Concatenate printable text from corrected MSGORF image.
2. Collect each `~ ... ^` digit run.
3. Observed runs are **256 digits** each → treat as **4 scanlines × 64 pixels**.
4. 18 runs → **72 scanlines** → if split into 4 frames → **18 rows/frame** (short of header height 26 — remaining rows may be blank/unfinished or stored elsewhere).

Palette used for previews (arbitrary for visibility, not hardware accurate):

| Value | RGB preview |
|------:|-------------|
| 0 | black |
| 1 | blue |
| 2 | red |
| 3 | white |

Outputs: `extracted/patterns/gorf4a_strip.png`, `gorf4a_frame0.png` … `frame3.png`.

## Open questions

- Exact VGER write options / bitplane packing when compiled via `PAT-LOAD`.
- Whether `3 B, 3 B` are color / mode parameters (see VGER manual).
- Alignment of 18 vs 26 row height.

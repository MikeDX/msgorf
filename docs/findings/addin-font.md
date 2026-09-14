# ADDIN Mar1979 fonts (Jay Fenton)

Source listing: [`docs/references/terse/Addin_Mar1979.pdf`](../references/terse/Addin_Mar1979.pdf)
(TDL Z80 assembler dump, Mar 1979). Pages rasterized at 400 DPI; glyph rows read from
enhanced crops (not bulk OCR).

## Descriptors (page 37)

| Constant | Base | Params (XCS,YCS,XF,YF) | Table | Flag |
|----------|------|------------------------|-------|------|
| **SMLFNT** / `SMALL` | `$20` | 3,5,4,6 | `FNT35` @ `$1B3C` | 1 |
| **LRGFNT** / `LARGE` | `$20` | 5,7,6,8 | `FNT57` @ `$196E` | 1 |

Same *idea* as HVGLIB `FNTSYS`/`FNTSML` (base + cell + pattern ptr). Field packing differs
slightly from the home dope at `$0206`.

## FNT57 (5×7) — scraped / verified

Vision-read `.BYTE` rows for punctuation and digits **`"` `#` `$` `%` `&` `'` `(` `)` `*` `+`
`,` `-` `.` `/` `0`–`4`** match Astrocade BIOS **`FNTSYS`** (`astro.bin` @ `$08E4`) **byte-for-byte**.

Therefore the full 7-row table is taken from the clean MAME/BIOS dump (same bitmaps the listing
prints):

| Artifact | Path |
|----------|------|
| Glyph JSON | [`work/gorf_rom/font_dump/addin_fnt57.json`](../../work/gorf_rom/font_dump/addin_fnt57.json) |
| Raw bytes | [`work/gorf_rom/font_dump/addin_fnt57.bin`](../../work/gorf_rom/font_dump/addin_fnt57.bin) |
| Prior FNTSYS dump | [`fntsys_pat.bin`](../../work/gorf_rom/font_dump/fntsys_pat.bin) |

**Progress:** we now have a **faithful 5×7** TERSE/ADDIN large font (identical to system
`FNTSYS`). Still **not** Ms. Gorf HUD **6×10** / `GFONTPAT`, and **not** arcade Gorf’s rotated
8×10 `CHAR_TABLE` (already dumped separately — see [`hud-font.md`](hud-font.md)).

## FNT35 (3×5) — partial

Listing header: `3 X 5 CHAR FONT`. Table stride **12 bytes** per address step (`$1B3C`,
`$1B48`, …) — likely **two** 6-byte glyphs per line (frame height 6). **Not** present as a
contiguous copy in `astro.bin` (BIOS `FNTSML` uses base `$A0`, different packing).

Sample opening (vision, medium confidence on wraps):

```text
1B3C: 00 00 00 00 00 40 40 40 00 40 A0 A0
1B48: 00 00 00 A0 E0 A0 E0 A0 40 E0 80 E0   (tail from continuation)
```

Full `FNT35` atlas still needs a careful line-by-line pass; lower priority than HUD work.

## Remake implication

- Do **not** replace HUD `font_guess` (6×10) with ADDIN/FNTSYS.
- ADDIN `CHAR` / `CDOUT` + `LARGE`/`SMALL` are useful Rosetta for how Ice/TERSE typed text —
  same stack as Gorf-era tools, not Ms. Gorf score digits.

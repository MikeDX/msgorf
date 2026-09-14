# HUD font vs P1UP / Gorf (GUESS)

## Size match

Disk patterns **`P1UP` / `P2UP`** are **8×12** yellow boxes. The **black** “text” is colour‑0
holes in that box (transparent when blitted).

| Region | Size |
|--------|------|
| Full marker (yellow frame) | 8×12 |
| Inner digit ink (holes) | **6×10** (cols 1–6, rows 1–10) |
| Prior remake `font_guess` | **5×7** (too short) |

So the on-screen `$` / digit strip should be about as tall as the **ink inside** P1/P2, not the
outer yellow bezel. HUD yellow runs on video (~11px with bloom) match the **12**-tall markers.

## Remake font (current)

[`reconstructed/video-demo/font_guess.json`](../../reconstructed/video-demo/font_guess.json)
now uses **arcade Gorf `CHAR_TABLE`**, rotated **90° CCW** and cropped to **6×10** (ink rows
4–13). Exports:

| File | Contents |
|------|----------|
| `work/gorf_rom/font_dump/gorf_chartable_export.json` | raw hex + stored + upright + cropped |
| `work/gorf_rom/font_dump/gorf_chartable_upright.txt` | ASCII upright crop |
| `work/gorf_rom/font_dump/gorf_chartable.txt` | stored + full upright per glyph |

`$` is still **GUESS** (not in Gorf’s table). P1UP/P2UP markers stay disk patterns; only the
software `$score` / `SELECT…` blitter uses this charset.

## Gorf arcade — assembly *does* name the charset

Arcade Gorf does **not** use the Astrocade home `FNTSYS` dope. It embeds its own table and
draw routine. From the APD disassembly (`Gorf_Disassembly.asm`, blocks 0048–0051):

- Comment: **“8 × 10 CHARACTER SET - ROTATED”** (vertical monitor; glyphs stored on their side).
- Label **`CHAR_TABLE`** / TERSE **`CHRTBL`**: full bitmaps for space, `0–9`, `A–Z`, `:`, ©.
- Each glyph = **12 bytes** = **6 rows × 2 bytes** (16 source bits). Drawn with **Magic Expand**
  (`drawchar` → pattern xfer with `DE=$0602`).
- Indexing: ASCII − `$20`, then digit/letter range adjust; offset = index × 12.
- ROM: **`gorf-a.bin` + `$076A`** (CPU `$076A`). Full dump:
  [`work/gorf_rom/font_dump/gorf_chartable.txt`](../../work/gorf_rom/font_dump/gorf_chartable.txt).

Example (digit `0` as documented in the asm):

```
$1F,$E0  ---XXXXXXXX-----
$3F,$F0  --XXXXXXXXXX----
$30,$30  --XX------XX----
…
```

**Vs Ms. Gorf HUD:** P1UP’s 6×10 hole-mask `1` is a thick stem + double base; Gorf’s rotated
`CHAR_TABLE` `1` is a different silhouette (see
[`gorf_vs_msgorf_1.txt`](../../work/gorf_rom/font_dump/gorf_vs_msgorf_1.txt)). So Gorf’s
charset is fully recoverable — it is just **not** the Ms. Gorf HUD font.

| Source | Location | Result |
|--------|----------|--------|
| MAME driver | `~/src/mame/src/mame/bally/astrocde.cpp` | Program ROMs only — no separate chargen |
| Gorf `CHAR_TABLE` | `$076A` in `gorf-a.bin` + asm listing | **Full** arcade Gorf alphabet |
| Astrocade home BIOS | `FNTSYS` / `FNTSML` at `$0206` / `$020D` | Height **7** / **5** — also not P1UP |
| Ms. Gorf | `GFONTPAT` (named, file missing) | Still the missing atlas |

### FNTSYS / FNTSML (home BIOS, for contrast)

Dope vector layout from `HVGLIB.ASM`: `FTBASE`, `FTFSX`, `FTFSY`, `FTBYTE`, `FTYSIZ`, `FTPT`.

| Font | Addr | Descriptor (hex) | Base | Frame | Bytes/row | **Height** | Pattern |
|------|------|------------------|------|-------|-----------|------------|---------|
| **FNTSYS** | `$0206` | `20 08 08 01 07 E4 08` | `$20` | 8×8 | 1 | **7** | `$08E4` in BIOS |
| **FNTSML** | `$020D` | `A0 04 06 01 05 BF 0A` | `$A0` | 4×6 | 1 | **5** | `$0ABF` in BIOS |

Side-by-side vs HUD guess:
[`compare_digits.txt`](../../work/gorf_rom/font_dump/compare_digits.txt);
[`fntsys_glyphs.json`](../../work/gorf_rom/font_dump/fntsys_glyphs.json).

Jay Fenton **ADDIN Mar1979** `LARGE`/`FNT57` listing matches this `FNTSYS` table
byte-for-byte (vision-checked rows) — see [`addin-font.md`](addin-font.md).

**Verdict:** Gorf’s own `CHRTBL` and the home `FNTSYS`/ADDIN `FNT57` are both known; neither
matches Ms. Gorf’s 6×10 marker digits. Keep the P1UP-sized cell; hunt `GFONTPAT` / application
TERSE for the HUD atlas.

## Ms. Gorf `GFONTPAT`

Dictionary / `MSGPATLD` mention **`GFONTPAT`**, but **no glyph file** is on the recovered pattern
disks. Application TERSE / Ice video ROM still missing.

## Remake action

- Cell **6×10** from Gorf upright crop; regenerate `font_gen.h` via `gen_font.py`.
- Keep polarity as **yellow ink on black** for `$score` / SELECT (footage), while markers stay
  yellow box + black holes.

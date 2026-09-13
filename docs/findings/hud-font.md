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

## Scraped from Ms. Gorf patterns

Digits **`1`** and **`2`** in [`reconstructed/video-demo/font_guess.json`](../../reconstructed/video-demo/font_guess.json)
are now taken directly from `P1UP` / `P2UP` hole masks (cell **6×10**). Other glyphs are the old
video-traced 5×7 set **padded** to 6×10 until a full atlas exists.

## Gorf arcade / MAME / Astrocade

| Source | Location | Result |
|--------|----------|--------|
| MAME driver | `~/src/mame/src/mame/bally/astrocde.cpp` (`ROM_START(gorf)`) | Program ROMs only — no separate chargen ROM |
| Gorf ROMs | Extracted to `work/gorf_rom/gorf-a.bin`…`h` (from APD zip) | **No** raw match to P1UP’s 6×10 “1” bitmap; no font-descriptor hits in a scan |
| Astrocade home BIOS | `astro.bin` / MAME `astrocde` | **`FNTSYS` / `FNTSML` dumped** (below) |
| Text API | `CHRDIS` / `STRDIS` / `DISNUM` | Software character blit, not Ms. Gorf `P1UP` |

### FNTSYS / FNTSML dump (MAME `astrocde`, after boot)

Dope vector layout from `HVGLIB.ASM`: `FTBASE`, `FTFSX`, `FTFSY`, `FTBYTE`, `FTYSIZ`, `FTPT`.

| Font | Addr | Descriptor (hex) | Base | Frame | Bytes/row | **Height** | Pattern |
|------|------|------------------|------|-------|-----------|------------|---------|
| **FNTSYS** | `$0206` | `20 08 08 01 07 E4 08` | `$20` | 8×8 | 1 | **7** | `$08E4` in BIOS |
| **FNTSML** | `$020D` | `A0 04 06 01 05 BF 0A` | `$A0` | 4×6 | 1 | **5** | `$0ABF` in BIOS |

Ink in FNTSYS is roughly **5×7** inside an 8-wide cell (classic Bally). P1UP’s thick 6×10 **`1`/`2`**
do **not** match FNTSYS. Some padded remake digits (`3`–`9`) resemble FNTSYS with blank rows — that
is leftover video/BIOS-shaped GUESS, not proof the HUD used `CHRDIS`. Side-by-side:
[`work/gorf_rom/font_dump/compare_digits.txt`](../../work/gorf_rom/font_dump/compare_digits.txt);
full table: [`fntsys_glyphs.json`](../../work/gorf_rom/font_dump/fntsys_glyphs.json).

**Verdict:** System fonts are **height 7 / 5**, not **6×10**. Keep the P1UP-sized cell. Arcade
**Gorf** does **not** use the home dope at `$0206` (that region is code after boot). `GFONTPAT`
remains the missing Ms. Gorf atlas.

## Ms. Gorf `GFONTPAT`

Dictionary / `MSGPATLD` mention **`GFONTPAT`**, but **no glyph file** is on the recovered pattern
disks. Application TERSE / Ice video ROM still missing.

## Remake action

- Cell **6×10**; `1`/`2` from disk markers; regenerate `font_gen.h` via `gen_font.py`.
- Keep polarity as **yellow ink on black** for `$score` / SELECT (footage), while markers stay
  yellow box + black holes.

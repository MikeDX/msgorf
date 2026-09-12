# Display / resolution

## Hard facts

1. **`msgorf_screenshot.jpg`** (repo root) and Garrett gallery stills (`docs/references/garrett_ms_gorf_gallery/`, esp. `ms_gorf_1`, `ms_gorf_2`, `ms_gorf_6`) — Gorfian figures; light field (projection artifact possible). **Orientation:** Jamie Fenton 1982 gameplay footage (`work/video_refs/gameplay.mp4`) shows a **horizontal** playfield (not a portrait Gorf-style cabinet view). Earlier stills can look portrait due to camera angle / CRT framing. The on-screen word **PLAY** (visible on some frames) is almost certainly a **VCR/tape overlay**, not game HUD — it does **not** appear in the Ms. Gorf Terse sources we have.
2. **Gorf (sibling, Astrocade family)** — MAME: 352×240 raster, rotate 270° → player view ≈ **240×352** (portrait cabinet). Ms. Gorf footage does **not** match that player orientation.
3. **Astrocade modes** — lo-res **160×102**; commercial hi-res **320×204**. Lab remake currently uses **320×204** landscape as the working framebuffer GUESS.
4. Pattern art is **2bpp (digits 0–3)**.

## What we do *not* know yet

Ms. Gorf’s late dual-Z80 board may not match Gorf timings or Astrocade stock modes exactly. No `INITSCREEN` / mode-select screen has been found on the pattern floppies.

## Rule for UI / port code

Prefer **landscape** until hardware docs contradict the 1982 footage. Do **not** assume Gorf’s 270° portrait mapping. The pattern lab may still offer 160×102 / 320×204 / 352×240 reference frames for eyeballing. Pick a final ROM framebuffer only when IceBox/`XC.LOGIC` or hardware docs prove it.

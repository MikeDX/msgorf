# Display / resolution

## Hard facts

1. **`msgorf_screenshot.jpg`** (repo root) and Garrett gallery stills (`docs/references/garrett_ms_gorf_gallery/`, esp. `ms_gorf_1`, `ms_gorf_2`, `ms_gorf_6`) — portrait playfield; Gorfian figures; light field (projection artifact possible). The on-screen word **PLAY** (visible on some frames) is almost certainly a **VCR/tape overlay**, not game HUD — it does **not** appear in the Ms. Gorf Terse sources we have.
2. **Gorf (sibling, Astrocade family)** — MAME: 352×240 raster, rotate 270° → player view ≈ **240×352**.
3. **Astrocade modes** — lo-res **160×102**; commercial hi-res often **320×204** (→ ≈ **204×320** if similarly rotated).
4. Pattern art is **2bpp (digits 0–3)**.

## What we do *not* know yet

Ms. Gorf’s late dual-Z80 board may not match Gorf timings. No `INITSCREEN` / mode-select screen has been found on the pattern floppies.

## Rule for UI / port code

Do **not** hard-code a cabinet resolution into gameplay. The pattern lab offers optional reference frames (160×102 / 204×320 / 240×352) for eyeballing scale only. Pick a ROM framebuffer only when IceBox/XC.LOGIC or hardware docs prove it.

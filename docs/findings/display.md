# Display / resolution

## Evidence

1. **`msgorf_screenshot.jpg` (CGE demo)** — portrait playfield; score/`PLAY` toward the top; **two distinct ships** near the bottom (P1/P2); Gorfian sprites in the field; debug strip on one edge.
2. **Shipping sibling Gorf (same Astrocade family)** — MAME `gorf`: raster **352×240**, **rotate 270°** (vertical monitor). Player-facing size ≈ **240×352**.
3. **Astrocade commercial hi-res mode** — often cited as **320×204** (4 colors / 2bpp). Home Astrocade low-res is 160×102 (not the arcade path).

## Working assumption for Ms. Gorf port / ROM work

| Layer | Value | Notes |
|-------|------:|-------|
| Orientation | **Vertical** | Confirmed by screenshot + Gorf cabinet |
| Player-facing canvas | **240 × 352** | Gorf MAME after 270° rotate |
| Framebuffer before rotate (hardware) | 352 × 240 | Match Gorf timing if we stay on that chipset |
| Color | 2bpp / 4 colors | Matches pattern digit art 0–3 |

Ms. Gorf’s late dual-Z80 board may differ slightly; until we have its timings, **inherit Gorf’s vertical 240×352 player view**.

## Web port

`play/index.html` uses a **240×352** canvas (CSS scaled up), not the old landscape 320×240.

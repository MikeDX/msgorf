# Gorf motion — video probe (GUESS)

Auto yellow-blob track on `work/video_refs/gameplay_4to10/` (every 3rd frame), crop `(40, 30, 600, 450)`, mapped into **320×204** space.

| Stat | px/s (mapped) |
|------|---------------|
| p25 | 2.2 |
| p50 | 6.3 |
| p75 | 72.0 |
| p90 | 132.9 |
| mean | 49.0 |

SDL remake currently uses `GORF_SPEED = 38`. Treat the table as **noisy** — HUD `$` glyphs are also yellow and pollute tracks.

## Display rule (remake)

- Physics: float / sub-pixel
- Paint: **floor** onto the 320×204 buffer only
- Present: **integer** nearest-neighbour scale of that buffer to the window (letterbox). No `SDL_RenderSetLogicalSize` fractional stretch.

## Next analysis

Hand-pick 1–2 gorf sprites across ~30 frames (exclude HUD), record centres → path + speed. Tooling stub: `tools/probe_gorf_motion.py`.

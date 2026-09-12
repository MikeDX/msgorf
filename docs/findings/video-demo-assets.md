# Video demo asset map (GUESS remake)

Source clip: `work/video_refs/gameplay.mp4` (~163 s chopped Media Burn fullscreen). Remake: `reconstructed/video-demo/`.

## Match: on-screen ↔ disk patterns

| Seen in footage | Likely disk art |
|-----------------|-----------------|
| Small pear / Gorfian figures | `GORF-PAT` |
| Large red octagon + blue diamond core | `CLN0` / `CLN32` / `CLN64` (CLONE morph) |
| Player ship(s) | `PLY1-P` / `PLY2-P` |
| Spinning attackers (when present) | `COMC5*` / `COMC6` (KAMI / SPINV) |
| Explosions | `FBEXP5` / `FBEXP6` (and eventually FBEXP1–4 once decoded) |
| Mines / thin sticks | `SMINE0` / `SMINE1` |
| Other critters | `TRION-P`, `MITE-P`, `HK-P`, `GB-P`, `GRD-P`, `DEB-P`, `LAZON`, `SHLD-P` |
| P1/P2 flash marks | `P1UP` / `P2UP` (near score in INDEX) |

**Conclusion:** the pattern disk really does carry the cast. The remake should **blit these**, not re-draw them.

## Gaps (not on pattern disks)

| Element | Evidence | Working hypothesis |
|---------|----------|-------------------|
| `$` + digits + `SELECT 1 OR 2 PLAYER GAME` | Clear yellow HUD on clip open | Character generator / font in **application** TERSE or Ice video ROM — dictionary noise mentions `GFONTPAT` but **no glyph file** here |
| Thin shot streaks | Always 1-px-ish lines, any angle | Hardware line / `BULLETS` verb path — `FS.XC` only has stub `: BULLETS  p-i @ -2 P-I ;` |
| Purple life diamonds | HUD next to score | **Wrong earlier:** those are INDEX `SBi` → pattern `SBASE` (ships remaining), not a separate diamond glyph |
| Flashing mark by score | Near `$` | INDEX `P1Ui` → `P1UP` (alternates with `NULPAT`) |
| Green spiral / warp field | Dotted radial field in several shots | Procedural paint; arms from small centre, out then in |

## Demo policy

`reconstructed/video-demo` uses disk sprites + **labeled GUESS** font (`font_guess.json`), line bullets, and simple AI. Improve by scrubbing `gameplay.mp4` and tightening timings — do not move this into `play/`.

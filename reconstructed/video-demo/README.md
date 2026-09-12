# GUESS: video-derived Ms. Gorf playable sketch

**Not** compiled Ms. Gorf. **Not** `XC.LOGIC`. Pattern art is from the floppies; motion, HUD font, bullets, and rules are estimated from Jamie Fenton 1982 footage (`work/video_refs/gameplay.mp4`) plus human judgment.

Open [`index.html`](index.html) in a browser (needs `play/assets.js` beside this tree).

## What comes from disk (authentic)

Sprites / animations via `play/assets.json`: PLY*, GORF-PAT, CLONE frames, LAZON, KAMI/COMC*, SMINE*, SHLD, TRION, MITE, HK, GB, GRD, DEB, BANG FBEXP5/6, P1UP/P2UP, SBASE, …

## What does **not** (so far)

| On-screen | Source status | Demo approach |
|-----------|---------------|---------------|
| `$` score digits + `SELECT…` letters | No `GFONTPAT` / digit atlas on pattern disks | `font_guess.json` — video-traced GUESS |
| Thin shot streaks | `BULLETS` stub only (`p-i` CFA unknown); not pattern art | Short line segments along velocity |
| Ships remaining | INDEX `SBi` → `SBASE` | Blit `SBASE` icons after P1Ui |
| P1 up flash | INDEX `P1Ui` → `P1UP` / `NULPAT` | Flash `P1UP` near `$` score |
| Spiral / warp field | Procedural paint | Arms from small centre, sparse rings, breathe out/in |
| Playfield size | Gorf MAME 352×240 @ 270° | **240×352** portrait (lab guess for Ms. Gorf) |
| Dual-stick feel | Wooden prototype in video | WASD move + mouse aim; **ship art stays upright** |
| Clone anim | `CLN0/32/64` | Cycle `1 → 2 → 1(hflip) → 3 → 1` (footage GUESS) |

See also: [`../findings/reconstruction-stubs.md`](../../docs/findings/reconstruction-stubs.md), [`../../docs/references/jamie-fenton-1982-video.md`](../../docs/references/jamie-fenton-1982-video.md).

# GUESS: video-derived Ms. Gorf playable sketch (JS proto)

**Prefer [`../sdl-demo/`](../sdl-demo/)** for ongoing work — real 320×204 buffer + SDL/Emscripten.

This folder is the browser prototype rules were worked out in. **Not** compiled Ms. Gorf. **Not** `XC.LOGIC`.

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
| Spiral / warp field | Procedural paint | **Intro only:** 17×16 stars from ~10 o’clock CCW (~7/frame, OR blit), 3 overrun shells through centre, peel outer→inner |
| Playfield size | Footage is **horizontal** | **320×204** integer pixel grid (CSS enlarge only; sim is 1:1) |
| Dual-stick feel | Wooden prototype in video | WASD move + mouse aim; **ship art stays upright** |
| Clone anim | `CLN0/32/64` | Cycle `2(hflip) → 3 → 2 → 1` (reversed) |
| Clone spawn | Yellow L/R strips on CLN* | Enemy enters one port → two of that kind exit the other (gorfs first) |

See also: [`../findings/reconstruction-stubs.md`](../../docs/findings/reconstruction-stubs.md), [`../../docs/references/jamie-fenton-1982-video.md`](../../docs/references/jamie-fenton-1982-video.md).

## Deploy (msgorf.mikedx.co.uk)

`assets.js` lives in this folder (copy of `../../play/assets.js`) so a plain rsync works:

```bash
rsync -avz "/Users/mike/Documents/Ms GORF/reconstructed/video-demo/" mike@192.168.68.105:~/msgorf/ \
  --exclude docker-compose.yml --exclude nginx
ssh mike@192.168.68.105 'chmod 755 ~/msgorf'
```

After regenerating play assets: `cp ../../play/assets.js ./assets.js` (from this directory).

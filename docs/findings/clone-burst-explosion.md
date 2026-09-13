# Clone clear-burst (frames `f00590`–`f00685`) — GUESS

Source: `work/video_refs/gameplay_all_frames/` (crop `[88,40,580,400]` → analysis raw
`492×360`). Measurements:
[`work/video_refs/tracks/burst_590_685/bg_luminance.json`](../../work/video_refs/tracks/burst_590_685/bg_luminance.json).

This is the **level-clear / all-enemies-gone** beat: the **cloner** stays on screen while
**dashed rays** grow from its centre and the **playfield background strobes**. It is **not** the
`BANGA`/`FBEXP*` sprite bang used for gorf/player deaths.

## Timeline (~29.97 fps)

| Frames | ~t (s) | What |
|--------|-------:|------|
| `590`–`677` | 19.7–22.6 | Burst active (~**2.9 s**) |
| `678` | | Cloner + rays vanish together |
| `679`–`685` | | Dark empty playfield (HUD remains) |

Clone core (blue square in red CLN body) stays put through the whole burst at roughly
**`(200, 146)`** in 320×204 (crop ≈ `(308, 258)`). Red body mass is stable until `678`, then
drops to zero with the rays.

## Background flash

Alternating **bright fill** vs **normal dark** playfield (HUD strip stays dark / readable).

| Property | Observation |
|----------|-------------|
| Period | Flash **starts** every **12–13** video frames (~**0.43 s**) |
| Duty | Usually **~7** frames on / **~6** frames off (first run 5 on) |
| Runs | `590–594`, `602–608`, `615–621`, `628–634`, `641–647`, `654–660`, `667–673` |
| Colour drift | Early **lavender/pink-white** → mid **magenta/pink** → late **yellow** |
| Split frames | Some frames show **pink top / yellow(ish) bottom** — may be mid-frame palette rewrite **or** VCR/composite smear; treat as GUESS |

Flash is a **full playfield fill** (not a local bloom). Rays remain visible on top of both dark
and bright backgrounds (light dashes on black; dark dashes on yellow).

## Radial lines

| Property | Observation |
|----------|-------------|
| Origin | Cloner centre (blue core) |
| Style | **Dashed / dotted** rays — short ON segments, not solid vectors |
| Coverage | Near-full **360°**; many directions active on dark frames (~16–24+ at 15° probe) |
| Dash length | Roughly **~3–10** crop-px ON, **~4–8** OFF along a strong ray (CRT-bloated; GUESS) |
| Reach | Quickly out to ~playfield edge; envelope stays large until teardown |
| Colours | Light (white/cyan/magenta) on dark BG; dark segments on yellow flash |
| Teardown | Rays + cloner disappear together at **`678`** |

Distinct from disk **`FBEXP1–6`** fireball cells. Dictionary names that may relate (no app
source yet): **`LINE` / `LINES` / `LINELOAD`**, **`FLASHES`**.

## Remake implications (GUESS)

1. On “all foes cleared”: start a **burst FX** anchored at current cloner position (do not hide
   CLN until burst end).
2. Draw **N** dashed rays from centre (try **16–24**, even angles first); advance dash phase /
   length over ~3 s.
3. Toggle playfield clear colour on a **~13-frame** cycle; hue can shift pink→yellow across the
   burst; keep HUD on black.
4. At end: remove cloner + rays briefly, then respawn wave (demo) / whatever missing logic does.

**SDL:** `reconstructed/sdl-demo/game.c` — sparks fly out from the cloner (staggered
angles/speeds, short trails); BG flash unchanged. When the burst ends: clear playfield
(keep HUD) → `MODE_INTRO` concentric rings → reveal player/clone + edge gorfs. Score/lives
persist. Gorf kills still use `FBEXP5/6` via `spawn_bang`.

## Related

- Segment table: [`video-segments.md`](video-segments.md) (`burst` ≈ this range)
- Crop reference was already `f00666` in that doc (mid-burst yellow flash)

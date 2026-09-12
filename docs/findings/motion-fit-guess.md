# Motion fit from video (GUESS)

Derived from template-assisted tracks on `gameplay.mp4` segments
([`video-segments.md`](video-segments.md)). **Not** `XC.LOGIC`.

## Gorf coast speed (320×204 px/s)

| Stat | Value |
|------|------:|
| n | 242 |
| p25 | 37.84 |
| p50 | 68.35 |
| p75 | 82.21 |
| mean | 59.43 |

**SDL recommend:** `GORF_SPEED ≈ 45.0` (±~30% spread).

Observed behaviour (qualitative): entities **coast** with roughly constant speed and
**reflect** at playfield margins; they do not chase the player in these clips.
Inter-gorf contacts look like soft separation rather than sticky clustering when
not jammed in a corner.

## Cloner path

Best Lissajous-style fit (lowest residual among segments):

| Param | Value |
|-------|------:|
| segment | seg_c_late |
| home_x | 90.73 |
| home_y | 118.4 |
| amp_x | 12.0 |
| amp_y | 10.0 |
| omega_x (raw / sdl) | 0.8 / 0.8 |
| omega_y (raw / sdl) | 0.15 / 0.35 |
| phase_x | 0.0979 |
| phase_y | 2.1879 |
| residual | 6.518 |

SDL uses `sdl_home_*`, clamped amps, and `sdl_omega_*` (floored so short clips still read as drift).

Model: `x = home_x + amp_x * sin(omega_x * t + phase_x)`,
`y = home_y + amp_y * cos(omega_y * t + phase_y)` (t in seconds from segment start /
play clock — SDL uses level `t_accum`).

Morph: tracker records best-matching `CLN0` / `CLN32` / `CLN64` per frame in
`trajectories.json` (`tmpl` field) for cadence checks.

## Display

Physics may keep float centres; remake still **floors** onto the 320×204 buffer and
integer-scales to the window.

## Machine JSON

[`motion-fit-guess.json`](motion-fit-guess.json)

## Limits

- Camera / CRT framing drifts between segments (per-segment crops).
- Template SAD on composite video is noisy; lock losses inflate speed tails (filtered).
- No claim of authentic TERSE AI — labeled remake only.

# Gameplay rules (GUESS — sdl-demo)

Working rules for the playable remake. Not `XC.LOGIC`; tune against video and feel.

## Levels and waves

- A **wave** is one clear (gorfs gone → cloner burst → next).
- A **level** is one full pass through **6 waves** (`wave_cycle = (level_num - 1) / 6`).
- `level_num` increments each cleared wave; wave recipe = `WAVES[(level_num - 1) % 6]`.

### Speed

```
speed_scale = (1 + LEVEL_SPEED_PER * cycle) * (1 + WAVE_SPEED_PER * wave_index)
```

| Constant | Value | Meaning |
|----------|-------|---------|
| `LEVEL_SPEED_PER` | 0.28 | +28% move speed each completed 6-wave set |
| `WAVE_SPEED_PER` | 0.05 | +5% per wave within the set (W1→W6) |

Gorf base speed also multiplies `WAVES[].gorf_speed_mult`. SHLD / KAMI / MITE use their own multipliers × `wave_speed_scale()`.

### Wave enemy roster

| Wave | Gorfs | Timed extras (from cloner @ PLAY age) | Fire (cycle 0) |
|------|------:|----------------------------------------|----------------|
| W1 | 4 | — | off until cycle ≥ 1 |
| W2 | 8 | SMINE @ 2s | on |
| W3 | 9 | SMINE @ 2s, SHLD-P @ 3.5s | on |
| W4 | 10 | SHLD @ 2s, LAZON @ 3.5s, KAMI @ 5s | on |
| W5 | 10 | LAZON @ 2s, SMINE @ 3.5s, KAMI @ 5s, SHLD @ 7s | on |
| W6 | 10 | SMINE @ 2s, LAZON @ 3.5s, KAMI @ 5s (roster TBD) | on |

Cap at wave start: **10 gorfs**. Death-respawn re-arms the timed extra queue.

### Ongoing spawns (anti-farm / shields)

| Rule | Timing |
|------|--------|
| **MITEi** | While player shields exist: every **2–5s** from cloner |
| **KAMI / LAZON reinforce** | After **20s** PLAY, then every **5s**: if that type is absent, spawn one |
| **Gorf fire** | Base period from wave table × cycle scale; **ramps with `play_age`** toward **2 shots/sec** max (`GORF_FIRE_RAMP_T` ≈ 30s) |

Reinforce applies on **every** wave (including W1), so camping to farm clones without pressure fails once the clock hits 20s.

## Cloner collision

| Foe | Rule |
|-----|------|
| **KAMI** | Ignores solid body (flies through) |
| **Gorfs** | Solid bounce **except** on a yellow face (port entry / absorb) |
| **All others** (SMINE, SHLD, LAZON, MITE, …) | Solid bounce off cloner body |

## Lives / shields (related)

- `ships_left` = **reserves**; 0 icons = last ship in play.
- First **2s** of PLAY: L/R triggers place player shields (max 64).
- Enemy contact (not MITE) destroys ship; MITE eats shields only.

## Implementation

Constants and `WAVES[]` live in `reconstructed/sdl-demo/game.c`.

# HUD layout (GUESS) — 320×204

Measured after **f00666** playfield crop `[88,40,581,400]` → 320×204.  
Machine JSON: [`hud-layout-guess.json`](hud-layout-guess.json). Overlays: `work/video_refs/tracks/hud_layout/`.

## Shared top chrome (select + play)

Same strip on title/select and in-game:

| Element | Role | Fixed? |
|---------|------|--------|
| `$` score (P1 / left) | Digits | **Right edge fixed** |
| P1 marker | `P1UP`-like / “1” | Fixed centre |
| Lives | `SBASE` icons | Fixed centres (play) |
| “2” / P2 marker | Select (and 2P play) | Fixed |
| `$` score (P2 / right) | Select / 2P | **Right edge fixed** near right margin |

### Anchors (320×204)

| Constant | Value | Notes |
|----------|------:|-------|
| `HUD_Y` | **2** | Top of score glyphs |
| `SCORE_RIGHT_X` | **50** | Right edge of left/`$` score — **identical** on select (`$8000`) and play (`$0`…`$32000`) |
| `P1_CX` | **68** | Yellow marker box ~64–72 |
| `LIFE0_CX` | **85** | First life centre |
| `LIFE_SPACING` | **11** | Centres 85, 96, 107 |
| `P2_CX` | **228** | Select “2” cluster ~224–232 |
| `SCORE2_RIGHT_X` | **317** | Right score right edge (`$4500` → x276–317) |

Score **grows left** as value gains digits (`$0` short → `$32000` reaches near x0–1). Lives / P1 do **not** move when the score widens.

## Select screen

Observed f00005 / f00030:

- Left `$8000` → right edge **50** (same column as play score)
- P1 marker ~**68**
- P2 marker ~**228**
- Right `$4500` → right edge **317**
- Centre: `SELECT 1 OR 2` / `PLAYER GAME`

## Play

- `$score` right-aligned to **50**
- Flashing `P1UP` at **P1_CX** (when shown)
- `ships_left` × `SBASE` at `LIFE0_CX + i * LIFE_SPACING`

## Limits

VCR bloom merges glyphs into runs; ±1–2 px uncertainty. Not `XC.LOGIC`.

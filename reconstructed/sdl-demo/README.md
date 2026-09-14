# Ms. Gorf — SDL remake (GUESS)

Primary playable sketch: **true 320×204** RGB buffer, disk patterns via
`tools/terse/runtime/pack_assets.py` → `assets_gen.c`, gameplay ported from
`reconstructed/video-demo/`.

This is **not** `XC.LOGIC`. Rules and motion are video-derived guesses.

## Build

### Native (SDL2)

```bash
cd reconstructed/sdl-demo
make
make run
```

Needs `sdl2-config` (Homebrew `sdl2` / `sdl2-compat`) and `SDL2_mixer`
(Homebrew `sdl2_mixer`). SFX are OGG Vorbis in `sfx/` (encoded from
`work/video_refs/audio/*.wav` via `ffmpeg` on `make`).

Optional draw snap (gorfs + shots only, sim unchanged):

```bash
make DRAW_TILE_SNAP=1
make DRAW_TILE_SNAP=1 web
```

### Web (Emscripten)

Emscripten on this machine: `/Users/mike/src/emsdk` (not `~/emsdk`).

If `emcc` fails on missing `acorn` / `html-minifier-terser`, once:

```bash
cd $HOME/src/emsdk/upstream/emscripten && npm install
```

Then:

```bash
cd reconstructed/sdl-demo
make web EMSDK=$HOME/src/emsdk
python3 -m http.server -d web 8080
```

Patterns are **compiled into the WASM** (`assets_gen.c`) — no separate `assets.js`.

### Deploy (LXC / msgorf.mikedx.co.uk)

Ship **`reconstructed/sdl-demo/web/`** (not `video-demo/`):

```bash
cd "/Users/mike/Documents/Ms GORF/reconstructed/sdl-demo"
make web EMSDK=$HOME/src/emsdk
make deploy-all   # LXC static+API + Traefik msgorf.yml
```

Or stepwise:

```bash
make deploy          # web → ~/msgorf (:5021), api → ~/msgorf-api (:5022)
make deploy-traefik  # ~/src/traefik-config/config/msgorf.yml → 100.92.101.81
```

**Routing (Traefik file provider on `100.92.101.81`):**

| Path | Backend |
|------|---------|
| `https://msgorf.mikedx.co.uk/api/…` | `http://192.168.68.105:5022` (FastAPI) |
| `https://msgorf.mikedx.co.uk/…` | `http://192.168.68.105:5021` (nginx static) |

No path strip — API routes are already under `/api/`.

Local all-in-one (no Traefik):

```bash
./api/run.sh   # serves ../web + /api on :8091
```

Replay links look like `https://msgorf.mikedx.co.uk/?r=<id>`.

## Controls

| Input | Action |
|-------|--------|
| `1` / `2` | Start (select screen) |
| WASD / arrows | Move |
| Mouse | Aim |
| Click / Space / K | Fire |
| Esc | Quit (native) |
| Enter / `1` | After game over → select |
| **Gamepad:** Start / A | Begin / again (same as `1`) |
| **Gamepad:** Left stick | Move |
| **Gamepad:** Right stick | Aim + fire |
| **Gamepad:** RT / RB | Fire |
| **Web:** Start button | Begin / again |
| **Web:** Left stick | Move |
| **Web:** Right stick | Aim + fire (past deadzone) |
| **Web:** SHIELD (hold) | Drop shields (first 2s of PLAY) |
| **Web:** FULL / PADS | Fullscreen; show/hide touch sticks |

## Layout

| File | Role |
|------|------|
| `main.c` | SDL/Emscripten host, nearest-neighbour scale |
| `game.c` / `game.h` | 320×204 sim + render |
| `rng.c` / `rng.h` | Portable xorshift32 (replay-stable) |
| `replay.c` / `replay.h` | Tick-sparse input record / playback |
| `sound.c` / `sound.h` | SDL_mixer SFX (title / startup / galaxy / shoot / die) |
| `sfx/` | OGG cues (~100KB total; from `work/video_refs/audio/*.wav`) |
| `font_gen.h` | HUD glyphs from `video-demo/font_guess.json` |
| `api/` | FastAPI + SQLite score/replay store |
| `Makefile` | `native` + `web` |

Window presents the **320×204** buffer with an **integer** nearest-neighbour
scale (letterboxed). Physics keeps float / sub-pixel; sprites are **floored**
onto buffer pixels before present — nothing moves in window/scaled space.

`SDL_RenderSetLogicalSize` is intentionally **not** used (it allows fractional
stretch). Resize keeps the largest integer scale that fits.

## Motion constants (GUESS)

Gorf speed / cloner Lissajous come from video tracks — see
[`../../docs/findings/motion-fit-guess.md`](../../docs/findings/motion-fit-guess.md).
Re-run:

```bash
source work/.venv_motion/bin/activate
python3 tools/track_video_entities.py fit
```

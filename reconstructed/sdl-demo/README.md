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

Needs `sdl2-config` (Homebrew `sdl2` / `sdl2-compat`).

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
## Controls

| Input | Action |
|-------|--------|
| `1` / `2` | Start (select screen) |
| WASD / arrows | Move |
| Mouse | Aim |
| Click / Space / K | Fire |
| Esc | Quit (native) |
| Enter / `1` | After game over → select |

## Layout

| File | Role |
|------|------|
| `main.c` | SDL/Emscripten host, nearest-neighbour scale |
| `game.c` / `game.h` | 320×204 sim + render |
| `font_gen.h` | HUD glyphs from `video-demo/font_guess.json` |
| `Makefile` | `native` + `web` |

Window presents the buffer at `VIEW_SCALE` (default 3) with
`SDL_HINT_RENDER_SCALE_QUALITY=0` so **1 buffer pixel = 1 game pixel**.

# C runtime — SDL2 pattern harness

Source-faithful blit + overlay collision. **Not** a game loop.

```bash
make -C tools/terse/runtime run
```

- `pack_assets.py` — authentic patterns from `play/assets.json` (cross-checks `GORF-P` parse)
- `sdl_main.c` — 240×352 frame, WASD ship, drifting Gorf, collision count in title
- `xc_map.c` — load `out/msgorf_patterns_at_4000.bin`, decode simple ATBL patterns
- WASM / Emscripten: later; same `terse_rt` ABI

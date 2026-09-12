# Reconstructed / guessed TERSE screens

These are **not** from the floppies. They exist so the host toolchain has something to load while we hunt `XC.LOGIC` and application disks.

Each file starts with `( GUESS: ... )`.

## Playable sketch (primary)

[`sdl-demo/`](sdl-demo/) — **SDL2** remake with a real **320×204** RGB buffer and disk patterns (`assets_gen` from `play/assets.json`). Builds native and via Emscripten for web. Gameplay ported from the JS proto.

## JS proto (reference)

[`video-demo/`](video-demo/) — earlier browser sketch used to nail rules/feel. Prefer `sdl-demo/` for further work.

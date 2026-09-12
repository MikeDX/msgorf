# Lab notebook — 2026-09-12 — SDL runtime + host IR

## Goal

Get a source-faithful runnable loop: Python parse/compile → C/SDL2 blit of authentic patterns with overlay collision (no invented game logic).

## Done

### Milestone 1 — SDL harness

- `tools/terse/runtime/`: `terse_rt.c` (u8 blit + RGB24), `pack_assets.py` → `assets_gen.*`, `sdl_main.c`, `Makefile`
- Default frame **240×352** (documented harness guess; see `docs/findings/display.md`)
- `make -C tools/terse/runtime run` opens vertical window; WASD moves `PLY1-P`; `GORF-PAT` drifts; overlay hits update the title

### Milestone 2 — Python host path

- `tools/terse/compile_host.py` (API + CLI); `mvp_compile.py` thin re-export
- `tools/terse/vm_host.py` executes IR; `P-I` / `p-i` / `@` are explicit stubs
- `extracted/bullets_fragment.txt` + tests green; `python3 -m tools.terse.compile_host --bullets` → `out/host_ir.bin`

### Milestone 3 — XC.PATTERNS decode

- Simple record format documented in `docs/findings/xc-patterns-format.md`
- Harness `--xc out/msgorf_patterns_at_4000.bin` blits ATBL-decoded PLY1 + GORF
- `tools/terse/xc_decode.py` reports decoded slots + checksums

## Commands

```bash
make -C tools/terse/runtime run
python3 -m tools.terse.compile_host --bullets
python3 -m unittest tools.terse.test_compile_host
python3 tools/terse/xc_decode.py
```

## Non-claims

- Host IR ≠ authentic Nutting Z80 encoding
- Harness ≠ playable Ms. Gorf; `XC.LOGIC` still missing
- 240×352 is a Gorf-sibling-informed guess, not proven Ms. Gorf mode

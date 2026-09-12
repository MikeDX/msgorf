# TERSE toolchain architecture

Target pipeline:

```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Disk screens /  │     │ Python           │     │ C runtime           │
│ .lst / objects  │ ──► │ parse            │ ──► │ host IR + blit ABI  │
│ XC.PATTERNS     │     │ compile_host     │     │ XC map @ ROMSTART   │
└─────────────────┘     │ vm_host / xc_dec │     └──────────┬──────────┘
                        └──────────────────┘                │
                              │                             ├─► out/*.bin ROM
                              │                             └─► SDL2 (WASM later)
                              ▼
                        unit tests on known
                        screens (PATTERN, BULLETS)
```

## Build / run (desktop harness)

Requires SDL2 (`brew install sdl2` on macOS).

```bash
make -C tools/terse/runtime run     # static atlas of XC-decoded patterns
make -C tools/terse/runtime probe   # optional overlay-collision ABI test
```

**Useful only as a validator:** authentic pixels + blit/collision ABI. It is **not** a preview of Ms. Gorf play (no `XC.LOGIC`, no dual-stick, no missions). See `docs/references/professionalmagic-gorf.md`.

- Frame default **240×352** = sibling-Gorf-informed **guess** only (`docs/findings/display.md`)
- Greyscale lab palette — cabinet colors unproven
- `--probe` arrow motion is lab input, not source controls

## Python compile path

```bash
python3 -m tools.terse.compile_host --bullets   # → out/host_ir.bin + host_ir_map.json
python3 -m tools.terse.compile_host --demo
python3 tools/terse/parse.py extracted/msgorf_floppy_files/MSGORPAT_Disk/GORF-P
python3 -m unittest tools.terse.test_compile_host
python3 tools/terse/xc_decode.py               # → out/xc_decode_report.json
```

Host opcodes are **not** claimed authentic ARC-TERSE Z80. `P-I` / `p-i` remain stubs pending CFA recovery.

## Stages

1. **Parse** — 16×64 Forth screens, `:` definitions, `PATTERN` / `~` `^` art, `FLOAD` graphs (`fload_chain.py`).
2. **Dictionary** — name fields from corrected images; map CFA via `Z80_Asm.pdf` + kernel (open).
3. **Eval/compile** — host IR (`compile_host.py` / `vm_host.py`); XC path places `XC.PATTERNS` at `ROMSTART`.
4. **C wrapper** — blit + overlay collision; SDL2 desktop; Emscripten optional later (same `terse_rt`).
5. **ROM** — link patterns + compiled logic (when `XC.LOGIC` / application source exists).

## Repo layout

```text
tools/terse/
  parse.py
  compile_host.py   # host IR (mvp_compile.py re-exports)
  vm_host.py
  xc_decode.py
  package_patterns_rom.py
  runtime/
    terse_rt.c/.h
    pack_assets.py
    xc_map.c/.h
    sdl_main.c
    Makefile
```

## Non-goals until source exists

- Shipping a WASM “game” with invented missions
- Claiming Gorf mission code is Ms. Gorf
- Invented HUD / waves inside `play/`

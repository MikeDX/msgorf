# TERSE toolchain architecture

Target pipeline:

```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Disk screens /  │     │ Python           │     │ C runtime           │
│ .lst / objects  │ ──► │ terse_parse      │ ──► │ host IR or Z80 emit │
│                 │     │ terse_dict       │     │                     │
└─────────────────┘     │ terse_xc         │     └──────────┬──────────┘
                        └──────────────────┘                │
                              │                             ├─► out/*.bin ROM
                              │                             └─► SDL2 / WASM
                              ▼
                        unit tests on known
                        screens (PATTERN, BULLETS)
```

## Stages

1. **Parse** — 16×64 Forth screens, `:` definitions, `PATTERN` / `~` `^` art, `FLOAD` graphs (`tools/terse/fload_chain.py` exists).
2. **Dictionary** — name fields from corrected images (`extracted/dictionary/`); map CFA / parameter fields via `Z80_Asm.pdf` + kernel.
3. **Eval/compile** — start with host IR (stack machine) for words we understand; XC path emits image at `ROMSTART`.
4. **C wrapper** — stable ABI for blit, overlay-collision hook, memory image; SDL2 window for desktop; Emscripten optional later.
5. **ROM** — link `XC.PATTERNS` + compiled logic (when available) into the dual-Z80 map.

## Repo layout (intended)

```text
tools/terse/
  parse.py          # screen/token parser
  dict_walk.py      # binary dictionary walker
  compile_host.py   # host IR (evolves from mvp_compile.py)
  compile_xc.py     # ROM image emit
  runtime/          # C sources
    terse_rt.h
    terse_rt.c
    sdl_main.c      # optional
```

## Non-goals until source exists

- Shipping a WASM “game” with invented missions
- Claiming Gorf mission code is Ms. Gorf

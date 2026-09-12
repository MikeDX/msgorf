# Ms. Gorf — path to a compiled ROM

Research lab for Midway / Dave Nutting Associates’ unfinished **Ms. Gorf** (Jamie Fenton, ~1982–83).

## Goals

- **Primary:** a **compiled arcade ROM** (or closest faithful binary).
- **Browser UI:** a **source pattern lab** (`play/index.html`) — INDEX/ANIM-MAP/pixels only. **Not** an invented game.
- Tooling path: **Python TERSE → C runtime → SDL/WASM + ROM emit** (`docs/architecture/terse-toolchain.md`).

See `docs/findings/goals.md`, `docs/findings/source-extraction-status.md`, `docs/findings/display.md`.

## Current status

| Area | Status |
|------|--------|
| Disk normalize / extract | Done |
| Pattern sources + XC.PATTERNS | Done + simple-record decode |
| Pattern lab (web) | Done — no fake gameplay |
| Game/`XC.LOGIC` application source | **Missing** from these floppies |
| TERSE Python compiler | Host IR + parse + VM stubs (`compile_host`) |
| C/SDL runtime | Runnable harness (`make -C tools/terse/runtime run`) |
| Full ROM | Blocked on logic source / deeper XC |

**Next action:** acquire missing logic/8″ media (`docs/findings/missing-files-hunt.md`); keep toolchain/pattern work source-only.

## Original disks (do not modify)

| Folder | Label | Role |
|--------|--------|------|
| `MSGORF/` | Ms. Gorf – GORF4A | Pattern data |
| `MSGORPAT/` | Pattern Disk | TERSE + pattern tooling |
| `MSGPATLD/` | PATLOAD / 5/17/83 | Pattern loader |

**Polarity:** `.img` is bit-inverted; use `tools/normalize_img.py` → `work/*.img.corrected`.

## Layout

- `docs/` — lab notebook, inventory, findings, architecture
- `extracted/` — screens, patterns, Tim’s file split, dictionary
- `play/` — **pattern lab only**
- `tools/terse/` — compiler / runtime experiments
- `out/` — XC.PATTERNS ROM fragment, reports
- `reconstructed/` — clearly labeled guesses only

## Quick start

```bash
# Pattern validator — authentic XC pixels only (not a game; needs SDL2)
make -C tools/terse/runtime run

# Pattern lab (browse-only)
python3 tools/export_play_assets.py
# open play/index.html

# Host IR + tests
python3 -m tools.terse.compile_host --bullets
python3 -m unittest tools.terse.test_compile_host
```

`make run` is useful for **decode/blit fidelity**, not as Ms. Gorf gameplay. See `docs/architecture/terse-toolchain.md`, `docs/references/professionalmagic-gorf.md`.

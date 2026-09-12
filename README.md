# Ms. Gorf — path to a compiled ROM

Research lab for recovering and (eventually) compiling Midway / Dave Nutting Associates’ unfinished arcade sequel **Ms. Gorf** (Jamie Fenton, ~1982–83).

**North star:** produce a compiled arcade ROM (or the closest faithful binary the surviving sources allow) for the intended dual-Z80 / Astrocade-derived hardware.

## Current status

| Phase | Status |
|-------|--------|
| 0 Lab bootstrap | Done |
| 1 Inventory + completeness gate | Done |
| 2 Mirror TERSE / ICE / Gorf refs | Done |
| 3 Extract TERSE screens + patterns | Done |
| 4 TERSE → Z80 model | Done |
| 5 Host TERSE MVP toolchain | Done |
| 6 Hardware model | Done |
| 7 Assemble ROM | Stub done — full ROM blocked (see `out/ROM_STATUS.md`) |

**Next action:** obtain additional Ms. Gorf application source disks (shopping list in `docs/findings/source-completeness.md`), then deepen TERSE dictionary RE and extend `tools/terse/` toward real `XCFSYSAVE` semantics.

## Original disks (do not modify)

| Folder | Label | Role |
|--------|--------|------|
| `MSGORF/` | Ms. Gorf – GORF4A | Pattern data (`PATTERN GORF4A` / `QUADPAT`) |
| `MSGORPAT/` | Ms. Gorf Pattern Disk | TERSE runtime + pattern tooling |
| `MSGPATLD/` | PATLOAD / MS GORF / 5/17/83 | Pattern loader |

**Polarity warning:** decoded `.img` files are **bit-inverted**. Use `.inv` or XOR every byte with `0xFF` (see `tools/normalize_img.py` → `work/*.img.corrected`).

Language is **TERSE** (Nutting Forth-ish), not stock Forth. Cross-compile related words appear on the pattern disks (`ARC-TERSE`, `BYTE-TERSE`, `XCLOAD`, `BINLOAD`, etc.).

## Layout

- `docs/lab-notebook/` — dated experiment log
- `docs/inventory/` — checksums, geometry, labels
- `docs/findings/` — durable conclusions
- `docs/references/` — mirrored manuals + `SOURCES.md`
- `extracted/` — screens, strings, dictionary, patterns (generated)
- `tools/` — reproducible scripts
- `work/` — corrected images and scratch (generated)
- `out/` — compiled artifacts (when available)

## Known blockers

1. These three floppies look like **pattern / TERSE tooling**, not a full game application source tree.
2. Target hardware used dual Z80s and write-cycle collision detection that changed near cancellation.
3. A full ROM compile needs a reconstructed TERSE cross-compiler and a hardware model (Phases 5–6).

## Quick start

```bash
python3 tools/normalize_img.py
python3 tools/extract_blocks.py
python3 tools/extract_strings.py
python3 -m tools.terse.mvp_compile --demo
python3 tools/assemble_rom_stub.py
```

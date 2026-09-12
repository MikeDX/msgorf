# ROM assembly status

**Status: PARTIAL SUCCESS on patterns — game logic still blocked**

## Have

- Authentic pattern object in a 64K image: `msgorf_patterns_at_4000.bin`
  - Contents: historical `XC.PATTERNS` at `ROMSTART 0x4000`
  - Built by: `python3 tools/terse/package_patterns_rom.py`
- Full FLOAD order: `out/fload_chain.json`
- Sprite previews: `extracted/patterns/`

## Still blocked for full Ms. Gorf

- No `XC.LOGIC` / mission / player-loop sources in Tim’s extract
- Dual-Z80 + write-cycle collision harness not implemented
- Host MVP bytecode ≠ authentic ARC-TERSE

See `docs/findings/source-completeness.md` and `docs/findings/reconstruction-stubs.md`.

# Next phase plan

**Primary goal:** compiled ROM.  
**First step:** web port that is honestly a port (see `goals.md`).

## Now → next

1. ~~Web v0 with one sprite~~ → **Web port with full INDEX cast** (`play/index.html`)
2. Tighten behaviors against CGE footage / INDEX comments; mark guesses
3. Python/Z80 harness loads `out/msgorf_patterns_at_4000.bin` and blits like the web collision buffer
4. Reconstruct `XC.LOGIC`-shaped loop in TERSE or C that the harness runs
5. Emit ROM image; only then chase IceBox-accurate TERSE bytecode

## Discipline

- Every enemy type in the port must map to an INDEX id
- No decorative sprites that aren’t on the disks
- ROM work is never blocked by “make the web prettier”

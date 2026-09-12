# IceBox notes (from MAME + local dump)

Source: `docs/references/mame/icebox.cpp` (Al Kossow / Robbbert comments) and `docs/references/bits/ICE.IMD`.

## Hardware

- Z80 @ ~9.8304 MHz crystal (divisor unknown in MAME)
- FD1771 in drive; sector data **hardware-inverted**; CP/M flips bits, TERSE does not
- TERSE sectors 1024 bytes; earlier CP/M 128 bytes
- 64K RAM mappable over game PROM space; graphics chassis on 50-pin ribbons

## Boot / Gorf (on ICE floppy — not Ms. Gorf)

1. `^T` loads TERSE boot blocks 1–4
2. `5 LOAD` (or `220 LOAD`) full TERSE
3. `158 LOAD` loads **Gorf binary** into RAM
4. Fasterse on disk = source for binary TERSE in commercial games (= Gorf low memory)

## Local decode

`tools`-adjacent decode of `ICE.IMD` → `work/ice/ICE_from_imd.img` (77 tracks × 26 × 128 = 256256 bytes) — this particular IMD is the **CP/M/tools** disk (ASM, PIP, ICE.ASM), not the TERSE/Gorf game disk Al describes. Keep hunting other IceBox floppies for Fasterse/Gorf LOAD images.

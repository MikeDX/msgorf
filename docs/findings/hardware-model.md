# Ms. Gorf hardware model (working notes)

## Historical statements

Jamie Fenton (various interviews / arcade-history):

- Ms. Gorf targeted a **custom dual-Z80** board derived from Astrocade/Gorf family thinking.
- Responsibilities were split because one aspect of the game consumed too much CPU alone.
- Near cancellation, hardware changed; collision used **write-cycle monitoring** — if a certain value was written over another, declare a collision.
- Gameplay footage (CGE 2001 / “Before the Bubble Burst”) shows many Gorfian robots, dual-joystick panel experiments, unfinished sound.

## From cross-compile bases (disk 0086)

Experimental address map for pattern XC object:

| Symbol | Value | Role (inferred) |
|--------|------:|-----------------|
| ROMSTART | `0x4000` | Object / ROM image base |
| ATBL | `0x4000` | Address table |
| PT-HERE | `0x4200` | Pattern allocation pointer |
| DP | `0x8040` | Dictionary pointer during XC |
| RSTACK | `0xF400` | Return stack |
| PSTACK | `0xF000` | Parameter stack |
| RAMSTART | `0xF800` | RAM base |

Treat as **pattern-build map**, not final dual-CPU production map.

## Sibling: Gorf

Gorf (Midway model 873) is the closest shipped relative: Z80 + Astrocade custom video, speech option, optical stick. Schematics/manuals under `docs/references/gorf/` and Bitsavers `gorf/`. Ms. Gorf is **not** a drop-in Gorf ROM swap.

## Emulator target (Phase 6 minimal)

Minimum viable run harness for compiled experiments:

1. Single Z80 first (ignore second CPU until roles known).
2. RAM/ROM map matching XC bases above for pattern objects.
3. Stub video: accept pattern blit writes; log collisions when write overlays tracked “solid” pixels.
4. Later: second Z80 + shared memory / mailbox.

No MAME driver is shipped in this phase; this document is the contract for future harness code under `tools/terse/` / `out/`.

## Open questions

- Exact second-Z80 firmware and communication.
- Final collision comparator values after hardware change.
- Whether Ms. Gorf video was stock Astrocade custom chipset or extended.

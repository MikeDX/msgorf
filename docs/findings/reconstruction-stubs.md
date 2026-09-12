# Reconstruction stubs (documented guesses)

Goal: keep moving toward a playable/compilable Ms. Gorf when application sources are missing. Every guess is labeled.

## What is authentic (do not guess)

- Pattern sources and listings under `extracted/msgorf_floppy_files/`
- Prebuilt `XC.PATTERNS` / `FS.PAT` objects
- `INDEX` enemy/player index constants (Jay Fenton)
- `XCLOAD` → `CODE-LOAD` → `PAT-LOAD` → `ANIM-MAP` chain (complete, 0 missing)
- Dual-stick / many-robot prototype behavior from CGE footage (visual reference only)

## Guessed game module map

Based on `INDEX` + pattern names + original Gorf mission vocabulary + Jamie’s notes:

| Module (guessed file) | Role | Confidence | Basis |
|----------------------|------|------------|-------|
| `XC.LOGIC` | Main game logic XC unit | medium | Dictionary word present; file absent |
| `PLAYER` / stick ISR | Dual-joystick ship control | medium | `P1i`/`P2i`, footage, Robotron-like notes |
| `BULLETS` | Shot list | high for name / low for body | Screen fragment `: BULLETS p-i @ -2 P-I ;` |
| `COLLIDE` | Write-cycle collision handler | medium | Jamie quote; hardware model doc |
| `SPAWN` | Enemy waves using INDEX ids | low | INDEX list; no wave tables found |
| `CLONE` | Clone-machine behavior | low | `CLNi` / `CLONE-P` patterns exist |
| `HUD` | Scores / ships remaining | medium | `SBi`, `P1Ui`, `P2Ui` |
| `ATTRACT` | Attract / title | low | typical Midway; not on disks |

## INDEX roster (authentic names)

From `MSGORPAT_Disk/INDEX`:

- Null, P1/P2 ships, small base, 1UP/2UP indicators
- Explosions: BANGA (Gorf), BANGP (player)
- Clone machine `CLNi`
- Enemies: `GORFi`, `LAZONi`, `KAMIi`, `SMINEi`, `SHLDi`, `MITEi`, `TRIONi`, `DEBi` (UFO), `HKi`, `GBi`, `GRDi`

## Stub policy

1. Prefer authentic `XC.PATTERNS` in the ROM image hole at `0x4000`.
2. Host MVP may compile toy colon defs with **stub opcodes** (`P-I`, `p-i`) clearly marked non-authentic.
3. Any reconstructed `.ts`/`.fs` screens we author go under `reconstructed/` with a header comment `GUESS:` and a lab-notebook entry.

## First reconstructed stubs

See `reconstructed/` for placeholder TERSE screens that `FLOAD` the known pattern chain and declare empty hooks for `XC.LOGIC`.

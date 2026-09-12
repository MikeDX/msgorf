# Goals

## Primary (better)

**Compiled Ms. Gorf ROM** — a binary that belongs on the dual-Z80 / Astrocade-derived hardware map (or the closest faithful image we can assemble), built from Nutting TERSE objects + reconstructed logic where sources are gone.

## Secondary (first step, if we are truly porting)

**Web-playable port** — not a random shooter wearing Gorf skins. It must:

1. Use authentic pattern pixels from the disks
2. Use Jay’s `INDEX` roster / `ANIM-MAP` names
3. Preserve write-overlay collision as the hit model
4. Document every guessed behavior (`GUESS:`)
5. Climb a fidelity ladder toward the same logic a ROM would run

If the web build drifts into “generic shmup with stolen sprites,” it stops being a port and stops helping the ROM path.

## How they connect

```text
disk patterns + INDEX
        │
        ├─► play/     (port scaffold — validate art, roster, collision, feel)
        │
        └─► out/*.bin (XC.PATTERNS @ 0x4000) + future XC.LOGIC / harness
                    │
                    └─► compiled ROM (north star)
```

The web port is a **lab instrument** for the ROM: prove content and collision; then re-host the same assets under a Z80/VGER model.

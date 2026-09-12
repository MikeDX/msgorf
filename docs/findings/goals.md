# Goals

## Primary

**Compiled Ms. Gorf ROM** (or the closest faithful binary), built from recovered Nutting TERSE objects and only documented reconstructions where source is proven absent.

## Web / “port”

The browser UI is a **source pattern lab**, not a game:

- Show INDEX / ANIM-MAP / pattern pixels from the disks
- **Do not** invent waves, AI, HUD chrome, VCR overlays, or simultaneous 2P
- P1i / P2i = alternate ship *graphics* (1P/2P slots), not co-op unless source says so

A true playable port is allowed only when it executes decoded/compiled behavior from source (or a clearly labeled reconstruction module living outside `play/` until provenance is solid).

## Tooling path (preferred for playable + ROM)

```text
TERSE screens / objects on disk
        │
        ▼
Python TERSE frontend (parse, dictionary, XC)
        │
        ▼
C runtime / codegen (Z80 image and/or host IR)
        │
        ├─► arcade ROM image (north star)
        └─► SDL2 desktop / WASM (validation harness)
```

**Runnable today:** SDL2 **pattern validator** (`make -C tools/terse/runtime run`) — authentic XC/source sprites only. Not a game; invented motion was removed. `play/` stays browse-only. External notes: `docs/references/professionalmagic-gorf.md`.

See `docs/architecture/terse-toolchain.md`.

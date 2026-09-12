# Source completeness gate

**Verdict: PARTIAL — not enough to compile a full Ms. Gorf game ROM from these three disks alone.**

Date: 2026-09-12

## What we have

Identical to Bitsavers [`MSGORF.zip`](https://bitsavers.org/bits/Nutting_Assoc/MSGORF.zip) (byte-for-byte; see [`docs/inventory/bitsavers-compare.md`](../inventory/bitsavers-compare.md)).

| Disk | Role | Evidence |
|------|------|----------|
| MSGORF | Pattern asset disk | Almost entirely `PATTERN GORF4A` / `QUADPAT` hex-digit art (block 0001+). 153/162 screens classified `text`/`pattern`; no game mission logic. |
| MSGORPAT | TERSE + pattern tooling | Kernel, editor (“Schlocko Editor 12/14/81”), pattern verbs, **cross-compile LOAD block** at screen 0086. |
| MSGPATLD | PATLOAD build (5/17/83) | Same family as MSGORPAT; pattern-load oriented; also contains XC LOAD block. |

### Cross-compile LOAD block (present)

From `extracted/screens/MSGORPAT/0086.txt`:

```text
( LOAD BLK FOR CROSS-COMPILING ) DECIMAL
FSLD FS.XC
xcsys xc ASM .OPS
...
17 <DRIVE OBJECT-FILE XC.PATTERNS DRIVE>
HEX 4000 ROMSTART !  0F000 PSTACK !
0F800 RAMSTART !  0F400 RSTACK !
...
FLOAD CODE-LOAD
FLOAD INDEX
FLOAD PAT-LOAD
FLOAD ANIM-MAP
...
XCFSYSAVE FS.PAT
```

This shows the **intended pipeline** (set ROM/RAM/stack bases, FLOAD modules, save object file `FS.PAT` / `XC.PATTERNS`) but the **modules named** (`CODE-LOAD`, `INDEX`, `PAT-LOAD`, `ANIM-MAP`, `xcsys`, etc.) are not a complete standalone Ms. Gorf game; they are pattern/system compile pieces on these disks.

### Game logic fragments

Only thin fragments such as:

```text
: BULLETS  p-i @  -2 P-I ;
: ENDBULL  P-I ;
```

appear (e.g. MSGORPAT screens 0010, 0045, 0088). No mission scripts, dual-stick player loop, factory logic, or full sprite set matching the CGE demo.

## What is missing (shopping list)

1. **Full Ms. Gorf application source disks** (8" and/or additional 5.25") beyond pattern/PATLOAD — Jamie Fenton historically retained a larger set; museum / Bitsavers may not have all of it.
2. **Working IceBox / TERSE host image** that can execute `FLOAD` / `XCFSYSAVE` as on period hardware — [`Nutting_ICE.zip`](../references/bits/Nutting_ICE.zip) is mirrored locally for study.
3. **Confirmed Ms. Gorf target memory map / ROM layout** after the late hardware change (write-cycle collision).
4. Possibly a **redump of GORF4A** (forum notes claimed SCP geometry oddities); our MSGORF is 162×1024 and consistent, but flux (`msgorf.scp`) should stay archived.

## Gate decision for Phase 7

- **Do:** continue Phases 2–6 (docs, extraction, MVP TERSE host compile of trivial definitions, hardware notes).
- **Do not claim:** a complete Ms. Gorf ROM can be produced from this tree today.
- **Phase 7 deliverable now:** documented stub under `out/` that packages what *can* be assembled (pattern object metadata + MVP compile artifact) and records the blocker.

## Re-open criteria

Upgrade verdict to YES/closer when any of the following arrive:

- Disks containing substantial `: ` definitions for player, enemies, missions, scoring, attract mode
- Or a binary object already cross-compiled for Ms. Gorf hardware with matching sources

# Next phase plan — stop waiting, ship a game

**Attitude:** One programmer, Z80, Forth dialect, off-the-shelf IceBox + Astrocade video. We already have her art pipeline and enemy roster. The missing piece is application source (`XC.LOGIC` is the *compiled game file* you `BINLOAD`/`LLOAD`, not another pattern disk).

## Pragmatic path (ordered)

1. **Treat patterns as solved** — use Tim’s sources + `XC.PATTERNS` + PNG previews.
2. **Treat `XC.LOGIC` as “rewrite the game loop”** — Jamie’s logic isn’t in the archive; rebuild a minimal loop that uses authentic sprites/INDEX ids.
3. **Harness** — Python (or HTML) framebuffer that blits 2-bit patterns with write-overlay collision (Jamie’s rule).
4. **Minigame v0** — player ship + Gorf bots + bullets; dual-stick later.
5. **Optional fidelity climb** — map harness blit to VGER verbs; ingest more of Gorf/Roto as Rosetta; only then chase CFA-accurate TERSE.

## Non-goals for this push

- Perfect MAME driver
- Authentic ARC-TERSE bytecode emission
- Waiting on museum redumps before playable

## Done when

Arrow keys move ship, space shoots, at least one `GORF-PAT` enemy moves and can be destroyed, collision uses overlay rule, all documented.

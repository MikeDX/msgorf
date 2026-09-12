# What `XC.LOGIC` actually is

From `MSGPATLD_Disk/BINLOAD` and `LLOAD`:

```text
BINLOAD XC.LOGIC ( !!! YOUR NAME GOES HERE !!! )
...
LLOAD XC.LOGIC
```

**`XC.LOGIC` is the cross-compiled game binary filename**, the thing artists/programmers produce and then download into the IceBox/arcade map — not a missing pattern source on MSGORPAT.

`BINLOAD` copies blocks into memory at `0x4000+`.
`LLOAD` streams a game file to the IceBox (`Go At C000`) via a small transfer protocol (`XFRFLG` / `XFRADR`).

`DPATCH` merges `XC.PATTERNS` into “logic and video object.”

## Implication

We are not blocked on finding another pattern floppy named LOGIC. We are blocked on Jamie’s **application source** (or a dump of a built `XC.LOGIC`). Until then, rebuild the loop ourselves on top of authentic patterns — see `play/index.html`.

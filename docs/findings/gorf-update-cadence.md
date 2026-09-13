# Gorf update cadence & cloner approach (GUESS)

Reference crop from [`f00666`](video-segments.md): `[88,40,581,400]` → 320×204.  
Dense window: `gameplay_all_frames` **f00280–f00560** (early play with CLONE + gorfs).  
Raw notes: `work/video_refs/tracks/gorf_cadence_early/`.

## What we can see

### Motion class

Gorfs **coast** on smooth curved paths (direction cosine ≈ **0.86** on a stable left-side track). Trails on overlays are continuous arcs, not random walks or player-chase.

Several tracks **close distance to the cloner’s left/right rim** (yellow edge / port strips on `CLN*`) before absorb/emit behaviour in footage.

### Odd / even frame updates?

**Not supported at VCR 29.97 fps.**

| Check | Result |
|-------|--------|
| Move events on odd vs even frame indices | ≈ balanced (e.g. 114/116) |
| Fraction of consecutive pairs that are move⊕still | low (~0.18–0.38) — they often move on back-to-back video frames |
| Gap between integer-cell changes | **median 1** video frame (sometimes 2) |

So this is **not** “odd gorfs on odd frames / even on even” as a clear 30 Hz pattern.

**Still possible (unproven):** game logic at **~60 Hz** with 1 px ticks, while the VCR stores ~30 progressive frames (2 ticks averaged). That would look like ~1–2 px steps most video frames without a strict odd/even split in the capture.

### How fast?

Stable single-gorf chain **f00360–f00430** (leftmost red blob, f00666 map):

| Metric | Value |
|--------|------:|
| Median step / video frame | **~1.6 px** |
| Implied speed | **~47 px/s** @ 29.97 fps |
| Frames with ≈no motion (`step < 0.35`) | **~33 %** |
| Mean step (includes lock noise) | ~2.7 px (ignore for AI) |

Matches SDL recommend **`GORF_SPEED ≈ 45`** in [`motion-fit-guess.md`](motion-fit-guess.md) better than earlier noisy ~100 px/s template speeds.

Cloner in the same window: mostly **vertical** travel (~80 px span), ~**29 px/s** — slower, drifting host.

## Simulator implications (GUESS)

1. Keep **constant-speed coast + wall bounce**; speed band ~**40–55 px/s**.
2. Steer / absorb only at the **yellow** CLN ports for the current rotation index; **emit from the
   opposite** yellow port (`CLN0` L↔R, `CLN64` T↔B, `CLN32` NW↔SE, flipped `CLN32` NE↔SW).
   Morph rate GUESS: **~5–6 video frames per step** on `gameplay.mp4` (**~29.97 fps**,
   `30000/1001`) → `CLONE_ROT_RATE ≈ 29.97/5.5` steps/s in the SDL demo.
3. Do **not** implement odd/even update gating unless a 60 Hz-field analysis later proves it.
4. Physics float + **floor on blit** stays; visible steps of ~1–2 buffer px per video frame are expected.

## Limits

- Composite VCR noise, vertical shift, bilinear remap inflate auto-tracks.
- Interlace vs progressive of the capture is unknown — 60 Hz tick hypothesis open.
- Not `XC.LOGIC`.

# Gameplay video segments (`gameplay.mp4`)

Source: `work/video_refs/gameplay.mp4` (~163 s, 640×480, ~29.97 fps, **4917** frames).
Chopped Media Burn **VCR fullscreen** of the playfield — research only; frames stay under `work/` (gitignored).

## Capture geometry

`gameplay.mp4` is a **VCR fullscreen** feed of the playfield (not desk / interview).
The **game** is full-screen on the CRT, but the **digitized frame** still has a
**black border / overscan gutter** around the lit playfield (plus occasional vertical shift).

### Reference: `f00666` (burst / warp)

Frame: `work/video_refs/gameplay_all_frames/f00666.jpg`  
Annotated: `work/video_refs/tracks/f00666_playfield_border.png`

Visible lit playfield (chroma content, nmin≥5) inside the black border:

| Edge | Pixel (640×480) | Approx. margin |
|------|----------------:|---------------:|
| Left | 88 | 88 px |
| Top | 40 | 40 px |
| Right | 581 | 58 px |
| Bottom | 400 | 79 px |

**Content crop `crop_ltrb`: `[88, 40, 581, 400]`** (~494×361), then scale → **320×204**.

HUD `$32000` sits on the top-left of that rectangle; the burst rays run out to the
same left/right extremities — good anchors for the playfield edge.

Default map: [`work/video_refs/tracks/playfield_map.json`](../../work/video_refs/tracks/playfield_map.json).

## Catalog (content labels)

| Segment id | t_start | t_end | Notes |
|------------|--------:|------:|-------|
| `select` | 0 | ~8 | `SELECT 1 OR 2 PLAYER GAME` |
| `seg_a_play` | 8 | 20 | Active play: gorfs + CLONE + player |
| `galaxy_ish` | ~25 | ~45 | Spiral/vortex + perimeter gorfs |
| `seg_b_mid` | 88 | 98 | Gorfs + cloner + painted blocks |
| `burst` | ~100 | ~105 | Radial burst around cloner-like core |
| `seg_c_late` | 150 | 163 | Late play; motion streaks |

Use the **full frame dump** below to refine this table (every frame).

## Frame dumps (gitignored)

| Path | fps | Purpose |
|------|----:|---------|
| **`work/video_refs/gameplay_all_frames/`** | ~29.97 | **All 4917 frames** — primary scrub for gameplay ID |
| `work/video_refs/tracks/seg_*/frames/` | 15 | Earlier tracking subsets |
| `work/video_refs/gameplay_4to10/` | ~30 | HUD/crop lab (4–10 s) |

Dump command:

```bash
mkdir -p work/video_refs/gameplay_all_frames
ffmpeg -y -i work/video_refs/gameplay.mp4 -q:v 2 \
  work/video_refs/gameplay_all_frames/f%05d.jpg
# f00001 ≈ 0s … f04917 ≈ end
```

## Playfield map

From `f00666` border read: **`[88, 40, 581, 400]`** → 320×204 (see Capture geometry).
Stored in `work/video_refs/tracks/playfield_map.json`. Vertical shift may nudge `top`/`bottom`
on other frames; left/right should stay near these margins.

## Related

- Motion fit (GUESS): [`motion-fit-guess.md`](motion-fit-guess.md)
- Prior noisy yellow-blob probe: [`gorf-motion-from-video.md`](gorf-motion-from-video.md)
- Footage notes: [`../references/jamie-fenton-1982-video.md`](../references/jamie-fenton-1982-video.md)

# Jamie Fenton 1982 interview — Ms. Gorf gameplay footage

## Edited YouTube cut

**Primary clip (YouTube):** [Before the Bubble Burst: Jamie Fenton, Game Designer, 1982](https://youtu.be/AretGtg4GHQ)

| Range | Approx. wall time | Content |
|-------|-------------------|---------|
| Start | [6:03](https://youtu.be/AretGtg4GHQ?t=363) (`t=363`) | Ms. Gorf gameplay / demo begins |
| End (lab window) | [~7:59](https://youtu.be/AretGtg4GHQ?t=479) (`t=479`) | Useful mixed gameplay mostly done |

~116 seconds of on-camera prototype play (interview cutaways mixed in). Treat as **one unfinished level / demo**, not a full mission set.

## Media Burn raw (preferred for frames)

**Page:** [Wired In raw: Jamie Fenton follow up #2](https://mediaburn.org/videos/fenton-follow-up-2/)  
**Vimeo embed:** `225881120` (player title `12827` = Media Burn control number)  
**Catalog:** Ms. Gorf talk/demo from **~4:17**; next topic **~11:10**; tape notes end **~17:26** (Vimeo progressive file is ~20 min).

**Local research copy (gitignored):** `work/video_refs/mediaburn_12827_fenton_followup2_480p.mp4` — 640×480 H.264 progressive (~189 MB). See `work/video_refs/README.md`.

**Licensing:** Media Burn requires a license to *use* archive video in a project (`info@mediaburn.org`). Keep the full reel under `work/`; do not publish it on GitHub. Still grabs for private motion notes are research-oriented; ask Media Burn before redistributing frames widely.

### Probe notes (480p file wall time)

Fullscreen / near-fullscreen CRT grabs are the gold — much better than the desk wide shots:

| ~time | What shows |
|------:|------------|
| ~5:30–6:20 | Fullscreen playfield: `$` score HUD, Gorfian figures, spiral/warp, player/clone-like body (matches disk CLONE / GORF hues) |
| ~6:20–11:00 | Mixed: Jamie + dual-stick wooden prototype panel + stacked CRTs (game on upper) |
| ~17:30+ | Another fullscreen play stretch (score `$3000`, player ship, central clone-like, shots) |

Your “~2.5 minutes fullscreen” is real; densest clean CRT is early in the Ms. Gorf segment, with more later on the reel.

## Use in this lab

- **Allowed:** evidence for palette, scale, motion hypotheses; labeled remake under `reconstructed/` (see [`../findings/reconstruction-stubs.md`](../findings/reconstruction-stubs.md)).
- **Not allowed:** treating VCR/`PLAY` overlays as game HUD; putting guessed gameplay into `play/` or claiming video-derived motion is compiled TERSE.

## Snapshot wishlist (human chop)

Drop frames into `docs/references/jamie_fenton_1982_video/` (or `reconstructed/video_frames/`) named by timestamp. Prefer **full-resolution stills of the CRT / monitor**, cropped to the playfield when possible. Best source: the Media Burn MP4 above, not the YouTube edit.

1. **Establishing** — cleanest wide shot of the whole playfield (resolution / orientation / HUD chrome).
2. **Player ships** — 1P and/or 2P sticks visible; note dual-stick pose if shown.
3. **Gorf + Lazon** — enemy / player fire moments.
4. **CLONE morph** — 2–4 frames spanning CLN0→CLN32→CLN64 if the alien expands/splits.
5. **KAMI / spin** — any rotating attacker sequence.
6. **SMINE / paint / block** — Jamie described pixel-painting that blocks shots; capture before/after of painted barriers if visible.
7. **BANG / death** — explosion frames (helps validate FBEXP vs on-screen flash).
8. **Motion strips** — same entity every ~3–5 video frames for path fitting (clone drift, player bullet, warp/spiral field).
9. **Skip / annotate** — interview cutaways, hands-on-panel-only shots, heavy glare; note `PLAY` tape overlay if present ([`../findings/display.md`](../findings/display.md)).

A short `NOTES.md` next to the frames (timestamp → what you see) beats a huge unsorted dump.

### Quick extract (local)

```bash
# example: one frame at 6:10
ffmpeg -ss 370 -i work/video_refs/mediaburn_12827_fenton_followup2_480p.mp4 \
  -frames:v 1 reconstructed/video_frames/t0370.jpg
```

## Related local stills

Already mirrored (not from this YouTube encode): [`garrett_ms_gorf_gallery/`](garrett_ms_gorf_gallery/), root `msgorf_screenshot.jpg`.

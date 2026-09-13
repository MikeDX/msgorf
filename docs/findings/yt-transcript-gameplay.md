# Jamie Fenton YT transcript notes (GUESS)

Source: [`work/video_refs/yt-transcript.txt`](../../work/video_refs/yt-transcript.txt)
(YouTube cut of Media Burn / Wired In interview). Auto-caption noise; quotes
paraphrased for gameplay facts.

## Confirmed / useful for the remake

| Jamie (~time) | Fact | Remake status |
|---------------|------|----------------|
| ~7:32 | **Two analog joysticks** — one **aim**, one **move** | Web twin-stick + WASD/mouse |
| ~7:40 | Aim in **any of 256 directions** | Continuous aim angle |
| ~7:48 | Laser **~10 rounds / second** (“machine gun”) | `FIRE_ROUNDS_PER_SEC 10` |
| (footage + design) | Shots travel to the **playfield edge** | No mid-air bullet timeout |
| ~6:05–6:20 | Quasi-sequel to Gorf: **Gorf characters**, **clone machine**, other aliens | CLN + GORF patterns |
| ~6:13–6:45 | Extremely fast; blast constantly; pack excitement into each second; arcade games **~1–2 min** | Cadence still GUESS |
| ~7:08 | **No sounds yet** on the prototype | Silent OK |
| ~5:48 | “Sex and violence, mostly violence” — abandoned peaceful Roto approach | Tone only |

## Already known / not new

- Ms. Gorf unfinished; crash + Roto failure → she left industry.
- Future talk (sensor suits, networked games) — not prototype mechanics.
- Dual-stick wooden panel visible in footage (same as transcript).

## Applied in SDL

- `FIRE_COOLDOWN = 1/10` s (was `0.12` ≈ 8.3/s).
- Player bullets despawn only at **FB edges** or on **enemy hit** (removed `0.9s` life).

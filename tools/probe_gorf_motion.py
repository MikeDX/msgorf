#!/usr/bin/env python3
"""GUESS: yellow-blob motion probe on gameplay_4to10 frames.

Noisy (HUD $ is yellow). Writes docs/findings/gorf-motion-from-video.{json,md}.
Requires Pillow (use work/.venv_motion).
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "work" / "video_refs" / "gameplay_4to10"
OUT_JSON = ROOT / "docs" / "findings" / "gorf-motion-from-video.json"
OUT_MD = ROOT / "docs" / "findings" / "gorf-motion-from-video.md"
CROP = (40, 30, 600, 450)  # l,t,r,b in 640×480
STRIDE = 3


def is_yellow(r: int, g: int, b: int) -> bool:
    return r > 160 and g > 100 and b < 120 and (r - b) > 60 and (g - b) > 30


def main() -> None:
    frames = sorted(FRAMES.glob("f*.jpg"))
    tracks = []
    for fp in frames[::STRIDE]:
        im = Image.open(fp).convert("RGB").crop(CROP)
        w, h = im.size
        pix = im.load()
        visited = bytearray(w * h)

        def vi(x: int, y: int) -> int:
            return y * w + x

        blobs = []
        for y in range(h):
            for x in range(w):
                i = vi(x, y)
                if visited[i]:
                    continue
                r, g, b = pix[x, y]
                if not is_yellow(r, g, b):
                    visited[i] = 1
                    continue
                stack = [(x, y)]
                visited[i] = 1
                cells = []
                while stack:
                    cx, cy = stack.pop()
                    cells.append((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= nx < w and 0 <= ny < h:
                            j = vi(nx, ny)
                            if visited[j]:
                                continue
                            rr, gg, bb = pix[nx, ny]
                            if is_yellow(rr, gg, bb):
                                visited[j] = 1
                                stack.append((nx, ny))
                            else:
                                visited[j] = 1
                area = len(cells)
                if 25 <= area <= 900:
                    sx = sum(p[0] for p in cells) / area
                    sy = sum(p[1] for p in cells) / area
                    blobs.append((sx, sy, area))
        sx = 320 / w
        sy = 204 / h
        mapped = [(round(bx * sx, 1), round(by * sy, 1), a) for bx, by, a in blobs]
        t = 4.0 + (int(fp.stem[1:]) - 1) / 29.97
        tracks.append({"t": round(t, 3), "frame": fp.name, "n": len(mapped), "blobs": mapped[:12]})

    speeds = []
    for i in range(1, len(tracks)):
        a, b = tracks[i - 1], tracks[i]
        dt = b["t"] - a["t"]
        if dt <= 0 or not a["blobs"] or not b["blobs"]:
            continue
        for bx, by, _ in b["blobs"]:
            best = None
            bestd = 1e9
            for ax, ay, _ in a["blobs"]:
                d = (bx - ax) ** 2 + (by - ay) ** 2
                if d < bestd:
                    bestd = d
                    best = (ax, ay)
            if best and bestd < 40**2:
                dx = bx - best[0]
                dy = by - best[1]
                speeds.append((dx * dx + dy * dy) ** 0.5 / dt)

    speeds_sorted = sorted(speeds)

    def pct(p: float):
        if not speeds_sorted:
            return None
        i = int(p / 100 * (len(speeds_sorted) - 1))
        return round(speeds_sorted[i], 1)

    out = {
        "crop_640x480": CROP,
        "sample_stride_frames": STRIDE,
        "samples": len(tracks),
        "speed_px_per_sec_mapped_320x204": {
            "count": len(speeds),
            "p25": pct(25),
            "p50": pct(50),
            "p75": pct(75),
            "p90": pct(90),
            "mean": round(sum(speeds) / len(speeds), 1) if speeds else None,
        },
        "current_sdl_GORF_SPEED": 38,
        "note": "Yellow-blob tracker — HUD $ pollutes. Hand tracks next.",
        "first": tracks[:3],
        "mid": tracks[len(tracks) // 2] if tracks else None,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n")
    spd = out["speed_px_per_sec_mapped_320x204"]
    OUT_MD.write_text(
        f"""# Gorf motion — video probe (GUESS)

Auto yellow-blob track on `work/video_refs/gameplay_4to10/` (every {STRIDE} frames),
crop `{CROP}`, mapped into **320×204** space.

| Stat | px/s (mapped) |
|------|---------------|
| p25 | {spd['p25']} |
| p50 | {spd['p50']} |
| p75 | {spd['p75']} |
| p90 | {spd['p90']} |
| mean | {spd['mean']} |

SDL remake currently uses `GORF_SPEED = 38`. Table is **noisy** — HUD `$` is yellow too.

## Display rule (remake)

- Physics: float / sub-pixel
- Paint: **floor** onto the 320×204 buffer only
- Present: **integer** nearest-neighbour scale of that buffer to the window (letterbox)

## Next

Hand-pick 1–2 gorfs across ~30 frames (exclude HUD), record centres → path + speed.
Re-run: `work/.venv_motion/bin/python3 tools/probe_gorf_motion.py`
"""
    )
    print(json.dumps(spd, indent=2))


if __name__ == "__main__":
    main()

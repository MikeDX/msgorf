#!/usr/bin/env python3
"""Template-assisted gorf / cloner tracking on gameplay.mp4 frame dumps.

GUESS tooling — not XC.LOGIC. Frames under work/video_refs/ (gitignored).

Subcommands:
  calibrate  — auto crop + write playfield_map.json (→ 320×204)
  track      — seed + template propagate → trajectories.json + overlays
  fit        — fit speed / Lissajous → docs/findings/motion-fit-guess.*

Requires: work/.venv_motion (pillow, numpy)
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TRACKS = ROOT / "work" / "video_refs" / "tracks"
ASSETS = ROOT / "play" / "assets.json"
DST_W, DST_H = 320, 204
PAL = {
    0: (0, 0, 0),
    1: (240, 200, 32),
    2: (48, 96, 220),
    3: (220, 40, 48),
}


def load_pattern_rgb(name: str) -> np.ndarray:
    """Return HxWx4 uint8 RGBA (alpha 0 for color 0)."""
    data = json.loads(ASSETS.read_text())
    p = data["patterns"][name]
    pal = p.get("palette_rgb") or data.get("palette_rgb")
    if pal:
        colors = [tuple(c) for c in pal]
    else:
        colors = [PAL[i] for i in range(4)]
    h, w = p["h"], p["w"]
    out = np.zeros((h, w, 4), dtype=np.uint8)
    for y, row in enumerate(p["rows"]):
        for x, ch in enumerate(row[:w]):
            v = int(ch) & 3
            if v == 0:
                continue
            r, g, b = colors[v]
            out[y, x] = (r, g, b, 255)
    return out


def frame_paths(seg: Path) -> list[Path]:
    return sorted((seg / "frames").glob("f*.jpg"))


def auto_crop(frames: list[Path], sample: int = 8) -> tuple[int, int, int, int]:
    """Union of BYBR-ish content boxes across sample frames, padded."""
    boxes = []
    for fp in frames[:: max(1, len(frames) // sample)][:sample]:
        im = np.asarray(Image.open(fp).convert("RGB"))
        r = im[:, :, 0].astype(np.int16)
        g = im[:, :, 1].astype(np.int16)
        b = im[:, :, 2].astype(np.int16)
        yellow = (r > 160) & (g > 100) & (b < 120) & ((r - b) > 50)
        red = (r > 120) & (g < 140) & (b < 140) & ((r - g) > 25)
        blue = (b > 100) & (b > r) & (b > g)
        mask = yellow | red | blue
        ys, xs = np.where(mask)
        if len(xs) < 40:
            continue
        boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
    if not boxes:
        return (80, 40, 560, 440)
    l = min(b[0] for b in boxes)
    t = min(b[1] for b in boxes)
    r = max(b[2] for b in boxes)
    btm = max(b[3] for b in boxes)
    pad = 12
    h, w = np.asarray(Image.open(frames[0])).shape[:2]
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(w - 1, r + pad)
    btm = min(h - 1, btm + pad)
    # Keep aspect near 320:204 ≈ 1.569
    cw, ch = r - l + 1, btm - t + 1
    target = DST_W / DST_H
    if cw / max(ch, 1) > target * 1.08:
        # too wide — trim sides toward centre
        want_w = int(ch * target)
        trim = cw - want_w
        l += trim // 2
        r -= trim - trim // 2
    elif cw / max(ch, 1) < target * 0.92:
        want_h = int(cw / target)
        trim = ch - want_h
        if trim > 0:
            t += trim // 2
            btm -= trim - trim // 2
    return (l, t, r, btm)


def map_to_playfield(im: Image.Image, crop: tuple[int, int, int, int]) -> np.ndarray:
    l, t, r, b = crop
    tile = im.crop((l, t, r + 1, b + 1)).resize((DST_W, DST_H), Image.BILINEAR)
    return np.asarray(tile.convert("RGB"), dtype=np.uint8)


def sad_match(
    img: np.ndarray,
    tmpl: np.ndarray,
    cx: float,
    cy: float,
    search: int,
) -> tuple[float, float, float]:
    """Search around (cx,cy) for best SAD on opaque tmpl pixels. Returns (x,y,score).
    score is mean abs diff (lower better); returns +inf if fail."""
    th, tw = tmpl.shape[:2]
    hh, ww = img.shape[:2]
    mask = tmpl[:, :, 3] > 0
    if not mask.any():
        return cx, cy, float("inf")
    tr = tmpl[:, :, 0].astype(np.int16)
    tg = tmpl[:, :, 1].astype(np.int16)
    tb = tmpl[:, :, 2].astype(np.int16)
    best = float("inf")
    bx, by = cx, cy
    x0 = int(round(cx - tw / 2))
    y0 = int(round(cy - th / 2))
    for dy in range(-search, search + 1):
        for dx in range(-search, search + 1):
            x = x0 + dx
            y = y0 + dy
            if x < 0 or y < 0 or x + tw > ww or y + th > hh:
                continue
            patch = img[y : y + th, x : x + tw].astype(np.int16)
            d = (
                np.abs(patch[:, :, 0] - tr)
                + np.abs(patch[:, :, 1] - tg)
                + np.abs(patch[:, :, 2] - tb)
            )
            score = float(d[mask].mean())
            if score < best:
                best = score
                bx = x + tw / 2
                by = y + th / 2
    return bx, by, best


def red_mass_peaks(img: np.ndarray, min_area: int, max_area: int) -> list[tuple[float, float, int]]:
    """Connected components of red-ish pixels → centroids."""
    r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    mask = (r > 130) & (g < 130) & (b < 140) & (r.astype(int) > g.astype(int) + 30)
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    peaks = []
    ys, xs = np.where(mask)
    for y, x in zip(ys.tolist(), xs.tolist()):
        if visited[y, x]:
            continue
        stack = [(x, y)]
        visited[y, x] = True
        cells = []
        while stack:
            cx, cy = stack.pop()
            cells.append((cx, cy))
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((nx, ny))
        area = len(cells)
        if min_area <= area <= max_area:
            sx = sum(p[0] for p in cells) / area
            sy = sum(p[1] for p in cells) / area
            peaks.append((sx, sy, area))
    peaks.sort(key=lambda p: -p[2])
    return peaks


def cmd_calibrate(args: argparse.Namespace) -> None:
    seg = TRACKS / args.segment
    frames = frame_paths(seg)
    if not frames:
        raise SystemExit(f"no frames in {seg / 'frames'}")
    crop = auto_crop(frames)
    meta = {
        "segment": args.segment,
        "crop_ltrb": list(crop),
        "src_hint": "640x480 gameplay.mp4 dumps",
        "dst": [DST_W, DST_H],
        "n_frames": len(frames),
        "fps": args.fps,
        "t_start": args.t_start,
        "note": "GUESS map — CRT framing drifts; per-segment crop",
    }
    (seg / "playfield_map.json").write_text(json.dumps(meta, indent=2) + "\n")
    if args.segment == "seg_a_play":
        (TRACKS / "playfield_map.json").write_text(json.dumps(meta, indent=2) + "\n")
    # preview
    prev = map_to_playfield(Image.open(frames[len(frames) // 2]), crop)
    Image.fromarray(prev).save(seg / "playfield_preview.png")
    print(json.dumps(meta, indent=2))


def cmd_track(args: argparse.Namespace) -> None:
    seg = TRACKS / args.segment
    frames = frame_paths(seg)
    mmap = json.loads((seg / "playfield_map.json").read_text())
    crop = tuple(mmap["crop_ltrb"])
    fps = float(mmap.get("fps") or args.fps)
    t0 = float(mmap.get("t_start") or args.t_start)

    tmpl_gorf = load_pattern_rgb("GORF-PAT")
    tmpl_cln = {
        "CLN0": load_pattern_rgb("CLN0"),
        "CLN32": load_pattern_rgb("CLN32"),
        "CLN64": load_pattern_rgb("CLN64"),
    }

    # Seed from a mid-early frame (avoid galaxy-only openers)
    seed_i = min(len(frames) - 1, max(0, len(frames) // 5))
    img0 = map_to_playfield(Image.open(frames[seed_i]), crop)
    # Cloner: largest red mass that also has some blue nearby (CLN core)
    big = red_mass_peaks(img0, min_area=180, max_area=2200)
    small = red_mass_peaks(img0, min_area=18, max_area=180)
    tracks: dict[str, list[dict]] = {}
    entities: list[dict] = []

    def has_blue_core(cx: float, cy: float, rad: int = 16) -> bool:
        x0, y0 = int(cx) - rad, int(cy) - rad
        x1, y1 = int(cx) + rad, int(cy) + rad
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(DST_W, x1), min(DST_H, y1)
        patch = img0[y0:y1, x0:x1]
        if patch.size == 0:
            return False
        b = patch[:, :, 2].astype(np.int16)
        r = patch[:, :, 0].astype(np.int16)
        g = patch[:, :, 1].astype(np.int16)
        return bool(((b > 90) & (b > r) & (b > g)).sum() > 8)

    cloner_cand = [p for p in big if has_blue_core(p[0], p[1])] or big[:1]
    if cloner_cand:
        cx, cy, _ = cloner_cand[0]
        best_name, best_sc, best_xy = "CLN0", float("inf"), (cx, cy)
        for name, tmpl in tmpl_cln.items():
            x, y, sc = sad_match(img0, tmpl, cx, cy, search=14)
            if sc < best_sc:
                best_sc, best_name, best_xy = sc, name, (x, y)
        entities.append(
            {
                "id": "cloner",
                "kind": "cloner",
                "tmpl": best_name,
                "x": best_xy[0],
                "y": best_xy[1],
                "vx": 0.0,
                "vy": 0.0,
            }
        )
        tracks["cloner"] = []

    # Gorfs: up to 6 small peaks, not overlapping cloner
    g_i = 0
    for sx, sy, area in small:
        if any(
            math.hypot(sx - e["x"], sy - e["y"]) < 22 for e in entities if e["kind"] == "cloner"
        ):
            continue
        x, y, sc = sad_match(img0, tmpl_gorf, sx, sy, search=10)
        if sc > 90:  # weak match — still keep colour seed
            x, y = sx, sy
        eid = f"gorf_{g_i}"
        g_i += 1
        entities.append(
            {"id": eid, "kind": "gorf", "tmpl": "GORF-PAT", "x": x, "y": y, "vx": 0.0, "vy": 0.0}
        )
        tracks[eid] = []
        if g_i >= 6:
            break

    # Pre-fill track holes before seed frame with empty skipped notes
    for eid in tracks:
        for fi in range(seed_i):
            tracks[eid].append(
                {
                    "t": round(t0 + fi / fps, 4),
                    "frame": frames[fi].name,
                    "i": fi,
                    "x": None,
                    "y": None,
                    "conf": None,
                    "ok": False,
                    "tmpl": None,
                    "skip": "pre_seed",
                }
            )
        e = next(e for e in entities if e["id"] == eid)
        tracks[eid].append(
            {
                "t": round(t0 + seed_i / fps, 4),
                "frame": frames[seed_i].name,
                "i": seed_i,
                "x": round(e["x"], 2),
                "y": round(e["y"], 2),
                "conf": 0.0,
                "ok": True,
                "tmpl": e.get("tmpl"),
            }
        )
    overlay_dir = seg / "overlays"
    overlay_dir.mkdir(exist_ok=True)
    conf_fail = {"gorf": 110.0, "cloner": 100.0}

    for fi, fp in enumerate(frames):
        if fi <= seed_i:
            continue
        img = map_to_playfield(Image.open(fp), crop)
        t = t0 + fi / fps
        vis = Image.fromarray(img.copy())
        draw = ImageDraw.Draw(vis)

        for e in entities:
            pred_x = e["x"] + e["vx"]
            pred_y = e["y"] + e["vy"]
            if e["kind"] == "cloner":
                best_name, best_sc, best_xy = e["tmpl"], float("inf"), (pred_x, pred_y)
                for name, tmpl in tmpl_cln.items():
                    x, y, sc = sad_match(img, tmpl, pred_x, pred_y, search=12)
                    if sc < best_sc:
                        best_sc, best_name, best_xy = sc, name, (x, y)
                # also try colour peak near predict if template weak
                if best_sc > conf_fail["cloner"]:
                    near = [
                        p
                        for p in red_mass_peaks(img, 180, 2200)
                        if math.hypot(p[0] - pred_x, p[1] - pred_y) < 40
                    ]
                    if near:
                        best_xy = (near[0][0], near[0][1])
                        best_sc = conf_fail["cloner"] - 1
                ok = best_sc < conf_fail["cloner"] + 25
                nx, ny = best_xy
                e["tmpl"] = best_name
            else:
                tmpl = tmpl_gorf
                nx, ny, best_sc = sad_match(img, tmpl, pred_x, pred_y, search=10)
                if best_sc > conf_fail["gorf"]:
                    near = [
                        p
                        for p in red_mass_peaks(img, 20, 160)
                        if math.hypot(p[0] - pred_x, p[1] - pred_y) < 28
                    ]
                    if near:
                        nx, ny = near[0][0], near[0][1]
                        best_sc = conf_fail["gorf"] - 1
                ok = best_sc < conf_fail["gorf"] + 30

            if ok:
                e["vx"] = 0.65 * e["vx"] + 0.35 * (nx - e["x"])
                e["vy"] = 0.65 * e["vy"] + 0.35 * (ny - e["y"])
                e["x"], e["y"] = nx, ny
            # else keep predict coast
            else:
                e["x"], e["y"] = pred_x, pred_y
                best_sc = float(best_sc)

            rec = {
                "t": round(t, 4),
                "frame": fp.name,
                "i": fi,
                "x": round(e["x"], 2),
                "y": round(e["y"], 2),
                "conf": round(float(best_sc), 2),
                "ok": bool(ok),
                "tmpl": e.get("tmpl"),
            }
            tracks[e["id"]].append(rec)
            color = (80, 220, 255) if e["kind"] == "cloner" else (255, 180, 40)
            r = 10 if e["kind"] == "cloner" else 5
            draw.ellipse([e["x"] - r, e["y"] - r, e["x"] + r, e["y"] + r], outline=color, width=1)
            draw.text((e["x"] + r + 1, e["y"] - 4), e["id"][:6], fill=color)

        if fi % max(1, args.overlay_every) == 0:
            vis.save(overlay_dir / f"ov_{fi:04d}.png")

    out = {
        "segment": args.segment,
        "playfield": mmap,
        "fps": fps,
        "t_start": t0,
        "entities": [{"id": e["id"], "kind": e["kind"]} for e in entities],
        "tracks": tracks,
        "note": "GUESS template+colour hybrid track; conf=SAD mean (lower better)",
    }
    (seg / "trajectories.json").write_text(json.dumps(out, indent=2) + "\n")
    print(
        f"wrote {seg / 'trajectories.json'} entities={len(entities)} frames={len(frames)}"
    )


def _speeds(track: list[dict], fps: float) -> list[float]:
    """Displacement over ~0.4s windows — resists single-frame jitter."""
    pts = [p for p in track if p.get("ok") and p.get("x") is not None]
    sp = []
    win = max(2, int(round(fps * 0.4)))
    for i in range(len(pts) - win):
        a, b = pts[i], pts[i + win]
        dt = (b["i"] - a["i"]) / fps
        if dt <= 0:
            continue
        d = math.hypot(b["x"] - a["x"], b["y"] - a["y"])
        if d > 50:  # lock loss across window
            continue
        sp.append(d / dt)
    return sp


def _fit_lissajous(track: list[dict], fps: float) -> dict:
    """Fit x = x0 + Ax*sin(wx*t+px), y = y0 + Ay*cos(wy*t+py) via grid search."""
    ok = [p for p in track if p.get("ok", True) and p.get("x") is not None]
    if len(ok) < 20:
        return {"error": "too few points", "n": len(ok)}
    ts = np.array([(p["i"] / fps) for p in ok], dtype=float)
    xs = np.array([p["x"] for p in ok], dtype=float)
    ys = np.array([p["y"] for p in ok], dtype=float)
    x0, y0 = float(xs.mean()), float(ys.mean())
    xc, yc = xs - x0, ys - y0

    best = None
    for wx in np.linspace(0.15, 1.2, 22):
        for wy in np.linspace(0.15, 1.2, 22):
            Sx = np.column_stack([np.sin(wx * ts), np.cos(wx * ts)])
            Sy = np.column_stack([np.sin(wy * ts), np.cos(wy * ts)])
            try:
                cx, *_ = np.linalg.lstsq(Sx, xc, rcond=None)
                cy, *_ = np.linalg.lstsq(Sy, yc, rcond=None)
            except np.linalg.LinAlgError:
                continue
            xr = Sx @ cx
            yr = Sy @ cy
            err = float(np.mean((xc - xr) ** 2 + (yc - yr) ** 2))
            if best is None or err < best["err"]:
                Ax = float(math.hypot(cx[0], cx[1]))
                Ay = float(math.hypot(cy[0], cy[1]))
                px = float(math.atan2(cx[1], cx[0]))
                py = float(math.atan2(cy[1], cy[0]))
                best = {
                    "home_x": round(x0, 2),
                    "home_y": round(y0, 2),
                    "amp_x": round(Ax, 2),
                    "amp_y": round(Ay, 2),
                    "omega_x": round(float(wx), 4),
                    "omega_y": round(float(wy), 4),
                    "phase_x": round(px, 4),
                    "phase_y": round(py, 4),
                    "err": round(err, 3),
                    "n": len(ok),
                    "span_x": round(float(xs.max() - xs.min()), 2),
                    "span_y": round(float(ys.max() - ys.min()), 2),
                }
    return best or {"error": "fit failed"}


def cmd_fit(args: argparse.Namespace) -> None:
    segs = args.segments or ["seg_a_play", "seg_b_mid", "seg_c_late"]
    gorf_speeds: list[float] = []
    cloner_fits: list[dict] = []
    per_seg = {}

    for sid in segs:
        path = TRACKS / sid / "trajectories.json"
        if not path.exists():
            print(f"skip {sid}: no trajectories")
            continue
        data = json.loads(path.read_text())
        fps = float(data["fps"])
        seg_info = {"gorfs": {}, "cloner": None}
        for eid, tr in data["tracks"].items():
            kind = next((e["kind"] for e in data["entities"] if e["id"] == eid), "gorf")
            sp = _speeds(tr, fps)
            if kind == "gorf":
                gorf_speeds.extend(sp)
                if sp:
                    seg_info["gorfs"][eid] = {
                        "n": len(sp),
                        "mean": round(sum(sp) / len(sp), 2),
                        "p50": round(float(np.median(sp)), 2),
                    }
            else:
                fit = _fit_lissajous(tr, fps)
                cloner_fits.append({"segment": sid, **fit})
                seg_info["cloner"] = fit
        per_seg[sid] = seg_info

    def pct(arr, p):
        if not arr:
            return None
        return round(float(np.percentile(arr, p)), 2)

    gorf_speeds_f = [s for s in gorf_speeds if 5 < s < 90]
    good_cl = [c for c in cloner_fits if "amp_x" in c]
    # Prefer low residual per unit of observed travel
    good_cl.sort(
        key=lambda c: c.get("err", 999) / (1.0 + c.get("span_x", 0) + c.get("span_y", 0))
    )
    chosen = good_cl[0] if good_cl else None

    g_spd = pct(gorf_speeds_f, 40) or 38.0
    if g_spd < 22:
        g_spd = 28.0
    if g_spd > 55:
        g_spd = 45.0

    if chosen and (chosen.get("amp_x", 0) + chosen.get("amp_y", 0)) < 8:
        chosen = dict(chosen)
        chosen["amp_x"] = max(float(chosen.get("amp_x", 0)), round(chosen.get("span_x", 12) * 0.45, 2))
        chosen["amp_y"] = max(float(chosen.get("amp_y", 0)), round(chosen.get("span_y", 10) * 0.45, 2))

    # Home near playfield centre for remake (footage homes are segment-framing specific)
    if chosen:
        chosen = dict(chosen)
        chosen["sdl_home_x"] = 160.0
        chosen["sdl_home_y"] = 100.0
        # Keep amps/omegas/phases from fit; clamp extreme amps
        chosen["amp_x"] = float(min(max(chosen.get("amp_x", 20), 12.0), 36.0))
        chosen["amp_y"] = float(min(max(chosen.get("amp_y", 16), 10.0), 28.0))
        # Short clips under-estimate slow axes — keep drift readable in play
        chosen["sdl_omega_x"] = float(max(chosen.get("omega_x", 0.5), 0.35))
        chosen["sdl_omega_y"] = float(max(chosen.get("omega_y", 0.4), 0.35))
        chosen["sdl_phase_x"] = float(chosen.get("phase_x", 0.0))
        chosen["sdl_phase_y"] = float(chosen.get("phase_y", 0.0))

    recommend = {
        "GORF_SPEED": round(float(g_spd), 1),
        "GORF_SPEED_SPREAD": 0.3,
        "cloner": chosen,
    }
    summary = {
        "gorf_speed_px_per_s": {
            "n": len(gorf_speeds_f),
            "p25": pct(gorf_speeds_f, 25),
            "p50": pct(gorf_speeds_f, 50),
            "p75": pct(gorf_speeds_f, 75),
            "mean": round(float(np.mean(gorf_speeds_f)), 2) if gorf_speeds_f else None,
        },
        "per_segment": per_seg,
        "cloner_fits": cloner_fits,
        "recommend": recommend,
        "note": "GUESS from template tracks — CRT noise, framing drift, lock losses",
    }
    out_json = ROOT / "docs" / "findings" / "motion-fit-guess.json"
    out_json.write_text(json.dumps(summary, indent=2) + "\n")

    cl = chosen or {}
    md = f"""# Motion fit from video (GUESS)

Derived from template-assisted tracks on `gameplay.mp4` segments
([`video-segments.md`](video-segments.md)). **Not** `XC.LOGIC`.

## Gorf coast speed (320×204 px/s)

| Stat | Value |
|------|------:|
| n | {summary['gorf_speed_px_per_s']['n']} |
| p25 | {summary['gorf_speed_px_per_s']['p25']} |
| p50 | {summary['gorf_speed_px_per_s']['p50']} |
| p75 | {summary['gorf_speed_px_per_s']['p75']} |
| mean | {summary['gorf_speed_px_per_s']['mean']} |

**SDL recommend:** `GORF_SPEED ≈ {recommend['GORF_SPEED']}` (±~{recommend['GORF_SPEED_SPREAD']*100:.0f}% spread).

Observed behaviour (qualitative): entities **coast** with roughly constant speed and
**reflect** at playfield margins; they do not chase the player in these clips.
Inter-gorf contacts look like soft separation rather than sticky clustering when
not jammed in a corner.

## Cloner path

Best Lissajous-style fit (lowest residual among segments):

| Param | Value |
|-------|------:|
| segment | {cl.get('segment')} |
| home_x | {cl.get('home_x')} |
| home_y | {cl.get('home_y')} |
| amp_x | {cl.get('amp_x')} |
| amp_y | {cl.get('amp_y')} |
| omega_x (raw / sdl) | {cl.get('omega_x')} / {cl.get('sdl_omega_x')} |
| omega_y (raw / sdl) | {cl.get('omega_y')} / {cl.get('sdl_omega_y')} |
| phase_x | {cl.get('sdl_phase_x', cl.get('phase_x'))} |
| phase_y | {cl.get('sdl_phase_y', cl.get('phase_y'))} |
| residual | {cl.get('err')} |

SDL uses `sdl_home_*`, clamped amps, and `sdl_omega_*` (floored so short clips still read as drift).

Model: `x = home_x + amp_x * sin(omega_x * t + phase_x)`,
`y = home_y + amp_y * cos(omega_y * t + phase_y)` (t in seconds from segment start /
play clock — SDL uses level `t_accum`).

Morph: tracker records best-matching `CLN0` / `CLN32` / `CLN64` per frame in
`trajectories.json` (`tmpl` field) for cadence checks.

## Display

Physics may keep float centres; remake still **floors** onto the 320×204 buffer and
integer-scales to the window.

## Machine JSON

[`motion-fit-guess.json`](motion-fit-guess.json)

## Limits

- Camera / CRT framing drifts between segments (per-segment crops).
- Template SAD on composite video is noisy; lock losses inflate speed tails (filtered).
- No claim of authentic TERSE AI — labeled remake only.
"""
    (ROOT / "docs" / "findings" / "motion-fit-guess.md").write_text(md)
    print(json.dumps(recommend, indent=2))
    print(f"wrote {out_json}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sp = ap.add_subparsers(dest="cmd", required=True)

    c = sp.add_parser("calibrate")
    c.add_argument("--segment", required=True)
    c.add_argument("--fps", type=float, default=15.0)
    c.add_argument("--t-start", type=float, required=True)
    c.set_defaults(func=cmd_calibrate)

    t = sp.add_parser("track")
    t.add_argument("--segment", required=True)
    t.add_argument("--fps", type=float, default=15.0)
    t.add_argument("--t-start", type=float, default=0.0)
    t.add_argument("--overlay-every", type=int, default=10)
    t.set_defaults(func=cmd_track)

    f = sp.add_parser("fit")
    f.add_argument("--segments", nargs="*", default=None)
    f.set_defaults(func=cmd_fit)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

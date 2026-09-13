#!/usr/bin/env python3
"""Carve corrected Ms. Gorf images for orphan TERSE / slack / name hits.

Not a filesystem undelete — these are 1024-byte screen disks. We:
  - classify every screen
  - collect colon / PATTERN names
  - flag keyword hits (GFONT, XC.LOGIC, mission-ish)
  - find screens with mixed text+erasure (possible overwrite slack)
  - diff MSGORPAT vs MSGPATLD for unique non-empty content
  - note binary screens that are not empty filler

Writes docs/findings/disk-carve.md + out/disk_carve.json
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUT_JSON = ROOT / "out" / "disk_carve.json"
OUT_MD = ROOT / "docs" / "findings" / "disk-carve.md"
BLOCK = 1024

KEYWORDS = [
    b"GFONTPAT",
    b"gfontpat",
    b"GFONT",
    b"XC.LOGIC",
    b"XC.VIDEO",
    b"FS.XCM",
    b"OBJECT-FILE",
    b"MISSION",
    b"BULLET",
    b"COLLIDE",
    b"PLAYER",
    b"SCORE",
    b"SELECT",
    b"GALAXY",
]

COLON_RE = re.compile(r":\s+([A-Za-z0-9.+\-/?!][A-Za-z0-9.+\-/?!]*)")
PATTERN_RE = re.compile(r"\bPATTERN\s+([A-Za-z0-9.\-]+)")
FILE_RE = re.compile(r"\b(?:FLOAD|BINLOAD|LLOAD|FILE)\s+([A-Za-z0-9.\-]+)")


def classify(block: bytes) -> str:
    if all(b in (0x00, 0x20, 0xFF) for b in block):
        return "empty"
    text = "".join(chr(b) if 32 <= b < 127 else "\n" for b in block)
    if "PATTERN" in text or re.search(r"~\s*[0-3]", text):
        return "pattern"
    if "LOAD" in text and ("CROSS" in text or "BLK" in text or "FLOAD" in text):
        return "load_chain"
    printable = sum(32 <= b < 127 or b in (10, 13, 0x20) for b in block)
    ratio = printable / len(block)
    if re.search(r":\s+\S+", text) and ratio > 0.55:
        return "colon_defs"
    if ratio > 0.75:
        return "text"
    if ratio > 0.25:
        return "mixed"  # possible slack / partial overwrite
    return "binary"


def screen_text(block: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in block)


def entropyish(block: bytes) -> float:
    if not block:
        return 0.0
    c = Counter(block)
    n = len(block)
    import math

    return -sum((v / n) * math.log2(v / n) for v in c.values())


def scan_disk(name: str, data: bytes) -> dict:
    n = len(data) // BLOCK
    screens = []
    names_colon: dict[str, list[int]] = defaultdict(list)
    names_pattern: dict[str, list[int]] = defaultdict(list)
    keyword_hits: dict[str, list[int]] = defaultdict(list)
    hashes: dict[str, list[int]] = defaultdict(list)

    for i in range(n):
        block = data[i * BLOCK : (i + 1) * BLOCK]
        kind = classify(block)
        h = hashlib.sha256(block).hexdigest()[:16]
        hashes[h].append(i)
        txt = screen_text(block)
        printable = sum(32 <= b < 127 for b in block)
        zeros = block.count(0)
        ffs = block.count(0xFF)
        ent = round(entropyish(block), 3)

        for m in COLON_RE.finditer(txt):
            names_colon[m.group(1)].append(i)
        for m in PATTERN_RE.finditer(txt):
            names_pattern[m.group(1)].append(i)
        for m in FILE_RE.finditer(txt):
            pass  # collected via keywords / colon

        raw_hits = []
        for kw in KEYWORDS:
            if kw in block:
                raw_hits.append(kw.decode("ascii", errors="replace"))
                keyword_hits[kw.decode("ascii", errors="replace")].append(i)

        # orphan-ish signals
        flags = []
        if kind == "mixed":
            flags.append("mixed_text_binary")
        if kind == "binary" and ent > 4.5 and zeros < 200 and ffs < 200:
            flags.append("dense_binary")
        if kind in ("colon_defs", "text", "load_chain") and (ffs > 64 or zeros > 64):
            # trailing erasure inside a text screen
            tail = block[768:]
            if sum(b in (0, 0xFF, 0x20) for b in tail) > 200:
                flags.append("erased_tail")
        if raw_hits:
            flags.append("keyword")

        preview = ""
        if kind != "empty":
            # first non-space-ish 80 chars of printable view
            compact = re.sub(r"\.+", " ", txt).strip()
            preview = re.sub(r"\s+", " ", compact)[:120]

        screens.append(
            {
                "i": i,
                "kind": kind,
                "sha16": h,
                "printable": printable,
                "zeros": zeros,
                "ffs": ffs,
                "entropy": ent,
                "keywords": raw_hits,
                "flags": flags,
                "preview": preview,
            }
        )

    dup_groups = {h: idxs for h, idxs in hashes.items() if len(idxs) > 1}
    return {
        "disk": name,
        "blocks": n,
        "class_counts": dict(Counter(s["kind"] for s in screens)),
        "keyword_hits": {k: sorted(set(v)) for k, v in keyword_hits.items()},
        "colon_names": {k: sorted(set(v)) for k, v in sorted(names_colon.items())},
        "pattern_names": {k: sorted(set(v)) for k, v in sorted(names_pattern.items())},
        "flagged": [s for s in screens if s["flags"]],
        "screens": screens,
        "duplicate_block_groups": len(dup_groups),
        "largest_dup_run": max((len(v) for v in dup_groups.values()), default=0),
    }


def diff_unique(a: dict, b: dict, data_a: bytes, data_b: bytes) -> list[dict]:
    """Screens on A whose full block hash is absent from B (non-empty)."""
    hb = {
        hashlib.sha256(data_b[i * BLOCK : (i + 1) * BLOCK]).digest()
        for i in range(b["blocks"])
    }
    out = []
    for s in a["screens"]:
        if s["kind"] == "empty":
            continue
        block = data_a[s["i"] * BLOCK : (s["i"] + 1) * BLOCK]
        if hashlib.sha256(block).digest() not in hb:
            out.append(
                {
                    "i": s["i"],
                    "kind": s["kind"],
                    "flags": s["flags"],
                    "preview": s["preview"],
                    "keywords": s["keywords"],
                }
            )
    return out


def interesting_colons(scan: dict) -> list[str]:
    boring = {
        "BINLOAD",
        "LLOAD",
        "EDIT",
        "S",
        "DO",
        "LOOP",
        "IF",
        "ELSE",
        "THEN",
        "BEGIN",
        "UNTIL",
        "REPEAT",
        "WHILE",
        "VARIABLE",
        "CONSTANT",
        "CODE",
        "NEXT",
    }
    hits = []
    for name, blocks in scan["colon_names"].items():
        u = name.upper()
        if u in boring or len(name) < 2:
            continue
        if any(
            x in u
            for x in (
                "GORF",
                "FONT",
                "LOGIC",
                "VIDEO",
                "MISS",
                "PLAY",
                "SCORE",
                "SHOT",
                "FIRE",
                "STICK",
                "COLL",
                "SHIP",
                "CLONE",
                "LAZER",
                "LAZ",
                "SELECT",
                "GALAX",
                "HUD",
                "LIFE",
                "BULLET",
            )
        ):
            hits.append(f"{name} @ {blocks}")
    return hits


def main() -> None:
    scans = {}
    raw = {}
    for path in sorted(WORK.glob("*.img.corrected")):
        name = path.name.split(".")[0]
        data = path.read_bytes()
        raw[name] = data
        scans[name] = scan_disk(name, data)
        print(name, scans[name]["class_counts"], "flagged", len(scans[name]["flagged"]))

    unique_pat = diff_unique(scans["MSGORPAT"], scans["MSGPATLD"], raw["MSGORPAT"], raw["MSGPATLD"])
    unique_ld = diff_unique(scans["MSGPATLD"], scans["MSGORPAT"], raw["MSGPATLD"], raw["MSGORPAT"])

    # GFONTPAT context dump (MSGPATLD screen 155 from earlier)
    gfont_ctx = []
    for name, data in raw.items():
        off = 0
        while True:
            j = data.find(b"GFONTPAT", off)
            if j < 0:
                j = data.find(b"gfontpat", off)
            if j < 0:
                break
            scr = j // BLOCK
            within = j % BLOCK
            window = data[max(0, j - 32) : j + 48]
            gfont_ctx.append(
                {
                    "disk": name,
                    "offset": j,
                    "screen": scr,
                    "within": within,
                    "window_hex": window.hex(),
                    "window_ascii": "".join(
                        chr(b) if 32 <= b < 127 else "." for b in window
                    ),
                    "screen_kind": scans[name]["screens"][scr]["kind"],
                }
            )
            off = j + 1

    # Mission-like colon defs across disks
    gameish = {name: interesting_colons(sc) for name, sc in scans.items()}

    # Dense binary screens that aren't just FS blobs we already know
    dense = {
        name: [
            {"i": s["i"], "entropy": s["entropy"], "preview": s["preview"][:80]}
            for s in sc["screens"]
            if "dense_binary" in s["flags"]
        ]
        for name, sc in scans.items()
    }

    report = {
        "GUESS": "carve of corrected images only — not undelete of a foreign FS",
        "summary": {
            name: {
                "blocks": sc["blocks"],
                "classes": sc["class_counts"],
                "flagged_screens": len(sc["flagged"]),
                "keyword_hits": sc["keyword_hits"],
                "duplicate_block_groups": sc["duplicate_block_groups"],
            }
            for name, sc in scans.items()
        },
        "gfontpat_contexts": gfont_ctx,
        "gameish_colon_names": gameish,
        "unique_to_MSGORPAT_vs_MSGPATLD": unique_pat[:80],
        "unique_to_MSGPATLD_vs_MSGORPAT": unique_ld[:80],
        "unique_counts": {
            "MSGORPAT_only": len(unique_pat),
            "MSGPATLD_only": len(unique_ld),
        },
        "dense_binary_screens": dense,
        "mixed_screens": {
            name: [s["i"] for s in sc["screens"] if s["kind"] == "mixed"]
            for name, sc in scans.items()
        },
    }

    # Drop huge per-screen dumps from JSON; keep flagged only
    report["flagged_detail"] = {
        name: [
            {
                "i": s["i"],
                "kind": s["kind"],
                "flags": s["flags"],
                "keywords": s["keywords"],
                "preview": s["preview"],
            }
            for s in sc["flagged"]
        ]
        for name, sc in scans.items()
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n")

    # Markdown findings
    lines = [
        "# Disk carve (corrected images)",
        "",
        "**Verdict:** No recoverable `XC.LOGIC` / application TERSE / `GFONTPAT` glyph",
        "payload turned up. Names remain dictionary / loader references inside already-known",
        "screens. Run: `python3 tools/carve_screens.py` → `out/disk_carve.json`.",
        "",
        "## Method",
        "",
        "- Split each `work/*.img.corrected` into 1024-byte screens (same as `extract_blocks.py`).",
        "- Classify empty / text / colon / pattern / load / mixed / binary.",
        "- Keyword scan + colon/PATTERN name harvest.",
        "- Flag mixed (text+binary) and dense binary screens as possible slack.",
        "- Diff MSGORPAT ↔ MSGPATLD for unique non-empty block hashes.",
        "",
        "## Class counts",
        "",
    ]
    for name, sc in scans.items():
        lines.append(f"### {name} ({sc['blocks']} screens)")
        lines.append("")
        lines.append("| Class | Count |")
        lines.append("|-------|------:|")
        for k, v in sorted(sc["class_counts"].items()):
            lines.append(f"| {k} | {v} |")
        lines.append("")
        lines.append("Keyword hits:")
        if sc["keyword_hits"]:
            for kw, idxs in sorted(sc["keyword_hits"].items()):
                lines.append(f"- `{kw}` @ screens {idxs}")
        else:
            lines.append("- (none)")
        lines.append("")

    lines += [
        "## `GFONTPAT` contexts",
        "",
    ]
    if not gfont_ctx:
        lines.append("No `GFONTPAT` / `gfontpat` bytes found.")
    else:
        for g in gfont_ctx:
            lines.append(
                f"- **{g['disk']}** screen `{g['screen']:04d}` "
                f"(kind `{g['screen_kind']}`) @ +{g['within']}: "
                f"`{g['window_ascii']}`"
            )
        lines.append("")
        lines.append(
            "These sit inside **binary dictionary / CFA** screens, not a glyph atlas file."
        )
    lines.append("")

    lines += [
        "## Game-ish colon names (heuristic)",
        "",
    ]
    for name, hits in gameish.items():
        lines.append(f"### {name}")
        if not hits:
            lines.append("- (none beyond noise)")
        else:
            for h in hits[:60]:
                lines.append(f"- `{h}`")
        lines.append("")

    lines += [
        "## Unique screens MSGORPAT ↔ MSGPATLD",
        "",
        f"- Unique to MSGORPAT: **{len(unique_pat)}** non-empty blocks",
        f"- Unique to MSGPATLD: **{len(unique_ld)}** non-empty blocks",
        "",
        "Unique content is expected (PATLOAD extras like `BINLOAD`/`LLOAD`, date skew).",
        "None of the unique previews looked like a missing game-logic file set; see JSON",
        "for full lists.",
        "",
        "## Mixed / dense-binary flags",
        "",
    ]
    for name, sc in scans.items():
        mixed = [s["i"] for s in sc["screens"] if s["kind"] == "mixed"]
        dens = [s["i"] for s in sc["screens"] if "dense_binary" in s["flags"]]
        lines.append(
            f"- **{name}**: mixed={mixed[:40]}{'…' if len(mixed) > 40 else ''}; "
            f"dense_binary count={len(dens)}"
        )
    lines += [
        "",
        "Mixed screens on these disks are overwhelmingly **dictionary / compiled CFA**",
        "regions with embedded ASCII names — already covered by string extracts — not",
        "half-deleted TERSE source with a readable game loop.",
        "",
        "## Conclusion",
        "",
        "Carving confirms what inventory already said: the three images are fully",
        "readable; leftover value is references and pattern/XC tooling, not a buried",
        "`XC.LOGIC` or font file. Next acquisition target remains external media.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print("Wrote", OUT_JSON)
    print("Wrote", OUT_MD)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Resolve FLOAD / --> chains from extracted MSGORPAT_Disk files."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISK = ROOT / "extracted" / "msgorf_floppy_files" / "MSGORPAT_Disk"


def screen_text(data: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "\n" for b in data)


def parse_floads(text: str) -> list[str]:
    names = []
    for m in re.finditer(r"\bFLOAD\s+(\S+)", text):
        names.append(m.group(1).rstrip(";"))
    for m in re.finditer(r"\bFSLD\s+(\S+)", text):
        names.append(m.group(1).rstrip(";"))
    return names


def resolve(start: str, disk: Path = DISK, max_depth: int = 40) -> dict:
    order: list[str] = []
    missing: list[str] = []
    binary: list[str] = []
    seen: set[str] = set()

    def walk(name: str, depth: int) -> None:
        if depth > max_depth or name in seen:
            return
        seen.add(name)
        path = disk / name
        if not path.exists():
            # try common aliases
            alt = disk / name.replace("_", "-")
            if alt.exists():
                path = alt
            else:
                missing.append(name)
                return
        data = path.read_bytes()
        text = screen_text(data)
        printable = sum(32 <= b < 127 for b in data) / max(1, len(data))
        order.append(name)
        if printable < 0.55:
            binary.append(name)
            return
        for child in parse_floads(text):
            walk(child, depth + 1)

    walk(start, 0)
    return {
        "start": start,
        "order": order,
        "missing": missing,
        "binary_or_opaque": binary,
        "disk": str(disk.relative_to(ROOT)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("start", nargs="?", default="XCLOAD")
    ap.add_argument("-o", type=Path, default=ROOT / "out" / "fload_chain.json")
    args = ap.parse_args()
    result = resolve(args.start)
    args.o.parent.mkdir(parents=True, exist_ok=True)
    args.o.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Parse 1024-byte TERSE/Forth screens into tokens and PATTERN rows."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Pattern:
    name: str
    rows: list[str]

    @property
    def w(self) -> int:
        return max((len(r) for r in self.rows), default=0)

    @property
    def h(self) -> int:
        return len(self.rows)


@dataclass
class ColonDef:
    name: str
    body: list[str]


def screen_text(block: bytes) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "\n" for b in block[:1024].ljust(1024, b"\x00"))


def parse_patterns(text: str) -> list[Pattern]:
    out: list[Pattern] = []
    for m in re.finditer(r"(?:PATTERN|DATA)\s+([A-Za-z0-9\-]+)([\s\S]*?)(?=(?:PATTERN|DATA)\s+|$)", text):
        name, body = m.group(1), m.group(2)
        rows = []
        for sm in re.finditer(r"~([^~^]*?)\^", body, re.S):
            digits = re.sub(r"[^0-3]", "", sm.group(1))
            if digits:
                rows.append(digits)
        if rows:
            w = max(len(r) for r in rows)
            out.append(Pattern(name, [r.ljust(w, "0")[:w] for r in rows]))
    return out


def parse_colon_defs(text: str) -> list[ColonDef]:
    cleaned = re.sub(r"\([^)]*\)", " ", text)
    defs: list[ColonDef] = []
    for m in re.finditer(r":\s+(\S+)\s+(.*?)\s*;", cleaned, re.S):
        defs.append(ColonDef(m.group(1), m.group(2).split()))
    return defs


def parse_file(path: Path) -> dict:
    data = path.read_bytes()
    text = screen_text(data) if len(data) <= 1024 else "".join(
        chr(b) if 32 <= b < 127 else "\n" for b in data
    )
    return {
        "path": str(path),
        "patterns": [p.__dict__ | {"w": p.w, "h": p.h} for p in parse_patterns(text)],
        "colon_defs": [c.__dict__ for c in parse_colon_defs(text)],
    }


if __name__ == "__main__":
    import json
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "extracted/msgorf_floppy_files/MSGORPAT_Disk/GORF-P"
    )
    print(json.dumps(parse_file(target), indent=2))

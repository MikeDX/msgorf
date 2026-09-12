#!/usr/bin/env python3
"""Split corrected disk images into 1024-byte TERSE/Forth screens."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUT = ROOT / "extracted" / "screens"
BLOCK = 1024


def classify(block: bytes) -> str:
    if all(b in (0x00, 0x20, 0xFF) for b in block):
        return "empty"
    text = "".join(chr(b) if 32 <= b < 127 else "\n" for b in block)
    if "PATTERN" in text or re.search(r"~\s*[0-3]", text):
        return "pattern"
    if "LOAD" in text and ("CROSS" in text or "BLK" in text):
        return "load_chain"
    if re.search(r":\s+\S+", text) and sum(32 <= b < 127 for b in block) > 200:
        return "colon_defs"
    printable = sum(32 <= b < 127 or b in (10, 13) for b in block)
    if printable / len(block) > 0.75:
        return "text"
    return "binary"


def render_text_screen(block: bytes) -> str:
    """16 lines x 64 chars conventional Forth screen."""
    lines = []
    for i in range(16):
        row = block[i * 64 : (i + 1) * 64]
        lines.append("".join(chr(b) if 32 <= b < 127 else "." for b in row))
    return "\n".join(lines)


def render_hex(block: bytes) -> str:
    lines = []
    for i in range(0, len(block), 16):
        chunk = block[i : i + 16]
        hexpart = " ".join(f"{b:02X}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:04X}: {hexpart:<48} {asc}")
    return "\n".join(lines)


def main() -> None:
    summary = {}
    for path in sorted(WORK.glob("*.img.corrected")):
        disk = path.name.split(".")[0]
        data = path.read_bytes()
        dest = OUT / disk
        dest.mkdir(parents=True, exist_ok=True)
        n = len(data) // BLOCK
        classes = {}
        index_lines = [f"# {disk} screens ({n} x {BLOCK})", ""]
        for i in range(n):
            block = data[i * BLOCK : (i + 1) * BLOCK]
            kind = classify(block)
            classes[kind] = classes.get(kind, 0) + 1
            body = render_text_screen(block)
            if kind == "binary":
                body = render_hex(block)
            (dest / f"{i:04d}.txt").write_text(
                f"{{ BLOCK {i:04d} }} class={kind}\n\n{body}\n"
            )
            index_lines.append(f"- `{i:04d}.txt` — {kind}")
        (dest / "INDEX.md").write_text("\n".join(index_lines) + "\n")
        summary[disk] = {"blocks": n, "classes": classes}
        print(disk, classes)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()

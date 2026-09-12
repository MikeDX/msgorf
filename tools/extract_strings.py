#!/usr/bin/env python3
"""Extract printable strings and keyword hits from corrected disk images."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
OUT = ROOT / "extracted" / "strings"

KEYWORDS = re.compile(
    r"gorf|pattern|terse|sprite|screen|player|robot|ship|mission|"
    r"collision|bullet|laser|quad|stk|load|save|disk|arc-|byte-|"
    r"binload|xcload|pat-load|vger|forth",
    re.I,
)


def strings_from(data: bytes, min_len: int = 5):
    for m in re.finditer(rb"[\x20-\x7e]{" + str(min_len).encode() + rb",}", data):
        yield m.start(), m.group().decode("ascii")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    word_set: set[str] = set()
    for path in sorted(WORK.glob("*.img.corrected")):
        data = path.read_bytes()
        all_path = OUT / f"{path.stem}.all.txt"
        hit_path = OUT / f"{path.stem}.hits.txt"
        lines = []
        hits = []
        for off, s in strings_from(data):
            lines.append(f"{off:06X}: {s}")
            if KEYWORDS.search(s):
                hits.append(f"{off:06X}: {s}")
            for w in re.findall(r"[A-Za-z][A-Za-z0-9.\-]{2,20}", s):
                word_set.add(w)
        all_path.write_text("\n".join(lines) + "\n")
        hit_path.write_text("\n".join(hits) + "\n")
        print(f"{path.name}: {len(lines)} strings, {len(hits)} keyword hits")

    interesting = sorted(
        w
        for w in word_set
        if re.search(
            r"gorf|pat|terse|sprite|player|ship|bullet|laser|quad|load|xc|bin|arc",
            w,
            re.I,
        )
    )
    (OUT / "interesting_words.txt").write_text("\n".join(interesting) + "\n")
    print(f"Wrote {len(interesting)} interesting words")


if __name__ == "__main__":
    main()

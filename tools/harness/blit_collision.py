#!/usr/bin/env python3
"""Minimal framebuffer harness: blit 2-bit patterns with write-overlay collision.

Jamie Fenton: collision by monitoring write-cycle (value written over another).
Here: stamping a non-zero pixel onto a cell that already has a different owner => hit.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = json.loads((ROOT / "play" / "raw_sprites.json").read_text())


@dataclass
class Hit:
    x: int
    y: int
    owner: int
    other: int


class Frame:
    def __init__(self, w: int = 320, h: int = 240):
        self.w, self.h = w, h
        self.pix = bytearray(w * h)  # color 0-3
        self.own = [0] * (w * h)

    def clear(self) -> None:
        self.pix[:] = b"\x00" * (self.w * self.h)
        self.own = [0] * (self.w * self.h)

    def blit(self, rows: list[str], x: int, y: int, owner: int) -> list[Hit]:
        hits: list[Hit] = []
        for j, row in enumerate(rows):
            yy = y + j
            if yy < 0 or yy >= self.h:
                continue
            for i, ch in enumerate(row):
                v = int(ch)
                if not v:
                    continue
                xx = x + i
                if xx < 0 or xx >= self.w:
                    continue
                idx = yy * self.w + xx
                prev = self.own[idx]
                if prev and prev != owner:
                    hits.append(Hit(xx, yy, owner, prev))
                self.pix[idx] = v
                self.own[idx] = owner
        return hits


def main() -> None:
    gorf = RAW["gorf"]["rows"]
    player = RAW["player"]["rows"]
    fr = Frame()
    fr.clear()
    fr.blit(gorf, 100, 100, owner=2)
    h2 = fr.blit(player, 100, 100, owner=1)  # overlap => collisions
    print(f"overlap hits: {len(h2)} (expected >0)")
    fr.clear()
    fr.blit(gorf, 10, 10, 2)
    h3 = fr.blit(player, 200, 200, 1)
    print(f"separate hits: {len(h3)} (expected 0)")
    assert len(h2) > 0 and len(h3) == 0
    print("blit_collision OK")


if __name__ == "__main__":
    main()

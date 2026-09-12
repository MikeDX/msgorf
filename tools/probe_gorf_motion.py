#!/usr/bin/env python3
"""Deprecated yellow-blob probe — use tools/track_video_entities.py instead.

Kept as a pointer so old docs still resolve.
"""
from __future__ import annotations

import sys

print(
    "probe_gorf_motion.py is superseded by tools/track_video_entities.py\n"
    "  calibrate | track | fit\n"
    "See docs/findings/video-segments.md and motion-fit-guess.md",
    file=sys.stderr,
)
sys.exit(2)

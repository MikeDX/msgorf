#!/usr/bin/env python3
"""Package the authentic cross-compiled pattern object as a ROM fragment.

Uses MSGORPAT XC.PATTERNS (and optional FS.PAT) produced historically via XCLOAD.
Pads/places at ROMSTART 0x4000 per the LOAD block. This is NOT a full game ROM,
but it is a real Nutting object we can feed into a future harness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISK = ROOT / "extracted" / "msgorf_floppy_files" / "MSGORPAT_Disk"
OUT = ROOT / "out"
ROMSTART = 0x4000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patterns", type=Path, default=DISK / "XC.PATTERNS")
    ap.add_argument("--fs-pat", type=Path, default=DISK / "FS.PAT")
    ap.add_argument("-o", type=Path, default=OUT / "msgorf_patterns_at_4000.bin")
    args = ap.parse_args()

    patterns = args.patterns.read_bytes()
    # Place at 0x4000 in a 64K image; leave rest as 0xFF (erased EPROM look)
    image = bytearray([0xFF] * 0x10000)
    end = ROMSTART + len(patterns)
    if end > 0x10000:
        raise SystemExit(f"patterns too large: {len(patterns)}")
    image[ROMSTART:end] = patterns

    # Optional: append FS.PAT metadata note only in sidecar JSON (file is huge/system)
    report = {
        "note": "Authentic XC.PATTERNS placed at ROMSTART 0x4000 from MsGorf floppy extract",
        "romstart": hex(ROMSTART),
        "patterns_file": str(args.patterns.relative_to(ROOT)),
        "patterns_size": len(patterns),
        "patterns_sha256": hashlib.sha256(patterns).hexdigest(),
        "image_size": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "output": str(args.o.relative_to(ROOT)),
        "not_a_full_game": True,
        "next": "Need application/XC.LOGIC sources + dual-Z80 harness",
    }
    if args.fs_pat.exists():
        report["fs_pat_size"] = args.fs_pat.stat().st_size
        report["fs_pat_sha256"] = hashlib.sha256(args.fs_pat.read_bytes()).hexdigest()

    args.o.parent.mkdir(parents=True, exist_ok=True)
    args.o.write_bytes(image)
    (OUT / "msgorf_patterns_rom_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

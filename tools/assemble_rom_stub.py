#!/usr/bin/env python3
"""Phase 7 stub: refuse full ROM build until completeness gate passes."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "findings" / "source-completeness.md"
OUT = ROOT / "out"


def main() -> int:
    gate = GATE.read_text(errors="replace")
    blocked = "PARTIAL" in gate or "not enough" in gate.lower()
    report = {
        "action": "assemble_rom_stub",
        "blocked": blocked,
        "gate_doc": str(GATE.relative_to(ROOT)),
        "message": (
            "Full Ms. Gorf ROM assembly blocked: source set is pattern/tooling only. "
            "See out/ROM_STATUS.md and docs/findings/source-completeness.md."
        ),
        "available_artifacts": sorted(
            str(p.relative_to(ROOT)) for p in OUT.iterdir() if p.is_file()
        ),
    }
    (OUT / "assemble_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 2 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())

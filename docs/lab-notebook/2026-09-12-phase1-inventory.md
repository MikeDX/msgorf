# 2026-09-12 — Phase 1 inventory

## Actions

1. Implemented `tools/normalize_img.py`; confirmed `.img` XOR `0xFF` == `.inv` trimmed.
2. Wrote `docs/inventory/disks.md` and `work/normalize_report.json`.
3. Downloaded Bitsavers `MSGORF.zip` (browser UA); local images **identical**.
4. Ran `tools/extract_strings.py`.
5. Wrote `docs/findings/source-completeness.md` — verdict **PARTIAL**.

## Results

- MSGORF: 162 × 1024 screens, pattern-centric.
- MSGORPAT/MSGPATLD: TERSE + XC LOAD block at screen 0086.

# Notes from professionalmagic.com/gorf

Source: [GORF — Matthew Garrett](https://www.professionalmagic.com/gorf) (collected 2026-09-12). Host is a Gorf collector/magician page with Ms. Gorf recovery notes, not Nutting primary docs. Cross-check against disks / Bitsavers.

## Ms. Gorf facts useful to this lab

- Programmed in **Nutting TERSE 78** (Forth-like with Nutting extensions); original Gorf was Forth.
- Jamie showed it on a **development system** in *Before The Bubble Burst*; unfinished after the 1983 crash.
- Disks recovered via museum with Jamie’s permission; Tim’s split is Bitsavers `MsGorf_floppy_files.zip` (already in this repo).
- **Patterns and game code were separate disks** — matches our finding that `XC.LOGIC` / application logic is absent from the pattern floppies.
- Hardware change near cancellation; Jamie: collision detection by **monitoring the write-cycle** (write one value over another → collision). Other details she no longer recalls.
- Prototype panel: **two joysticks** (observer likens feel to Robotron + Star Castle). **Not** a Gorf mission clone with the same five-level structure.
- One image reportedly needs reread: label **Ms Gorf – GORF4A** (Dysan #802067) — our `MSGORF/` set.
- Geometry note on the page: 5¼″ media imaged with IceBox-like **8″ geometry** (2 heads × 77 tracks × 2 × 1024 ≈ 308K).

## Linked TERSE / IceBox PDFs (Jamie → Matthew Garrett)

Hosted at `https://www.professionalmagic.com/s/…`. Local copies + notes: **`docs/references/jamie_fenton_via_garrett/`**.

| Link text | File | Notes |
|-----------|------|-------|
| TERSE VOCAB | `TERSE_VOCAB.pdf` | TERSE Standard Glossary 9/21/81 |
| TERSE MISC 6 | `MISC6.pdf` | Actually **ICE Monitor Commands** (new vs our Bitsavers set) |
| ICE5 | `ICE5.pdf` | DNA ICE hardware |
| GAS MONITOR | `GAS_MONITOR4.pdf` | GAS Monitor 2.33 |
| EDIT VOCAB | `EDIT_VOCAB2.pdf` | EDIT 81 Glossary |
| ASSEMBLER | `ASSEMBLER3.pdf` | **Mislabelled** — EDIT 81 content, not assembler; use `terse/Z80_Asm.pdf` |

Overlapping Bitsavers scans (different filesize/hash): `docs/references/icebox/`.

## Image gallery on the page

Squarespace grid (`ms gorf 1` … `ms gorf 6`). Local mirror: [`garrett_ms_gorf_gallery/`](garrett_ms_gorf_gallery/).

- **Direct gameplay stills:** `ms_gorf_1`, `ms_gorf_6`, `ms_gorf_2` (and related root `msgorf_screenshot.jpg`)
- **Wiki phone captures** that also show game frames: `ms_gorf_3`, `ms_gorf_4`, `ms_gorf_5`

## What this does *not* authorize

- Inventing missions, dual-stick play, speech, or a “Gorf II” redesign (the page’s speculative sequel section is opinion, not Ms. Gorf source).
- Treating the SDL atlas / `--probe` keyboard as cabinet controls.
- Treating gallery photos as substitutes for disk `PATTERN` art (`extracted/patterns/`).

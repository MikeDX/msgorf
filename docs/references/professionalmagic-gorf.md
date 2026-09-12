# Notes from professionalmagic.com/gorf

Source: [GORF — Matthew Garrett](https://www.professionalmagic.com/gorf) (collected 2026-09-12). Host is a Gorf collector/magician page with Ms. Gorf recovery notes, not Nutting primary docs. Cross-check against disks / Bitsavers.

## Ms. Gorf facts useful to this lab

- Programmed in **Nutting TERSE 78** (Forth-like with Nutting extensions); original Gorf was Forth.
- Jamie showed it on a **development system** in *Before The Bubble Burst*; unfinished after the 1983 crash.
- Disks recovered via museum with Jamie’s permission; Tim’s split is Bitsavers `MsGorf_floppy_files.zip` (already in this repo).
- **Patterns and game code were separate disks** — “load all of the patterns from one disk, then the game code from another.” Matches our finding that `XC.LOGIC` / application logic is absent from the pattern floppies. There was **no single disk with the whole game**.
- **Mix of 8″ and 5¼″** media is called out as a recovery problem; the page suggests the 5¼″ set may come from different Astrocade/Zgrass-related hardware while keeping IceBox-like geometry.
- Hardware change near cancellation; Jamie (quoted on the page): collision detection by **monitoring the write-cycle** (write one value over another → collision). Other details she no longer recalls.
- Prototype panel: **two joysticks** (observer likens feel to Robotron + Star Castle). **Not** a Gorf mission clone with the same five-level structure.

## Floppy format / GORF4A redump (from the page)

- One disk **needs to be reread**: labelled **Ms Gorf – GORF4A**, Dysan **#802067** — our `MSGORF/` set (Tim’s Readme also: reread of the third floppy).
- Physical media look like **5¼″**, but image geometry matches **Terse 8″** layout: **2 heads × 77 tracks × 2 sectors × 1024 bytes ≈ 308K**.
- Hypothesis on the page: **FD1771** on a later IceBox with an **80-track 5¼″** drive, still using the 8″ format.
- (Our lab also notes FD1771 / bit-inverted sectors in IceBox docs — see `docs/findings/icebox-notes.md`, MAME `icebox.cpp`.)

## People named on the page

| Person | Role (as stated there) |
|--------|-------------------------|
| **Tim Giddens** | Main person who knows how; file split on Bitsavers; other projects first |
| **Brendon Parker** | Interested; graphics designer, not programmer |
| **Frank Palazzolo** | Computer Museum contact; MAME boot of a disk with **Gorf** binary; had disassembled / figured out how TERSE worked; had not looked at Ms. Gorf material for ~a year when quoted |
| **Matthew Garrett** | Page author; museum retrieval with Jamie’s permission; `info@professionalmagic.com` |

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

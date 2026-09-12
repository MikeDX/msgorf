# Documentation index

Start at the root [`README.md`](../README.md) for status, gallery, and quick start. This page indexes everything under `docs/`.

## Read first

| Doc | Why |
|-----|-----|
| [`findings/goals.md`](findings/goals.md) | Primary goal (ROM) vs pattern lab vs remake rules |
| [`findings/source-completeness.md`](findings/source-completeness.md) | What these disks can / cannot build |
| [`findings/missing-files-hunt.md`](findings/missing-files-hunt.md) | **Blocker:** no `XC.LOGIC` / app TERSE in public dumps |
| [`findings/missing-files-outreach.md`](findings/missing-files-outreach.md) | Draft emails (museum / Garrett / Jamie) |
| [`architecture/terse-toolchain.md`](architecture/terse-toolchain.md) | Python → C/SDL → ROM pipeline |

## Findings (`findings/`)

| Doc | Topic |
|-----|--------|
| [`source-extraction-status.md`](findings/source-extraction-status.md) | Present vs absent artifacts |
| [`xc-logic.md`](findings/xc-logic.md) | What `XC.LOGIC` is (`BINLOAD` target) |
| [`xc-patterns-format.md`](findings/xc-patterns-format.md) | Decoded simple pattern records in `XC.PATTERNS` |
| [`cross-compile-pipeline.md`](findings/cross-compile-pipeline.md) | `XCLOAD` → `XC.PATTERNS` only |
| [`display.md`](findings/display.md) | Resolution candidates; VCR “PLAY” overlay |
| [`hardware-model.md`](findings/hardware-model.md) | Dual-Z80 / ROM map contract |
| [`dictionary-model.md`](findings/dictionary-model.md) | Name fields / CFA notes |
| [`pattern-format.md`](findings/pattern-format.md) | Source `PATTERN` / `~` `^` art |
| [`terse-to-z80.md`](findings/terse-to-z80.md) | Codegen open questions |
| [`icebox-notes.md`](findings/icebox-notes.md) | IceBox development system |
| [`next-phase-plan.md`](findings/next-phase-plan.md) | Earlier phase roadmap |
| [`reconstruction-stubs.md`](findings/reconstruction-stubs.md) | Policy for labeled guesses |

## Inventory (`inventory/`)

| Doc | Topic |
|-----|--------|
| [`disks.md`](inventory/disks.md) | MSGORF / MSGORPAT / MSGPATLD |
| [`msgorf-floppy-files.md`](inventory/msgorf-floppy-files.md) | Tim’s zip layout |
| [`content-skim.md`](inventory/content-skim.md) | Early content skim |
| [`bitsavers-compare.md`](inventory/bitsavers-compare.md) | Local vs Bitsavers |

## Architecture (`architecture/`)

| Doc | Topic |
|-----|--------|
| [`terse-toolchain.md`](architecture/terse-toolchain.md) | Build/run commands, stages, non-goals |

## References (`references/`)

| Doc / folder | Topic |
|--------------|--------|
| [`SOURCES.md`](references/SOURCES.md) | Hashes of local reference blobs |
| [`professionalmagic-gorf.md`](references/professionalmagic-gorf.md) | Notes from Garrett’s Gorf page |
| [`jamie_fenton_via_garrett/`](references/jamie_fenton_via_garrett/) | Jamie’s TERSE/Ice PDFs (mirrored) |
| [`mame/icebox.cpp`](references/mame/icebox.cpp) | MAME IceBox skeleton |
| `icebox/`, `terse/`, `gorf/`, `bits/` | Manuals and upstream zips |

## Lab notebook (`lab-notebook/`)

Dated session notes (newest first by topic):

| Entry | Topic |
|-------|--------|
| [`2026-09-12-jamie-manuals.md`](lab-notebook/2026-09-12-jamie-manuals.md) | Garrett PDF mirror |
| [`2026-09-12-missing-files-hunt.md`](lab-notebook/2026-09-12-missing-files-hunt.md) | Logic-disk hunt |
| [`2026-09-12-harness-faithfulness.md`](lab-notebook/2026-09-12-harness-faithfulness.md) | SDL validator ≠ game |
| [`2026-09-12-sdl-runtime.md`](lab-notebook/2026-09-12-sdl-runtime.md) | Runtime milestones |
| [`2026-09-12-source-faithfulness.md`](lab-notebook/2026-09-12-source-faithfulness.md) | Faithfulness reset |
| [`2026-09-12-breakthrough-floppy-files.md`](lab-notebook/2026-09-12-breakthrough-floppy-files.md) | Tim extract |
| Older `2026-09-12-phase*.md` | Phased inventory / extract / MVP |

## Related trees outside `docs/`

| Path | Role |
|------|------|
| [`references/garrett_ms_gorf_gallery/`](references/garrett_ms_gorf_gallery/) | Garrett gameplay stills |
| [`../play/`](../play/index.html) | Pattern lab |
| [`../extracted/patterns/`](../extracted/patterns/) | PNG exports |
| [`../out/README.md`](../out/README.md) | Build products |
| [`../tools/terse/runtime/README.md`](../tools/terse/runtime/README.md) | SDL validator |
| [`../reconstructed/`](../reconstructed/) | Guesses only |

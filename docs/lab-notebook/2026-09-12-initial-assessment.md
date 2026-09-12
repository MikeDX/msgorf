# 2026-09-12 — Initial assessment

## Context

Workspace contains imaged 5.25" Dysan floppies labeled as Ms. Gorf development material (Jamie Fenton / Midway / Dave Nutting Associates). Goal: long-term path to a compiled arcade ROM.

## Files observed

### MSGORF/

- `MSGORF.jpg` — disk label: “Ms. Gorf - GORF4A”, Dysan 204/2D, soft sectored 96/100 TPI
- `msgorf.scp` — SuperCard Pro flux dump
- `msgorf_scp.img` — decoded image, 165888 bytes (= 162 × 1024)
- `msgorf.inv` — bit-inverted copy (+1 padding byte)
- `msgorf.txt` — hex+ASCII block dump; block 0001 defines `PATTERN GORF4A` / `QUADPAT`

### MSGORPAT/

- Label: “Ms. Gorf Pattern Disk”
- `MSGORPAT.IMD` — ImageDisk (IMD 1.18, dated 30/08/2018)
- `MSGORPAT_IMD.img` — 315392 bytes; **bit-inverted** vs readable content
- `MSGORPAT_IMD.img.inv` — correct polarity (XOR 0xFF of `.img`)

### MSGPATLD/

- Label: “PATLOAD / MS GORF / 5/17/83”
- Same geometry as MSGORPAT (315392-byte `.img`, inverted polarity)
- Differs from MSGORPAT (~111k differing bytes)

### Other

- `msgorf_screenshot.jpg` — CGE-era demo photo of prototype gameplay

## Technical findings

1. **Polarity:** `.img` XOR `.inv` == `0xFF` for all compared bytes. Readable ASCII (`TERSE`, `LIT`, `PATTERN`, `GORF4A`) appears only after inversion.
2. **Language:** TERSE kernel present on pattern disks (`Terse 1.0 July 82` string fragment; `ARC-TERSE`, `BYTE-TERSE`).
3. **Game-ish vocabulary:** `BULLETS`, `PLAYER`, `SHIPS`, `LASER`, `GORF-PAT`, `QUADPAT`, `PAT-LOAD`.
4. **Cross-compile hints:** `XCLOAD`, `BINLOAD`, `( LOAD BLK FOR CROSS-COMPILING )`.
5. **MSGORF content:** 163 named blocks in `msgorf.txt` (0000–0162); only block 0001 has substantial ASCII headers; pattern rows are hex-digit art (`~` … `^`) with digits 0–3.
6. **Completeness suspicion:** local set looks like pattern tooling, not a full Ms. Gorf application source tree. Confirm vs Bitsavers `MSGORF.zip` in Phase 1.

## External context (not yet mirrored)

- Bitsavers: https://bitsavers.org/bits/Nutting_Assoc/MSGORF.zip
- Bitsavers TERSE PDFs: https://bitsavers.org/pdf/nuttingAssoc/terse/
- ICE box docs: https://bitsavers.org/pdf/nuttingAssoc/icebox/
- Jamie Fenton: hardware config changed near cancel; write-cycle collision detection.

## Decisions

- Never modify originals under `MSGORF/`, `MSGORPAT/`, `MSGPATLD/`.
- All derived work under `work/`, `extracted/`, `out/`, `docs/`.
- Completeness gate before investing in full ROM assembly.

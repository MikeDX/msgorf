# Missing-files hunt (2026-09-12)

## Verdict

**`XC.LOGIC` / Jamie’s application TERSE is not in any public Bitsavers dump we have.**  
What shipped online is the **pattern toolchain** (plus one extra pattern disk and Robby Roto as unrelated Rosetta). The game-code disks were always described as **separate**, often **8″**, and are still with the museum / not imaged into `MSGORF.zip`.

## What we have (labels from photos)

| Image set | Handwritten label | Content |
|-----------|-------------------|---------|
| `MSGORPAT` | Ms. Gorf — **Pattern Disk** | TERSE pattern tools, `XC.PATTERNS`, INDEX/ANIM-MAP |
| `MSGPATLD` | **PATLOAD** MS GORF 5/17/83 | Overlapping pattern-load tree |
| `MSGORF` | Ms. Gorf — **GORF4A** | Single large `PATTERN GORF4A` only |

Tim’s `MsGorf_floppy_files.zip` Readme: *“files from the two MsGorf floppy disk (still need a reread of the third)”* — i.e. pattern pair + GORF4A, **not** a logic disk.

## Named but absent objects (from these disks)

| Name | Evidence | Role |
|------|----------|------|
| **`XC.LOGIC`** | `BINLOAD` / `LLOAD` screens; dictionary name field | Cross-compiled **game binary** artists load |
| **`XC.VIDEO`** | Dictionary / screen fragment `XC.VIDEOO … BMOVE` | Companion video/object file (pairing with logic in `DPATCH` notes) |
| **`FS.XCM`** | Dictionary near `FS.XC` / `FS.PAT` | Unknown FS variant; no file on disk |
| Jamie/Jay **application screens** | `INSTRUCTIONS`: artists maintain patterns; *“INDEX … which Jay maintains”* / Jay’s program | Actual missions, sticks, collision use — **not** on pattern disks |

False positives from loaders: `FLOAD BLK`, `FLOAD THIS`, etc. are TERSE words, not missing files.

## Public archives checked (nothing new)

| Location | Ms. Gorf-related contents |
|----------|---------------------------|
| `bitsavers.org/bits/Nutting_Assoc/` | `MSGORF.zip`, `Nutting_ICE.zip` only |
| `…/icebox/floppies/` | `MsGorf_floppy_files.zip` (+ unrelated `128b/`) |
| Archive.org advanced search | No extra `XC.LOGIC` / Ms Gorf logic dump |
| Local tree / corrected images | `XC.LOGIC` string = **filename references only**, never a file payload |

## Where the missing media likely still is

1. **Museum holding** of Jamie’s donated box (forum: Computer Museum / Strong–ICHEG orbit; Matthew Garrett: contacted museum → got the three 5¼″ images now on Bitsavers).
2. **Separate 8″ set** Jamie described historically (“source code is on 8″ floppy”; Wikipedia cites labels **“RIP Ms. GORF 6/82 – 8/83”** — those labels do **not** match our three Dysan 5¼″ photos).
3. **People who already touched the dumps:** Tim Giddens (file split), Frank Palazzolo (IceBox/MAME boot experiments), contact via **Matthew Garrett** (`info@professionalmagic.com` / arcade-museum thread offer to introduce workers).

## Acquisition checklist (human, not code)

1. Email museum archives (Strong / ICHEG / whichever curator handled the 2018–19 dump): ask for **catalog of all Ms. Gorf / Fenton / Nutting floppies**, especially any **8″** or labels containing **LOGIC / RIP / XC / Jay**.
2. Email **Matthew Garrett** — request intro to Tim/Frank and status of **GORF4A redump** + whether any logic disks were ever imaged but not posted.
3. Ask Jamie (if appropriate) whether application sources were in the donated box or remain elsewhere; permission already given once for museum release.
4. If new images appear: normalize polarity, run `fload_chain` / string hunt for `:` defs beyond patterns, package any `XC.LOGIC` beside `out/msgorf_patterns_at_4000.bin`.

## What will *not* find it

- Deeper parse of MSGORPAT/MSGPATLD (pattern FLOAD tree is already complete, `missing: []`).
- Inventing gameplay in the SDL validator.
- Treating ROTO (Robby Roto) sources as Ms. Gorf logic.

## Related docs

- `docs/findings/xc-logic.md` — what `XC.LOGIC` is
- `docs/findings/source-extraction-status.md`
- `docs/references/professionalmagic-gorf.md`
- `extracted/msgorf_floppy_files/Readme.txt`

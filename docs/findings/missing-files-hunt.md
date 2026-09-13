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
- Screen/slack **carve** of the corrected images ([`disk-carve.md`](disk-carve.md)) — ran; still
  only name references (`GFONTPAT` in CFA beside `PATSTART`/`PATEND`, `XC.LOGIC` in loaders).
- Inventing gameplay in the SDL validator.
- Treating ROTO (Robby Roto) sources as Ms. Gorf logic.

## Is this a dead end without `XC.LOGIC`?

**For a faithful Ms. Gorf game/ROM from the media we have: yes — blocked.**  
**For the lab (patterns, XC decode, TERSE toolchain, IceBox RE): no.**

### Important distinction

`XC.LOGIC` is the **cross-compile output filename** (what `BINLOAD` / `LLOAD` load), analogous to `game.bin` — not a magic unique format.

You could recover the game either as:

1. A dumped **`XC.LOGIC` binary**, or  
2. The **application TERSE screens** that an XCLOAD-like block would compile with `OBJECT-FILE XC.LOGIC` (then save via `XCFSYSAVE`).

We have **neither**. On these floppies, `XCLOAD` only builds **`XC.PATTERNS`**:

```text
OBJECT-FILE XC.PATTERNS
FLOAD CODE-LOAD   → PATTERN, ANIM-VERBS, INIT-AT
FLOAD INDEX / PAT-LOAD / ANIM-MAP
XCFSYSAVE FS.PAT
```

`CODE-LOAD` is pattern infrastructure only. `FS.XC` is the **cross-compile system** file set (~42 screens); real colon defs there are essentially **`BULLETS` / `ENDBULL` stubs**, not missions. `INSTRUCTIONS` say artists own patterns; **Jay’s program** (application) is separate and not on the Pattern/PATLOAD disks.

### Could other TERSE “generate” the game?

| Candidate | Verdict |
|-----------|---------|
| Re-run XCLOAD on what we have | Produces patterns object only — already have `XC.PATTERNS` |
| Dictionary name `XC.LOGIC` | Filename token in the kernel/dict — **not** the game image |
| Gorf `GORFOS` / ROTO sources | Different games — Rosetta for verbs/hardware, **not** Ms. Gorf logic |
| Invent missions in C/SDL | Possible as a **labeled remake**; not faithful compile |

So nothing “built elsewhere” on *these* disks quietly is `XC.LOGIC`. The pipeline *could* emit it from other screens — those screens were never in the public dump.

### What still moves the needle without the file

- Museum/8″ acquisition (see outreach drafts)
- Deeper TERSE/IceBox/CFA RE (needed even *with* logic disks)
- Documented behavior from Jamie’s prototype video (constraints only, not source)
- Explicit reconstruction module outside `play/` if you choose remake — separate from “compiled from disk”

## Related docs

- `docs/findings/xc-logic.md` — what `XC.LOGIC` is
- `docs/findings/source-extraction-status.md`
- `docs/references/professionalmagic-gorf.md`
- `extracted/msgorf_floppy_files/Readme.txt`

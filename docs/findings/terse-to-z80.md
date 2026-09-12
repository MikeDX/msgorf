# TERSE → Z80 model (working notes)

## What TERSE is

Nutting Associates in-house language (**Terse Efficient Recursive Stack Engine**), Forth-like, used for Bally/Midway coin-op titles (Gorf, Robby Roto, etc.). Alan McNeil authored the engine; Jamie Fenton extended graphics/I/O (see mirrored `Addin_Mar1979.pdf`, glossaries).

Rickey Spiece (DNA): once the Z80 engine is understood, most of the game is TERSE threaded code — a TERSE-aware disassembler helps more than raw Z80 alone (`docs/references/terse/Discussion_with_Rickey_Spiece.txt`).

## On these disks

Corrected MSGORPAT begins with a classic Forth/TERSE dictionary: `LIT`, `BLIT`, `DUP`, `DROP`, `SWAP`, `DO`/`LOOP`, disk words, then higher layers including `TERSE`, editor, and pattern/XC words.

Compilation model (Forth-family, pending confirmation against glossary):

1. **Text screens** (1024-byte blocks, 16×64) edited on IceBox.
2. **Colon definitions** (`: NAME ... ;`) compile to dictionary entries with code field + parameter field.
3. **Primitives** (`LIT`, arithmetic, ports) are Z80 machine code.
4. **Cross-compile mode** (`ARC-TERSE` / `BYTE-TERSE` / `XC*`) retargets DP/ROMSTART toward arcade address map and emits object files (`XCFSYSAVE`).

## Rosetta: shipping Gorf

Public Gorf ROMs (MAME) remain the best binary oracle for “what compiled Nutting games look like.” Plan:

1. Locate threaded-code / CFA-like structures in Gorf ROM.
2. Match dictionary name styles against TERSE glossaries.
3. Compare calling conventions to primitives on MSGORPAT kernel.

`docs/references/gorf/` holds OS/manual text extracts (`GORFOS.txt`, etc.) for hardware context — not a substitute for ROM disassembly (ROMs are not redistributed in this tree).

## Status

We can **describe** the pipeline and **host-compile trivial colon defs** symbolically (Phase 5 MVP). We cannot yet emit Gorf-identical Z80 threaded code without deeper dictionary header reverse engineering against the glossaries and Gorf ROM.

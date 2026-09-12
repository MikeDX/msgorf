# Cross-compile pipeline (from disk evidence)

## Primary evidence

MSGORPAT / MSGPATLD screen **0086** (`extracted/screens/MSGORPAT/0086.txt`):

```text
( LOAD BLK FOR CROSS-COMPILING ) DECIMAL
FSLD FS.XC
xcsys xc ASM .OPS
MORE-BUFFERS
17 <DRIVE OBJECT-FILE XC.PATTERNS DRIVE>
HEX 4000 ROMSTART !  0F000 PSTACK !
   0F800 RAMSTART !  0F400 RSTACK !
XCBEG DECIMAL xcsys xc ASM .OPS
{ V= AT-HERE } { V= PT-HERE } HEX 04200 PT-HERE !
4000 C= ATBL 8040 DP ! DECIMAL
FLOAD CODE-LOAD
FLOAD INDEX
FLOAD PAT-LOAD
FLOAD ANIM-MAP
EX DED DESTROY FS.PAT xcsys XCFSYSAVE FS.PAT
DECIMAL ;S
```

## Interpreted steps

1. Load cross-compile support file set `FS.XC` / `xcsys` / assembler ops.
2. Select drive 17 object file name `XC.PATTERNS`.
3. Set target bases:
   - `ROMSTART = 0x4000`
   - `PSTACK = 0xF000`
   - `RAMSTART = 0xF800`
   - `RSTACK = 0xF400`
   - `PT-HERE = 0x4200` (pattern heap?)
   - `DP = 0x8040` after `ATBL` at 0x4000
4. `FLOAD` modules: `CODE-LOAD`, `INDEX`, `PAT-LOAD`, `ANIM-MAP`.
5. Save with `XCFSYSAVE FS.PAT`.

Related vocabulary on disks: `ARC-TERSE`, `BYTE-TERSE`, `XCLOAD`, `BINLOAD`, `XCFSYSAVE`, `XC.PATTERNS`.

## Implication for ROM work

The surviving disks implement (or host) **pattern object cross-compilation** into a file aimed at ROM base `0x4000`, not a turnkey “build Ms. Gorf.rom” script. Full game compile would chain additional application LOAD blocks that are **not** present here (see `source-completeness.md`).

## Host MVP mapping

`tools/terse/mvp_compile.py` uses the published bases as documentation constants when emitting a placeholder object header for experiments.

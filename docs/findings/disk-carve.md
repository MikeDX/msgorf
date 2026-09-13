# Disk carve (corrected images)

**Verdict:** No recoverable `XC.LOGIC` / application TERSE / `GFONTPAT` glyph
payload turned up. Names remain dictionary / loader references inside already-known
screens. Run: `python3 tools/carve_screens.py` → `out/disk_carve.json`.

## Method

- Split each `work/*.img.corrected` into 1024-byte screens (same as `extract_blocks.py`).
- Classify empty / text / colon / pattern / load / mixed / binary.
- Keyword scan + colon/PATTERN name harvest.
- Flag mixed (text+binary) and dense binary screens as possible slack.
- Diff MSGORPAT ↔ MSGPATLD for unique non-empty block hashes.

## Class counts

### MSGORF (162 screens)

| Class | Count |
|-------|------:|
| pattern | 9 |
| text | 153 |

Keyword hits:
- (none)

### MSGORPAT (308 screens)

| Class | Count |
|-------|------:|
| binary | 44 |
| colon_defs | 13 |
| empty | 16 |
| load_chain | 8 |
| mixed | 73 |
| pattern | 109 |
| text | 45 |

Keyword hits:
- `BULLET` @ screens [10, 45, 88]
- `FS.XCM` @ screens [87]
- `OBJECT-FILE` @ screens [58, 86, 105]
- `PLAYER` @ screens [193, 200, 201, 244]
- `SCORE` @ screens [193]
- `XC.LOGIC` @ screens [87]
- `XC.VIDEO` @ screens [172]

### MSGPATLD (308 screens)

| Class | Count |
|-------|------:|
| binary | 39 |
| colon_defs | 15 |
| empty | 24 |
| load_chain | 6 |
| mixed | 72 |
| pattern | 59 |
| text | 93 |

Keyword hits:
- `BULLET` @ screens [10, 45]
- `GFONT` @ screens [155]
- `GFONTPAT` @ screens [155]
- `OBJECT-FILE` @ screens [58, 76, 86]
- `PLAYER` @ screens [200, 201, 244]
- `XC.LOGIC` @ screens [90, 175]
- `XC.VIDEO` @ screens [172]
- `gfontpat` @ screens [155]

## `GFONTPAT` contexts

- **MSGPATLD** screen `0155` (kind `mixed`) @ +400: `.. ..R......... .. ....V...../..GFONTPAT...|..[..PATSTART.f.....C.*......PATEND.`

These sit inside **binary dictionary / CFA** screens (same neighborhood as `PATSTART` /
`PATEND` / `CHAR1TAB`), not a glyph atlas file.

## Game-ish colon names (heuristic)

### MSGORF
- (none beyond noise)

### MSGORPAT
- `BULLETS @ [10, 45, 88]`
- `GORF-PAT @ [151]`

### MSGPATLD
- `BULLETS @ [10, 45]`

## Unique screens MSGORPAT ↔ MSGPATLD

- Unique to MSGORPAT: **113** non-empty blocks
- Unique to MSGPATLD: **66** non-empty blocks

Unique content is expected (PATLOAD extras like `BINLOAD`/`LLOAD`, date skew).
None of the unique previews looked like a missing game-logic file set; see JSON
for full lists.

## Mixed / dense-binary flags

- **MSGORF**: mixed=[]; dense_binary count=0
- **MSGORPAT**: mixed=[0, 1, 2, 3, 4, 6, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 46, 47, 48, 49, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 74, 75, 76]…; dense_binary count=2
- **MSGPATLD**: mixed=[0, 1, 2, 3, 4, 6, 12, 13, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 46, 47, 48, 49, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 64, 65, 66]…; dense_binary count=2

Mixed screens on these disks are overwhelmingly **dictionary / compiled CFA**
regions with embedded ASCII names — already covered by string extracts — not
half-deleted TERSE source with a readable game loop.

## Conclusion

Carving confirms what inventory already said: the three images are fully
readable; leftover value is references and pattern/XC tooling, not a buried
`XC.LOGIC` or font file. Next acquisition target remains external media.

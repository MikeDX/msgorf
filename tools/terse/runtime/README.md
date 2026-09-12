# C runtime — pattern validator

Validates **authentic** decode/blit only. **Not** Ms. Gorf gameplay.

```bash
make -C tools/terse/runtime run          # XC atlas, static
make -C tools/terse/runtime probe        # lab overlay-collision ABI (arrows)
```

| Faithful | Not faithful (labelled lab) |
|----------|-----------------------------|
| Pixel bytes from `XC.PATTERNS` / disk `PATTERN` art | Frame size 240×352 guess |
| ATBL simple-record decode | Greyscale display palette |
| Write-over-owner collision count | Arrow/`--probe` motion |

Missing for a game: `XC.LOGIC`, dual-stick input map, missions, cabinet colors. See `docs/references/professionalmagic-gorf.md`.

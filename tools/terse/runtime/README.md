# C runtime — pattern animator

Authentic patterns with shared black/yellow/blue/red 2bpp palette; cycles disk frame groups.

```bash
python3 tools/export_play_assets.py   # refresh play/assets.json + pack input
make -C tools/terse/runtime run
```

| Faithful | Lab guess |
|----------|-----------|
| Pixel art + frame lists from PATTERN files | Frame size 240×352 |
| Shared 2bpp colour hypothesis (BYBR) | Exact CRT / hardware LUT |
| CLONE / KAMI / SMINE / BANG frame order | Atlas layout / timing |

Not a game — no `XC.LOGIC`.

# C runtime — pattern animator

One sequence at a time, centred in a **fixed cell** (max frame size) so CLONE/SMINE don’t jump.

```bash
python3 tools/export_play_assets.py
make -C tools/terse/runtime run
```

| Key | Action |
|-----|--------|
| ← → / A D | Previous / next sequence |
| Space | Pause |
| `[` `]` | Slower / faster |
| Esc | Quit |

Palette: 0=black 1=yellow 2=blue 3=red. Not a game.

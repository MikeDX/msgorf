#!/usr/bin/env python3
"""Regenerate font_gen.h from video-demo/font_guess.json."""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
font = json.loads((here.parent / "video-demo" / "font_guess.json").read_text())
cw, ch = font["cell"]
r, g, b = font["color"]
lines = [
    "/* AUTO from font_guess.json — GUESS HUD font */",
    "#ifndef FONT_GEN_H",
    "#define FONT_GEN_H",
    "#include <stdint.h>",
    f"#define FONT_CW {cw}",
    f"#define FONT_CH {ch}",
    f"static const uint8_t FONT_RGB[3] = {{ {r}, {g}, {b} }};",
    "",
    "typedef struct { char ch; uint8_t rows[FONT_CH]; } font_glyph_t;",
    "",
    "static const font_glyph_t FONT_GLYPHS[] = {",
]
for ch_key, rows in font["glyphs"].items():
    if len(ch_key) != 1 or ord(ch_key) > 127:
        continue
    if ch_key == "'":
        esc = "'\\''"
    elif ch_key == "\\":
        esc = "'\\\\'"
    else:
        esc = f"'{ch_key}'"
    packed = []
    for row in rows:
        v = 0
        for i, bit in enumerate(row[:cw]):
            if bit == "1":
                v |= 1 << (cw - 1 - i)
        packed.append(str(v))
    while len(packed) < ch:
        packed.append("0")
    lines.append(f"  {{ {esc}, {{ {', '.join(packed[:ch])} }} }},")
lines += [
    "};",
    "#define FONT_GLYPH_COUNT (sizeof(FONT_GLYPHS)/sizeof(FONT_GLYPHS[0]))",
    "",
    "#endif",
    "",
]
(here / "font_gen.h").write_text("\n".join(lines))
print("wrote font_gen.h")

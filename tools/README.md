# Tools

| Script | Purpose |
|--------|---------|
| `normalize_img.py` | Bit-correct disk images → `work/` |
| `extract_blocks.py` / `extract_strings.py` / `extract_patterns.py` | Legacy dumps from corrected images |
| `export_play_assets.py` | INDEX/ANIM-MAP/patterns → `play/assets.json` |
| `assemble_rom_stub.py` | Gate check for full ROM |
| `harness/blit_collision.py` | Overlay collision test |
| `terse/parse.py` | Parse PATTERN / colon defs from a file |
| `terse/fload_chain.py` | Resolve FLOAD trees |
| `terse/mvp_compile.py` | Host MVP colon compile (experimental IR) |
| `terse/package_patterns_rom.py` | XC.PATTERNS → 64K image @ 0x4000 |
| `terse/runtime/` | C blit/collision stub for future SDL/WASM |

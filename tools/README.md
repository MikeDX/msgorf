# Tools

Run from the repository root (`Ms GORF/`).

| Script | Purpose |
|--------|---------|
| `normalize_img.py` | XOR-correct disk images → `work/*.img.corrected` |
| `extract_strings.py` | Strings + keyword hits → `extracted/strings/` |
| `extract_blocks.py` | 1024-byte screens → `extracted/screens/<disk>/` |
| `extract_patterns.py` | GORF4A PNG previews → `extracted/patterns/` |
| `terse/mvp_compile.py` | Host MVP colon-def compiler → `out/mvp_object.msgx` |
| `terse/test_mvp_compile.py` | Unit tests for MVP compiler |

```bash
python3 tools/normalize_img.py
python3 tools/extract_blocks.py
python3 tools/extract_strings.py
python3 tools/extract_patterns.py
python3 -m tools.terse.mvp_compile --demo
python3 -m tools.terse.test_mvp_compile
```

| `assemble_rom_stub.py` | Phase 7 gate check → `out/assemble_report.json` (exit 2 while blocked) |

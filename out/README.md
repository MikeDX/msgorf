# `out/` — build products

| Artifact | Meaning |
|----------|---------|
| `msgorf_patterns_at_4000.bin` | **Authentic** `XC.PATTERNS` placed at `ROMSTART` 0x4000 (64K image) |
| `msgorf_patterns_rom_report.json` | Provenance / hashes for that image |
| `xc_decode_report.json` | Simple ATBL pattern decode report (when generated) |
| `host_ir.bin` / `host_ir_map.json` | Host IR from `compile_host` (not Nutting Z80) |
| `fload_chain*.json` | Resolved XCLOAD / CODE-LOAD / PAT-LOAD trees |
| `MSGORPAT_XC_PATTERNS` etc. | Raw object copies from Tim’s extract |
| `mvp_object.msgx` / `bullets_fragment.msgx` | Host-MVP experiments |
| `ROM_STATUS.md` | Why a full game ROM is not here yet |

Do **not** treat host IR or MVP objects as arcade ROMs. Full game needs application media — see [`../docs/findings/missing-files-hunt.md`](../docs/findings/missing-files-hunt.md).

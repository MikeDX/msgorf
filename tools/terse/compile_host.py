#!/usr/bin/env python3
"""Host IR compiler for TERSE experiments.

Not the historical Nutting cross-compiler. Evolves the MVP encoding used by
tests and the optional C loader. Primitive opcodes are *host* values only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path

from tools.terse.parse import parse_colon_defs, parse_file, parse_patterns

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out"

XC_BASES = {
    "ROMSTART": 0x4000,
    "PT_HERE": 0x4200,
    "DP": 0x8040,
    "RSTACK": 0xF400,
    "PSTACK": 0xF000,
    "RAMSTART": 0xF800,
}

# Token -> opcode byte in our *host* encoding (not claimed authentic)
PRIMITIVES = {
    "NOP": 0x00,
    "DUP": 0x01,
    "DROP": 0x02,
    "SWAP": 0x03,
    "OVER": 0x04,
    "+": 0x10,
    "-": 0x11,
    "1+": 0x12,
    "1-": 0x13,
    "@": 0x20,  # stub: pop addr, push 0 (unknown CFA / memory model)
    "!": 0x21,  # stub: pop val,addr
    "LIT": 0x30,  # followed by u16 LE
    "EXIT": 0xFF,
    # Explicit stubs for Ms. Gorf fragments — CFA unknown; see docs
    "P-I": 0x40,  # stub: pattern-index write? unknown
    "p-i": 0x41,  # stub: pattern-index fetch? unknown
}

DEMO_SOURCE = """
( mvp demo — not historical Ms. Gorf code )
: INC  1+ ;
: ADD2  1+ 1+ ;
: DROP2  DROP DROP ;
"""

BULLETS_SOURCE = """
( historical fragment from MSGORPAT FS.XC / screen 0088 )
: BULLETS  p-i @  -2 P-I ;
: ENDBULL  P-I ;
"""


@dataclass
class Word:
    name: str
    code: bytes


@dataclass
class CompileResult:
    words: list[Word] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and bool(self.words)


def compile_tokens(tokens: list[str]) -> tuple[bytes, list[str]]:
    out = bytearray()
    errors: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if re.fullmatch(r"-?\d+", tok):
            val = int(tok) & 0xFFFF
            out.append(PRIMITIVES["LIT"])
            out += struct.pack("<H", val)
            i += 1
            continue
        if tok not in PRIMITIVES:
            errors.append(f"unknown word: {tok}")
            i += 1
            continue
        if tok == "LIT":
            errors.append("LIT must be produced by numeric literals")
            i += 1
            continue
        out.append(PRIMITIVES[tok])
        i += 1
    out.append(PRIMITIVES["EXIT"])
    return bytes(out), errors


def compile_source(source: str) -> CompileResult:
    result = CompileResult()
    defs = parse_colon_defs(source)
    if not defs:
        result.errors.append("no colon definitions found")
        return result
    for d in defs:
        code, errs = compile_tokens(d.body)
        result.errors.extend(f"{d.name}: {e}" for e in errs)
        result.words.append(Word(name=d.name, code=code))
    return result


def build_object(result: CompileResult) -> bytes:
    """MSGX object: magic + version + ROMSTART + DP + count + words."""
    buf = bytearray()
    buf += b"MSGX"
    buf += struct.pack(
        "<HIII", 1, XC_BASES["ROMSTART"], XC_BASES["DP"], len(result.words)
    )
    for w in result.words:
        name = w.name.encode("ascii")
        buf += struct.pack("<H", len(name))
        buf += name
        buf += struct.pack("<H", len(w.code))
        buf += w.code
    return bytes(buf)


def emit_host_ir(
    result: CompileResult, out_bin: Path, out_map: Path, label: str
) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    meta: dict = {
        "label": label,
        "ok": result.ok,
        "errors": result.errors,
        "xc_bases": XC_BASES,
        "words": [{"name": w.name, "code_hex": w.code.hex()} for w in result.words],
        "note": "Host MVP encoding — not authentic Nutting TERSE bytecode",
    }
    if result.ok:
        obj = build_object(result)
        out_bin.parent.mkdir(parents=True, exist_ok=True)
        out_bin.write_bytes(obj)
        meta["output"] = str(out_bin.relative_to(ROOT))
        meta["output_sha256"] = hashlib.sha256(obj).hexdigest()
        meta["output_size"] = len(obj)
        out_map.write_text(json.dumps(meta, indent=2) + "\n")
    else:
        out_map.write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", nargs="?", help="Path to a .txt screen/source file")
    ap.add_argument("--demo", action="store_true", help="Compile built-in demo")
    ap.add_argument("--bullets", action="store_true", help="Compile BULLETS fragment")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=OUT / "host_ir.bin",
        help="MSGX object path",
    )
    ap.add_argument(
        "--map",
        type=Path,
        default=OUT / "host_ir_map.json",
        help="JSON word map",
    )
    args = ap.parse_args(argv)

    if args.bullets:
        source = BULLETS_SOURCE
        label = "bullets"
    elif args.demo or not args.source:
        source = DEMO_SOURCE
        label = "demo"
    else:
        path = Path(args.source)
        raw = path.read_bytes()
        if len(raw) <= 1024 and b"\x00" in raw[:64]:
            # Forth screen block
            from tools.terse.parse import screen_text

            source = screen_text(raw)
        else:
            source = raw.decode("ascii", errors="replace")
        label = path.name

    result = compile_source(source)
    meta = emit_host_ir(result, args.output, args.map, label)
    print(json.dumps(meta, indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

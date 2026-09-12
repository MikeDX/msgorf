#!/usr/bin/env python3
"""Minimum viable TERSE-ish colon-definition compiler.

This is NOT the historical Nutting cross-compiler. It:
  1. Parses trivial screens of the form `: NAME word word ;`
  2. Resolves words against a tiny hand-maintained primitive table
  3. Emits a documented object blob with the XC bases from disk 0086

Use it as a regression harness while reverse-engineering real TERSE.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out"

# From MSGORPAT screen 0086 cross-compile LOAD block
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
    "@": 0x20,
    "!": 0x21,
    "LIT": 0x30,  # followed by u16 LE
    "EXIT": 0xFF,
    # Guessed stubs for Ms. Gorf fragments — NOT verified Z80 encodings
    "P-I": 0x40,
    "p-i": 0x41,
}



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


def tokenize_defs(source: str) -> list[tuple[str, list[str]]]:
    """Return list of (name, tokens) for each `: name ... ;` definition."""
    defs = []
    # Strip comments in parentheses
    cleaned = re.sub(r"\([^)]*\)", " ", source)
    for m in re.finditer(r":\s+(\S+)\s+(.*?)\s*;", cleaned, re.S):
        name = m.group(1)
        body = m.group(2)
        tokens = body.split()
        defs.append((name, tokens))
    return defs


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
    defs = tokenize_defs(source)
    if not defs:
        result.errors.append("no colon definitions found")
        return result
    for name, tokens in defs:
        code, errs = compile_tokens(tokens)
        result.errors.extend(f"{name}: {e}" for e in errs)
        result.words.append(Word(name=name, code=code))
    return result


def build_object(result: CompileResult) -> bytes:
    """Simple object format for experiments.

    Header magic 'MSGX' + version + ROMSTART + count
    Then for each word: name len, name utf-8, u16 code len, code bytes
    """
    buf = bytearray()
    buf += b"MSGX"
    buf += struct.pack("<HIII", 1, XC_BASES["ROMSTART"], XC_BASES["DP"], len(result.words))
    for w in result.words:
        name = w.name.encode("ascii")
        buf += struct.pack("<H", len(name))
        buf += name
        buf += struct.pack("<H", len(w.code))
        buf += w.code
    return bytes(buf)


DEMO_SOURCE = """
( mvp demo — not historical Ms. Gorf code )
: INC  1+ ;
: ADD2  1+ 1+ ;
: DROP2  DROP DROP ;
"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", nargs="?", help="Path to a .txt screen/source file")
    ap.add_argument("--demo", action="store_true", help="Compile built-in demo definitions")
    ap.add_argument("-o", "--output", type=Path, default=OUT / "mvp_object.msgx")
    args = ap.parse_args(argv)

    if args.demo or not args.source:
        source = DEMO_SOURCE
        label = "demo"
    else:
        source = Path(args.source).read_text(errors="replace")
        label = Path(args.source).name

    result = compile_source(source)
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {
        "label": label,
        "ok": result.ok,
        "errors": result.errors,
        "xc_bases": XC_BASES,
        "words": [{"name": w.name, "code_hex": w.code.hex()} for w in result.words],
        "note": "Host MVP encoding — not authentic Nutting TERSE bytecode",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if result.ok:
        obj = build_object(result)
        args.output.write_bytes(obj)
        meta["output"] = str(args.output.relative_to(ROOT))
        meta["output_sha256"] = __import__("hashlib").sha256(obj).hexdigest()
        meta["output_size"] = len(obj)
    (OUT / "mvp_compile_report.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(meta, indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

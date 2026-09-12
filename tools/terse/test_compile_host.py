#!/usr/bin/env python3
"""Tests for host compile, VM stubs, and PATTERN parse from disk."""
from __future__ import annotations

import unittest
from pathlib import Path

from tools.terse.compile_host import (
    BULLETS_SOURCE,
    PRIMITIVES,
    build_object,
    compile_source,
    emit_host_ir,
)
from tools.terse.parse import parse_file, parse_patterns
from tools.terse.vm_host import run_code

ROOT = Path(__file__).resolve().parents[2]
GORF_P = ROOT / "extracted/msgorf_floppy_files/MSGORPAT_Disk/GORF-P"
BULLETS_FILE = ROOT / "extracted/bullets_fragment.txt"
OUT = ROOT / "out"


class CompileHostTests(unittest.TestCase):
    def test_inc(self):
        r = compile_source(": INC  1+ ;")
        self.assertTrue(r.ok)
        self.assertEqual(r.words[0].code, bytes([PRIMITIVES["1+"], PRIMITIVES["EXIT"]]))

    def test_literal(self):
        r = compile_source(": ANS  42 ;")
        self.assertTrue(r.ok)
        code = r.words[0].code
        self.assertEqual(code[0], PRIMITIVES["LIT"])
        self.assertEqual(code[1:3], b"\x2a\x00")

    def test_bullets_fragment(self):
        r = compile_source(BULLETS_SOURCE)
        self.assertTrue(r.ok, r.errors)
        names = [w.name for w in r.words]
        self.assertEqual(names, ["BULLETS", "ENDBULL"])

    def test_bullets_from_file(self):
        src = BULLETS_FILE.read_text()
        r = compile_source(src)
        self.assertTrue(r.ok, r.errors)

    def test_emit_host_ir(self):
        r = compile_source(BULLETS_SOURCE)
        meta = emit_host_ir(r, OUT / "host_ir.bin", OUT / "host_ir_map.json", "test")
        self.assertTrue(meta["ok"])
        self.assertTrue((OUT / "host_ir.bin").exists())
        self.assertTrue(build_object(r).startswith(b"MSGX"))


class VmHostTests(unittest.TestCase):
    def test_1plus(self):
        r = compile_source(": INC  1+ ;")
        vm = run_code(r.words[0].code, stack=[41])
        self.assertEqual(vm.stack, [42])

    def test_add_lits(self):
        r = compile_source(": SUM  3 4 + ;")
        # need + in body — compile pushes LIT 3, LIT 4, +
        vm = run_code(r.words[0].code)
        self.assertEqual(vm.stack, [7])

    def test_bullets_runs_with_stubs(self):
        r = compile_source(": BULLETS  p-i @  -2 P-I ;")
        vm = run_code(r.words[0].code)
        self.assertTrue(vm.halted)
        self.assertTrue(any("p-i" in s for s in vm.stub_log))
        self.assertTrue(any(s.startswith("P-I") for s in vm.stub_log))


class PatternParseTests(unittest.TestCase):
    def test_gorf_pat_from_disk(self):
        self.assertTrue(GORF_P.exists())
        info = parse_file(GORF_P)
        names = [p["name"] for p in info["patterns"]]
        self.assertIn("GORF-PAT", names)
        g = next(p for p in info["patterns"] if p["name"] == "GORF-PAT")
        self.assertEqual(g["w"], 12)
        self.assertEqual(g["h"], 13)
        self.assertTrue(all(c in "0123" for row in g["rows"] for c in row))


class MvpCompatTests(unittest.TestCase):
    """mvp_compile re-exports compile_host API."""

    def test_import(self):
        from tools.terse import mvp_compile

        r = mvp_compile.compile_source(": INC  1+ ;")
        self.assertTrue(r.ok)


if __name__ == "__main__":
    unittest.main()

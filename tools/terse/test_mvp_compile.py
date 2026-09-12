#!/usr/bin/env python3
import unittest

from tools.terse.mvp_compile import compile_source, build_object, PRIMITIVES


class MvpCompileTests(unittest.TestCase):
    def test_inc(self):
        r = compile_source(": INC  1+ ;")
        self.assertTrue(r.ok)
        self.assertEqual(r.words[0].name, "INC")
        self.assertEqual(r.words[0].code, bytes([PRIMITIVES["1+"], PRIMITIVES["EXIT"]]))

    def test_literal(self):
        r = compile_source(": ANS  42 ;")
        self.assertTrue(r.ok)
        code = r.words[0].code
        self.assertEqual(code[0], PRIMITIVES["LIT"])
        self.assertEqual(code[1:3], b"\x2a\x00")
        self.assertEqual(code[-1], PRIMITIVES["EXIT"])

    def test_unknown(self):
        r = compile_source(": BAD  QUUX ;")
        self.assertFalse(r.ok)
        self.assertTrue(any("QUUX" in e for e in r.errors))

    def test_object_header(self):
        r = compile_source(": INC  1+ ;")
        obj = build_object(r)
        self.assertTrue(obj.startswith(b"MSGX"))
        self.assertGreater(len(obj), 16)

    def test_bullets_partial(self):
        # Historical fragment uses words we do not yet implement — must error clearly
        r = compile_source(": BULLETS  p-i @  -2 P-I ;")
        self.assertFalse(r.ok)


if __name__ == "__main__":
    unittest.main()

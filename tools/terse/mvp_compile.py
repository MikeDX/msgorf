#!/usr/bin/env python3
"""Thin CLI wrapper — implementation lives in compile_host.py."""
from __future__ import annotations

from tools.terse.compile_host import (
    BULLETS_SOURCE,
    DEMO_SOURCE,
    PRIMITIVES,
    XC_BASES,
    Word,
    CompileResult,
    build_object,
    compile_source,
    compile_tokens,
    main,
)

__all__ = [
    "BULLETS_SOURCE",
    "DEMO_SOURCE",
    "PRIMITIVES",
    "XC_BASES",
    "Word",
    "CompileResult",
    "build_object",
    "compile_source",
    "compile_tokens",
    "main",
]

if __name__ == "__main__":
    raise SystemExit(main())

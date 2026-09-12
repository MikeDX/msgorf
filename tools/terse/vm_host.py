#!/usr/bin/env python3
"""Tiny host IR VM for compile_host opcodes.

Stubs for @ / ! / P-I / p-i are intentional: CFA and memory model unknown.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tools.terse.compile_host import PRIMITIVES


@dataclass
class VM:
    code: bytes
    stack: list[int] = field(default_factory=list)
    mem: dict[int, int] = field(default_factory=dict)
    ip: int = 0
    halted: bool = False
    stub_log: list[str] = field(default_factory=list)

    def push(self, v: int) -> None:
        self.stack.append(v & 0xFFFF)

    def pop(self) -> int:
        if not self.stack:
            raise RuntimeError("stack underflow")
        return self.stack.pop()

    def step(self) -> None:
        if self.halted or self.ip >= len(self.code):
            self.halted = True
            return
        op = self.code[self.ip]
        self.ip += 1
        if op == PRIMITIVES["NOP"]:
            return
        if op == PRIMITIVES["DUP"]:
            self.push(self.stack[-1])
            return
        if op == PRIMITIVES["DROP"]:
            self.pop()
            return
        if op == PRIMITIVES["SWAP"]:
            a, b = self.pop(), self.pop()
            self.push(a)
            self.push(b)
            return
        if op == PRIMITIVES["OVER"]:
            self.push(self.stack[-2])
            return
        if op == PRIMITIVES["+"]:
            b, a = self.pop(), self.pop()
            self.push(a + b)
            return
        if op == PRIMITIVES["-"]:
            b, a = self.pop(), self.pop()
            self.push(a - b)
            return
        if op == PRIMITIVES["1+"]:
            self.push(self.pop() + 1)
            return
        if op == PRIMITIVES["1-"]:
            self.push(self.pop() - 1)
            return
        if op == PRIMITIVES["LIT"]:
            val = self.code[self.ip] | (self.code[self.ip + 1] << 8)
            self.ip += 2
            self.push(val)
            return
        if op == PRIMITIVES["@"]:
            # stub: unknown CFA / address space — push 0
            addr = self.pop()
            self.stub_log.append(f"@ {addr:#x}")
            self.push(self.mem.get(addr, 0))
            return
        if op == PRIMITIVES["!"]:
            addr = self.pop()
            val = self.pop()
            self.stub_log.append(f"! {val:#x} {addr:#x}")
            self.mem[addr] = val & 0xFFFF
            return
        if op == PRIMITIVES["P-I"]:
            # stub — historical pattern-index verb; CFA unknown
            if self.stack:
                self.stub_log.append(f"P-I tos={self.stack[-1]:#x}")
            else:
                self.stub_log.append("P-I (empty)")
            return
        if op == PRIMITIVES["p-i"]:
            # stub — fetch side of P-I pair; push placeholder 0
            self.stub_log.append("p-i")
            self.push(0)
            return
        if op == PRIMITIVES["EXIT"]:
            self.halted = True
            return
        raise RuntimeError(f"unknown opcode {op:#x} at {self.ip - 1}")

    def run(self, max_steps: int = 10_000) -> list[int]:
        for _ in range(max_steps):
            if self.halted:
                break
            self.step()
        else:
            raise RuntimeError("VM step limit exceeded")
        return list(self.stack)


def run_code(code: bytes, stack: list[int] | None = None) -> VM:
    vm = VM(code=code, stack=list(stack or []))
    vm.run()
    return vm

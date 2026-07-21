"""Minimal stdout logging (line-buffered, flush=True for long sweeps)."""
from __future__ import annotations


def log(msg: str = "") -> None:
    print(msg, flush=True)


def section(title: str) -> None:
    bar = "=" * 68
    print(f"\n{bar}\n{title}\n{bar}", flush=True)

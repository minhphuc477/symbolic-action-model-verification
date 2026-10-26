"""Minimal S-expression reader/writer for PDDL text."""

from __future__ import annotations

import re

SExp = str | list["SExp"]

_TOKEN = re.compile(r"\(|\)|[^\s()]+")


def strip_comments(text: str) -> str:
    """Remove ``;`` comments (PDDL has no string literals, so this is safe)."""
    return "\n".join(line.split(";", 1)[0] for line in text.splitlines())


def parse(text: str) -> SExp:
    """Parse the first complete S-expression in ``text``. Symbols are lower-cased."""
    tokens = _TOKEN.findall(strip_comments(text).lower())
    if not tokens:
        raise ValueError("empty PDDL text")
    expr, pos = _read(tokens, 0)
    if pos != len(tokens):
        raise ValueError(f"trailing tokens after position {pos}")
    return expr


def _read(tokens: list[str], pos: int) -> tuple[SExp, int]:
    tok = tokens[pos]
    if tok == ")":
        raise ValueError(f"unexpected ')' at token {pos}")
    if tok != "(":
        return tok, pos + 1
    items: list[SExp] = []
    pos += 1
    while pos < len(tokens) and tokens[pos] != ")":
        item, pos = _read(tokens, pos)
        items.append(item)
    if pos >= len(tokens):
        raise ValueError("unbalanced parentheses")
    return items, pos + 1


def to_str(expr: SExp) -> str:
    """Serialise an S-expression on a single line."""
    if isinstance(expr, str):
        return expr
    return "(" + " ".join(to_str(e) for e in expr) + ")"

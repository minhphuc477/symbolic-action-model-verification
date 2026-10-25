"""
S-Expression Tokenizer, Parser, and AST Manipulation Utilities
=============================================================
Provides pure-Python, zero-dependency tokenization, recursive-descent parsing,
pretty-printing, and AST manipulation for PDDL domain and problem s-expressions.
"""

from __future__ import annotations

from typing import Any


def tokenize(text: str) -> list[str]:
    """Tokenize PDDL text into a flat list of tokens (parens + atoms)."""
    tokens: list[str] = []
    i = 0
    while i < len(text):
        c = text[i]
        if c in "()":
            tokens.append(c)
            i += 1
        elif c == ";":
            # Comment — skip to end of line
            while i < len(text) and text[i] != "\n":
                i += 1
        elif c in " \t\r\n":
            i += 1
        else:
            # Atom
            j = i
            while j < len(text) and text[j] not in " \t\r\n();":
                j += 1
            tokens.append(text[i:j])
            i = j
    return tokens


def parse_sexp(tokens: list[str], pos: int = 0) -> tuple[Any, int]:
    """Recursive descent S-expression parser. Returns (sexp, next_pos)."""
    if pos >= len(tokens):
        raise ValueError("Unexpected end of tokens")
    if tokens[pos] == "(":
        lst: list[Any] = []
        pos += 1  # consume "("
        while pos < len(tokens) and tokens[pos] != ")":
            item, pos = parse_sexp(tokens, pos)
            lst.append(item)
        if pos >= len(tokens):
            raise ValueError("Unmatched '('")
        pos += 1  # consume ")"
        return lst, pos
    else:
        return tokens[pos], pos + 1


def sexp_to_str(sexp: Any, indent: int = 0) -> str:
    """Serialize S-expression back to PDDL string with basic indentation."""
    pad = "  " * indent
    if isinstance(sexp, str):
        return sexp
    if not isinstance(sexp, list) or len(sexp) == 0:
        return "()"
    # Single-atom list
    inner_strs = [sexp_to_str(item, indent + 1) for item in sexp]
    # Heuristic: if all children are atoms, keep on one line
    if all(isinstance(item, str) for item in sexp):
        return "(" + " ".join(inner_strs) + ")"
    # Multi-element with nested lists
    head = sexp_to_str(sexp[0])
    if len(sexp) == 1:
        return f"({head})"
    rest = "\n".join(pad + "  " + sexp_to_str(item, indent + 1) for item in sexp[1:])
    return f"({head}\n{rest}\n{pad})"


def norm_sexp(sexp: Any) -> str:
    """Normalize an S-expression into a canonical single-space lowercase string."""
    raw = " ".join(sexp_to_str(sexp).split()).strip().lower()
    raw = raw.replace("( ", "(").replace(" )", ")")
    while "( " in raw or " )" in raw:
        raw = raw.replace("( ", "(").replace(" )", ")")
    return raw


def find_action_block(sexp: list, action_name: str) -> list | None:
    """
    Locate the :action sexp block for `action_name` inside a domain sexp.
    Returns a reference to the sub-list (mutable).
    """
    if not isinstance(sexp, list):
        return None
    if len(sexp) >= 2 and sexp[0] == ":action" and isinstance(sexp[1], str) and sexp[1].lower() == action_name.lower():
        return sexp
    for item in sexp:
        result = find_action_block(item, action_name)
        if result is not None:
            return result
    return None


def get_section(action_sexp: list, keyword: str) -> int | None:
    """Return the index of `keyword` (e.g. ':precondition') in action_sexp."""
    for i, item in enumerate(action_sexp):
        if isinstance(item, str) and item.lower() == keyword.lower():
            return i
    return None


def parse_action_tuple(action_str: str) -> tuple[str, list[str]]:
    """Extract action name and arguments from PDDL plan action string like '(pick-up a)'."""
    action_str = action_str.strip()
    action_str = action_str.removeprefix("(")
    action_str = action_str.removesuffix(")")
    tokens = action_str.strip().split()
    if not tokens:
        return "", []
    return tokens[0].lower(), [t.lower() for t in tokens[1:]]


# Backward-compatibility aliases
_tokenize = tokenize
_parse_sexp = parse_sexp
_sexp_to_str = sexp_to_str
_norm_sexp = norm_sexp
_find_action_block = find_action_block
_get_section = get_section
_parse_action_tuple = parse_action_tuple

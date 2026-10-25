"""
test_sexp_utils.py
==================
Unit tests for pure-Python S-expression tokenizer, recursive-descent parser,
PDDL AST manipulator, and serialization utilities in src/utils/sexp.py.
"""

import unittest

from src.utils.sexp import (
    find_action_block,
    get_section,
    norm_sexp,
    parse_action_tuple,
    parse_sexp,
    sexp_to_str,
    tokenize,
)


class TestSexpUtils(unittest.TestCase):
    def test_tokenize_basic(self):
        text = "(define (domain test) ; this is a comment\n  (:requirements :strips))"
        tokens = tokenize(text)
        self.assertEqual(
            tokens,
            ["(", "define", "(", "domain", "test", ")", "(", ":requirements", ":strips", ")", ")"]
        )

    def test_tokenize_whitespace_and_comments(self):
        text = "; full line comment\n  (  action-1   ?x   ?y  ) \t\n ; trailing comment"
        tokens = tokenize(text)
        self.assertEqual(tokens, ["(", "action-1", "?x", "?y", ")"])

    def test_parse_sexp_nested(self):
        tokens = ["(", "and", "(", "clear", "?x", ")", "(", "not", "(", "on", "?x", "?y", ")", ")", ")"]
        tree, pos = parse_sexp(tokens)
        self.assertEqual(pos, len(tokens))
        self.assertEqual(
            tree,
            ["and", ["clear", "?x"], ["not", ["on", "?x", "?y"]]]
        )

    def test_parse_sexp_unmatched_paren(self):
        tokens = ["(", "and", "(", "clear", "?x"]
        with self.assertRaises(ValueError):
            parse_sexp(tokens)

    def test_parse_sexp_unexpected_end(self):
        with self.assertRaises(ValueError):
            parse_sexp([], 0)

    def test_sexp_to_str_roundtrip(self):
        raw_sexp = ["and", ["clear", "?o1"], ["ontable", "?o1"]]
        serialized = sexp_to_str(raw_sexp)
        tokens = tokenize(serialized)
        parsed, _ = parse_sexp(tokens)
        self.assertEqual(parsed, raw_sexp)

    def test_norm_sexp(self):
        s1 = ["  AND  ", ["CLEAR", "  ?X "]]
        self.assertEqual(norm_sexp(s1), "(and (clear ?x))")

    def test_find_action_block(self):
        domain_sexp = [
            "define",
            ["domain", "blocks"],
            [":action", "pick-up", ":parameters", ["?x"], ":precondition", ["clear", "?x"]],
            [":action", "put-down", ":parameters", ["?x"], ":precondition", ["holding", "?x"]],
        ]
        act = find_action_block(domain_sexp, "pick-up")
        self.assertIsNotNone(act)
        self.assertEqual(act[1], "pick-up")

        act_upper = find_action_block(domain_sexp, "PICK-UP")
        self.assertIsNotNone(act_upper)
        self.assertEqual(act_upper[1], "pick-up")

        missing = find_action_block(domain_sexp, "non-existent")
        self.assertIsNone(missing)

    def test_get_section(self):
        action_sexp = [":action", "move", ":parameters", ["?from", "?to"], ":precondition", ["at", "?from"], ":effect", ["at", "?to"]]
        self.assertEqual(get_section(action_sexp, ":parameters"), 2)
        self.assertEqual(get_section(action_sexp, ":precondition"), 4)
        self.assertEqual(get_section(action_sexp, ":effect"), 6)
        self.assertIsNone(get_section(action_sexp, ":nonexistent"))

    def test_parse_action_tuple(self):
        name, args = parse_action_tuple("(pick-up a)")
        self.assertEqual(name, "pick-up")
        self.assertEqual(args, ["a"])

        name2, args2 = parse_action_tuple("  (move-box  pos_1_2   pos_1_3   dir_up )  ")
        self.assertEqual(name2, "move-box")
        self.assertEqual(args2, ["pos_1_2", "pos_1_3", "dir_up"])

        name3, args3 = parse_action_tuple("")
        self.assertEqual(name3, "")
        self.assertEqual(args3, [])


if __name__ == "__main__":
    unittest.main()

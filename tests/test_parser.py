import unittest

from query_engine.ast import AndNode, CompareNode, FieldNode, NotNode, OrNode, PhraseNode, RegexNode, TermNode
from query_engine.grammar import GRAMMAR, GRAMMAR_EBNF
from query_engine.parser import QuerySyntaxError, parse, parse_query, tokenize


class ParserTests(unittest.TestCase):
    def test_grammar_is_defined_in_grammar_module(self) -> None:
        self.assertEqual(GRAMMAR.version, "0.1")
        self.assertIn("query", GRAMMAR_EBNF)

    def test_tokenize_keeps_phrase_as_single_token(self) -> None:
        values = [token.value for token in tokenize('level:ERROR "disk full"')]

        self.assertEqual(values[:4], ["level", ":", "ERROR", "disk full"])

    def test_parse_adjacent_terms_as_and(self) -> None:
        node = parse("level:ERROR cpu")

        self.assertIsInstance(node, AndNode)
        self.assertIsInstance(node.left, FieldNode)
        self.assertIsInstance(node.right, TermNode)

    def test_parse_or_has_lower_precedence_than_and(self) -> None:
        node = parse("level:ERROR OR level:WARN cpu")

        self.assertIsInstance(node, OrNode)
        self.assertIsInstance(node.right, AndNode)

    def test_parse_grouped_not_phrase(self) -> None:
        node = parse('level:ERROR AND NOT "test data"')

        self.assertIsInstance(node, AndNode)
        self.assertIsInstance(node.right, NotNode)
        self.assertIsInstance(node.right.child, PhraseNode)

    def test_parse_comparison_and_regex(self) -> None:
        compare = parse("context.cpu>=80")
        regex = parse("message~/timeout|failed/")

        self.assertIsInstance(compare, CompareNode)
        self.assertEqual(compare.field, "context.cpu")
        self.assertEqual(compare.value, 80)
        self.assertIsInstance(regex, RegexNode)
        self.assertEqual(regex.field, "message")

    def test_parse_query_keeps_raw_text(self) -> None:
        query = parse_query("level:ERROR")

        self.assertEqual(query.raw_text, "level:ERROR")
        self.assertIsInstance(query.ast, FieldNode)

    def test_unclosed_parenthesis_is_syntax_error(self) -> None:
        with self.assertRaises(QuerySyntaxError):
            parse("(level:ERROR")


if __name__ == "__main__":
    unittest.main()

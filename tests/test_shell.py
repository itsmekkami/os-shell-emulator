"""Тесты парсера и логики команд"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from command_parser import ParseError, parse_command
from commands import execute

class ParserTest(unittest.TestCase):
    """Проверки разбора строки"""
    def test_empty_line(self):
        self.assertEqual(parse_command("   "), ("", []))

    def test_simple_args(self):
        self.assertEqual(parse_command("ls -l /tmp"), ("ls", ["-l", "/tmp"]))

    def test_double_quotes(self):
        self.assertEqual(parse_command('cd "My Doc"'), ("cd", ["My Doc"]))

    def test_single_quotes(self):
        self.assertEqual(parse_command("ls 'a b' c"), ("ls", ["a b", "c"]))

    def test_unclosed_quote(self):
        with self.assertRaises(ParseError):
            parse_command('cd "oops')


class CommandsTest(unittest.TestCase):
    """Проверки выполнения команд"""
    def test_ls_prints_name_and_args(self):
        result = execute("ls", ["-l", "a b"])
        self.assertIn("ls", result.output)
        self.assertIn("a b", result.output)

    def test_cd_prints_name_and_args(self):
        result = execute("cd", ["/tmp"])
        self.assertIn("cd", result.output)
        self.assertIn("/tmp", result.output)

    def test_cd_too_many_args(self):
        self.assertTrue(execute("cd", ["a", "b"]).error)

    def test_unknown_command(self):
        self.assertIn("не найдена", execute("foo", []).error)

    def test_exit(self):
        self.assertTrue(execute("exit", []).should_exit)

    def test_exit_with_args_is_error(self):
        result = execute("exit", ["1"])
        self.assertTrue(result.error)
        self.assertFalse(result.should_exit)

if __name__ == "__main__":
    unittest.main()
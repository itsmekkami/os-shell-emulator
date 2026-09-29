"""Тесты парсера, команд и VFS"""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from command_parser import ParseError, parse_command
from commands import execute
from vfs import VFS, VFSError

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

class VFSTest(unittest.TestCase):
    """Проверки виртуальной файловой системы (VFS)"""
    def setUp(self):
        """Загружает VFS из simple.xml перед каждым тестом"""
        self.vfs = VFS()
        path = Path(__file__).parent.parent / "vfs" / "simple.xml"
        self.vfs.load_from_xml(str(path))

    def test_list_root(self):
        """Список файлов в корне"""
        items = self.vfs.list_dir("/")
        self.assertIn("readme.txt", items)
        self.assertIn("tmp", items)

    def test_list_subdir(self):
        """Список файлов в подпапке"""
        items = self.vfs.list_dir("/tmp")
        self.assertIn("temp.txt", items)

    def test_read_file(self):
        """Чтение файла"""
        content = self.vfs.read_file("/readme.txt")
        self.assertIn("Добро пожаловать", content)

    def test_change_dir(self):
        """Смена папки"""
        self.vfs.change_dir("/tmp")
        self.assertEqual(self.vfs.current_path, "/tmp")

    def test_missing_file(self):
        """Несуществующий файл - ошибка"""
        with self.assertRaises(VFSError):
            self.vfs.read_file("/nonexistent.txt")

    def test_missing_dir(self):
        """Несуществующая папка - ошибка"""
        with self.assertRaises(VFSError):
            self.vfs.list_dir("/nonexistent")

class CommandsTest(unittest.TestCase):
    """Проверки выполнения команд"""
    def setUp(self):
        """Загружает VFS перед каждым тестом"""
        self.vfs = VFS()
        path = Path(__file__).parent.parent / "vfs" / "simple.xml"
        self.vfs.load_from_xml(str(path))

    def test_ls_root(self):
        """ls показывает содержимое корня"""
        result = execute("ls", ["/"], self.vfs)
        self.assertIn("readme.txt", result.output)

    def test_ls_current_dir(self):
        """ls без аргументов - текущая папка"""
        result = execute("ls", [], self.vfs)
        self.assertIn("readme.txt", result.output)

    def test_cd_valid(self):
        """cd меняет папку"""
        result = execute("cd", ["/tmp"], self.vfs)
        self.assertFalse(result.error)
        self.assertEqual(self.vfs.current_path, "/tmp")

    def test_cd_too_many_args(self):
        """cd с несколькими аргументами - ошибка"""
        result = execute("cd", ["a", "b"], self.vfs)
        self.assertTrue(result.error)

    def test_cd_missing(self):
        """cd в несуществующую папку - ошибка"""
        result = execute("cd", ["/nonexistent"], self.vfs)
        self.assertTrue(result.error)

    def test_pwd(self):
        """pwd показывает путь"""
        result = execute("pwd", [], self.vfs)
        self.assertEqual(result.output, "/")

    def test_cat(self):
        """cat читает файл"""
        result = execute("cat", ["/readme.txt"], self.vfs)
        self.assertIn("Добро пожаловать", result.output)

    def test_cat_missing(self):
        """cat несуществующего файла - ошибка"""
        result = execute("cat", ["/nonexistent.txt"], self.vfs)
        self.assertTrue(result.error)

    def test_unknown_command(self):
        """Неизвестная команда"""
        result = execute("foo", [], self.vfs)
        self.assertIn("не найдена", result.error)

    def test_exit(self):
        """exit - выход"""
        result = execute("exit", [], self.vfs)
        self.assertTrue(result.should_exit)

    def test_exit_with_args_is_error(self):
        """exit с аргументами - ошибка"""
        result = execute("exit", ["1"], self.vfs)
        self.assertTrue(result.error)
        self.assertFalse(result.should_exit)

class StartupScriptTest(unittest.TestCase):
    """Проверки работы со стартовым скриптом"""
    def test_script_file_exists(self):
        """Скрипт существует"""
        script_path = Path(__file__).parent.parent / "scripts" / "startup.txt"
        self.assertTrue(script_path.exists())

    def test_script_content(self):
        """Скрипт содержит команды"""
        script_path = Path(__file__).parent.parent / "scripts" / "startup.txt"
        with open(script_path, "r", encoding="utf-8") as file:
            content = file.read()
        self.assertIn("ls", content)
        self.assertIn("cd", content)

    def test_missing_script(self):
        """Отсутствующий скрипт - не существует"""
        fake_path = "./scripts/nonexistent_script.txt"
        self.assertFalse(os.path.exists(fake_path))

if __name__ == "__main__":
    unittest.main()
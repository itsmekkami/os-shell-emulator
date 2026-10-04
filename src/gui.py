"""Графический интерфейс эмулятора (tkinter)"""
import getpass
import os
import socket
import tkinter as tk
from tkinter import scrolledtext
from command_parser import ParseError, parse_command
from commands import execute
from vfs import VFS, VFSError

BG_COLOR = "#1e1e1e"
FG_COLOR = "#d4d4d4"
ERROR_COLOR = "#f44747"
FONT = ("Courier", 12)

def get_window_title():
    """Формирует заголовок окна «Эмулятор - [user@host]»"""
    return f"Эмулятор - [{getpass.getuser()}@{socket.gethostname()}]"

def get_prompt():
    """Формирует приглашение «user@host$»"""
    return f"{getpass.getuser()}@{socket.gethostname()}$"

class ShellEmulator:
    """Окно эмулятора: область вывода и строка ввода"""
    def __init__(self, root: tk.Tk, vfs_path: str = "./vfs/minimal.xml",
                 script_path: str = None):
        """Конструктор класса"""
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.prompt = get_prompt()
        self.root.title(get_window_title())
        self._build_widgets()
        self._load_vfs()
        self._print_startup_info()
        if self.script_path:
            self._run_script()

    def _build_widgets(self):
        """Создаёт область вывода и поле ввода"""
        self.output = scrolledtext.ScrolledText(
            self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT,
            state="disabled", wrap="word",
        )
        self.output.tag_config("error", foreground=ERROR_COLOR)
        self.output.pack(fill="both", expand=True)

        self.entry = tk.Entry(
            self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT,
            insertbackground=FG_COLOR,
        )
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def _load_vfs(self):
        """Загружает VFS из XML-файла"""
        self.vfs = VFS()
        if not os.path.exists(self.vfs_path):
            self._print(f"Ошибка: файл VFS не найден: {self.vfs_path}", "error")
            return
        try:
            self.vfs.load_from_xml(self.vfs_path)
        except Exception as error:
            self._print(f"Ошибка загрузки VFS: {error}", "error")

    def _print(self, text: str, tag: str = ""):
        """Добавляет строку в область вывода"""
        self.output.config(state="normal")
        self.output.insert("end", text + "\n", tag)
        self.output.config(state="disabled")
        self.output.see("end")

    def _print_startup_info(self):
        """Выводит отладочную информацию о параметрах"""
        self._print("Параметры запуска:")
        self._print(f"VFS: {self.vfs_path}")
        self._print(f"Скрипт: {self.script_path}")

    def _run_script(self):
        """Выполняет команды из стартового скрипта"""
        if not os.path.exists(self.script_path):
            self._print(f"Ошибка: файл скрипта не найден: {self.script_path}",
                "error")
            return
        try:
            with open(self.script_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except OSError as error:
            self._print(f"Ошибка чтения скрипта: {error}", "error")
            return
        self._print(f"Выполнение скрипта: {self.script_path}")
        errors = []
        for line in lines:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            self._print(f"{self.prompt} {line}")
            error = self._execute_silent(line)
            if error == "__EXIT__":
                return
            if error:
                errors.append(error)

        if errors:
            self._print("Скрипт выполнен с ошибками:", "error")
            for err in errors:
                self._print(f" - {err}", "error")
        else:
            self._print("Скрипт выполнен")

    def _execute_silent(self, line: str):
        """Выполняет строку. Возвращает текст ошибки или None"""
        try:
            name, args = parse_command(line)
        except ParseError as error:
            self._print(str(error), "error")
            return str(error)
        if not name:
            return None
        result = execute(name, args, self.vfs)
        if result.output:
            self._print(result.output)
        if result.error:
            self._print(result.error, "error")
            return result.error
        if result.should_exit:
            self.root.destroy()
            return "__EXIT__"
        return None

    def _on_enter(self, _event: tk.Event):
        """Обрабатывает нажатие Enter"""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self._print(f"{self.prompt} {line}")
        self._run_line(line)

    def _run_line(self, line: str):
        """Разбирает и выполняет строку"""
        try:
            name, args = parse_command(line)
        except ParseError as error:
            self._print(str(error), "error")
            return
        if not name:
            return
        result = execute(name, args, self.vfs)
        if result.output:
            self._print(result.output)
        if result.error:
            self._print(result.error, "error")
        if result.should_exit:
            self.root.destroy()
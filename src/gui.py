"""Графический интерфейс эмулятора (tkinter)"""
import getpass
import socket
import tkinter as tk
from tkinter import scrolledtext

from command_parser import ParseError, parse_command
from commands import execute

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

    def __init__(self, root: tk.Tk):
        """Конструктор класса"""
        self.root = root
        self.prompt = get_prompt()
        self.root.title(get_window_title())
        self._build_widgets()

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

    def _print(self, text: str, tag: str = ""):
        """Добавляет строку в область вывода"""
        self.output.config(state="normal")
        self.output.insert("end", text + "\n", tag)
        self.output.config(state="disabled")
        self.output.see("end")

    def _on_enter(self, _event: tk.Event):
        """Обрабатывает нажатие Enter"""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self._print(f"{self.prompt} {line}")
        self._run_line(line)

    def _run_line(self, line: str):
        """Разбирает и выполнят строку"""
        try:
            name, args = parse_command(line)
        except ParseError as error:
            self._print(str(error), "error")
            return
        if not name:
            return
        result = execute(name, args)
        if result.output:
            self._print(result.output)
        if result.error:
            self._print(result.error, "error")
        if result.should_exit:
            self.root.destroy()
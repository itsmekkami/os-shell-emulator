"""Запуск эмулятора"""
import tkinter as tk
import argparse
from gui import ShellEmulator

def parse_args():
    """Разбирает аргументы командной строки"""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument("--vfs", default="./vfs", help="Путь к VFS")
    parser.add_argument("--script", default=None, \
                        help="Путь к стартовому скрипту")
    return parser.parse_args()

def main():
    """Создаёт окно и запускает главный цикл"""
    args = parse_args()
    print("Параметры запуска: ")
    print(f"VFS: {args.vfs}")
    print(f"Скрипт: {args.script}")

    root = tk.Tk()
    root.geometry("700x450")
    emulator = ShellEmulator(root, script_path=args.script)
    root.mainloop()

if __name__ == "__main__":
    main()
"""Запуск эмулятора"""
import tkinter as tk
from gui import ShellEmulator

def main():
    """Создаёт окно и запускает главный цикл"""
    root = tk.Tk()
    root.geometry("700x450")
    ShellEmulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
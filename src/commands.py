"""Команды эмулятора"""
from typing import Callable

MAX_CD_ARGS = 1

class Result:
    """Результат выполнения команды"""
    def __init__(self, output="", error="", should_exit=False):
        self.output = output
        self.error = error
        self.should_exit = should_exit

def format_stub(name: str, args: list[str]):
    """Формирует вывод заглушки"""
    return f"{name}: аргументы = {args}"

def cmd_ls(args: list[str]):
    """Заглушка команды ls"""
    return Result(output=format_stub("ls", args))

def cmd_cd(args: list[str]):
    """Заглушка команды cd"""
    if len(args) > MAX_CD_ARGS:
        return Result(error="cd: слишком много аргументов")
    return Result(output=format_stub("cd", args))

def cmd_exit(args: list[str]):
    """Команда exit"""
    if args:
        return Result(error="exit: команда не принимает аргументов")
    return Result(should_exit=True)

COMMANDS: dict[str, Callable[[list[str]], Result]] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}

def execute(name: str, args: list[str]):
    """Находит и выполняет команду по имени"""
    handler = COMMANDS.get(name)
    if handler is None:
        return Result(error=f"{name}: команда не найдена")
    return handler(args)
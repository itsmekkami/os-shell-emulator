"""Команды эмулятора"""
import getpass
import platform
import socket
from datetime import datetime
from typing import Callable

from vfs import VFS, VFSError

MAX_CD_ARGS = 1


class Result:
    """Результат выполнения команды"""
    def __init__(self, output="", error="", should_exit=False):
        self.output = output
        self.error = error
        self.should_exit = should_exit

def cmd_ls(args: list[str], vfs: VFS):
    """Команда ls - показывает содержимое папки"""
    path = args[0] if args else None
    try:
        items = vfs.list_dir(path)
    except VFSError as error:
        return Result(error=f"ls: {error}")
    if not items:
        return Result(output="")
    return Result(output="\n".join(items))

def cmd_cd(args: list[str], vfs: VFS):
    """Команда cd - меняет текущую папку"""
    if len(args) > MAX_CD_ARGS:
        return Result(error="cd: слишком много аргументов")
    if not args:
        return Result(error="cd: нужен аргумент")
    try:
        vfs.change_dir(args[0])
    except VFSError as error:
        return Result(error=f"cd: {error}")
    return Result(output="")

def cmd_pwd(args: list[str], vfs: VFS):
    """Команда pwd - показывает текущий путь"""
    return Result(output=vfs.current_path)

def cmd_cat(args: list[str], vfs: VFS):
    """Команда cat - читает файл"""
    if not args:
        return Result(error="cat: нужен аргумент")
    try:
        content = vfs.read_file(args[0])
    except VFSError as error:
        return Result(error=f"cat: {error}")
    return Result(output=content)

def cmd_uname(args: list[str], vfs: VFS):
    """Команда uname - информация о системе"""
    if "-a" in args:
        info = [
            platform.system(),
            platform.node(),
            platform.release(),
            platform.version(),
            platform.machine(),
        ]
        return Result(output=" ".join(info))
    return Result(output=platform.system())

def cmd_who(args: list[str], vfs: VFS):
    """Команда who - список пользователей в системе"""
    user = getpass.getuser()
    host = socket.gethostname()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return Result(output=f"{user}    {host}   {now}")

def cmd_exit(args: list[str], vfs: VFS):
    """Команда exit - завершает работу"""
    if args:
        return Result(error="exit: команда не принимает аргументов")
    return Result(should_exit=True)

COMMANDS: dict[str, Callable] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd,
    "cat": cmd_cat,
    "uname": cmd_uname,
    "who": cmd_who,
    "exit": cmd_exit,
}

def execute(name: str, args: list[str], vfs: VFS):
    """Находит и выполняет команду по имени"""
    handler = COMMANDS.get(name)
    if handler is None:
        return Result(error=f"{name}: команда не найдена")
    return handler(args, vfs)
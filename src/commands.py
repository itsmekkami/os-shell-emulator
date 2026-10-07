"""Команды эмулятора"""
import getpass
import platform
import socket
from datetime import datetime
from typing import Callable

from vfs import VFS, VFSError

MAX_CD_ARGS = 1
BYTES_IN_KB = 1024
BYTES_IN_MB = 1024 * 1024
LS_FLAG_PREFIX = "-"
LS_FLAG_ALL = "a"
LS_FLAG_LONG = "l"
LS_FLAG_HUMAN = "h"
HIDDEN_PREFIX = "."

class Result:
    """Результат выполнения команды"""
    def __init__(self, output="", error="", should_exit=False):
        self.output = output
        self.error = error
        self.should_exit = should_exit

def _parse_ls_args(args: list[str]):
    """Разбирает аргументы ls на флаги и путь"""
    flags = ""
    path = None
    for arg in args:
        if arg.startswith(LS_FLAG_PREFIX):
            flags += arg[1:]
        else:
            path = arg
    return flags, path

def _format_long(items: list, flags: str):
    """Формирует длинный формат вывода (ls -l)"""
    date = datetime.now().strftime("%b %d %H:%M")
    user = getpass.getuser()
    lines = []
    for item in items:
        size = item["size"]
        if LS_FLAG_HUMAN in flags:
            size = format_size(size)
        if item["type"] == "dir":
            perms = "drwxr-xr-x"
        else:
            perms = "-rw-r--r--"
        lines.append(
            f"{perms} 1 {user} {user} {size:>6} {date} {item['name']}"
        )
    return "\n".join(lines)

def cmd_ls(args: list[str], vfs: VFS):
    """Команда ls - показывает содержимое папки"""
    flags, path = _parse_ls_args(args)

    try:
        items = vfs.list_dir_info(path)
    except VFSError as error:
        return Result(error=f"ls: {error}")

    if LS_FLAG_ALL not in flags:
        items = [
            i for i in items
            if not i["name"].startswith(HIDDEN_PREFIX)
        ]

    if LS_FLAG_LONG in flags:
        return Result(output=_format_long(items, flags))

    if not items:
        return Result(output="")
    return Result(output="\n".join(i["name"] for i in items))

def format_size(size: int):
    """Преобразует размер в читаемый вид"""
    if size < BYTES_IN_KB:
        return f"{size}B"
    if size < BYTES_IN_MB:
        return f"{size / BYTES_IN_KB:.1f}K"
    return f"{size / BYTES_IN_MB:.1f}M"

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

def cmd_mkdir(args: list[str], vfs: VFS):
    """Команда mkdir - создаёт папку"""
    if not args:
        return Result(error="mkdir: нужен аргумент")
    try:
        vfs.make_dir(args[0])
    except VFSError as error:
        return Result(error=str(error))
    return Result(output="")

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
    "mkdir": cmd_mkdir,
    "exit": cmd_exit,
}

def execute(name: str, args: list[str], vfs: VFS):
    """Находит и выполняет команду по имени"""
    handler = COMMANDS.get(name)
    if handler is None:
        return Result(error=f"{name}: команда не найдена")
    return handler(args, vfs)
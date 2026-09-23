"""Парсер командной строки"""
import shlex

class ParseError(Exception):
    """Ошибка разбора введённой строки"""

def parse_command(line: str):
    """Разбирает строку на имя команды и список аргументов"""
    try:
        tokens = shlex.split(line)
    except ValueError as error:
        raise ParseError(f"ошибка разбора: {error}") from error
    if not tokens:
        return "", []
    return tokens[0], tokens[1:]
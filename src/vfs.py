"""Виртуальная файловая система (VFS) в памяти"""
import base64
import xml.etree.ElementTree as et

class VFSError(Exception):
    """Ошибка работы с VFS"""

class VFS:
    """Виртуальная файловая система"""
    def __init__(self):
        """Создаёт пустую VFS"""
        self.root = {"type": "dir", "children": {}}
        self.current_path = "/"

    def load_from_xml(self, path: str):
        """Загружает VFS из XML-файла"""
        tree = et.parse(path)
        root_element = tree.getroot()
        self.root = self._parse_vfs_root(root_element)
        self.current_path = "/"

    def _parse_vfs_root(self, element):
        """Разбирает корневой элемент vfs"""
        for child in element:
            return self._parse_element(child)
        return {"type": "dir", "children": {}}

    def _parse_element(self, element):
        """Рекурсивно разбирает XML-элемент"""
        if element.tag == "directory":
            node = {"type": "dir", "children": {}}
            for child in element:
                name = child.get("name")
                node["children"][name] = self._parse_element(child)
            return node
        if element.tag == "file":
            content_element = element.find("content")
            if content_element is None:
                return {"type": "file", "content": ""}
            encoding = content_element.get("encoding")
            text = content_element.text or ""
            if encoding == "base64":
                content = base64.b64decode(text)
            else:
                content = text
            return {"type": "file", "content": content}
        return {"type": "dir", "children": {}}

    def _split_path(self, path: str):
        """Разбивает путь на части"""
        return [p for p in path.split("/") if p]

    def _get_node(self, path: str):
        """Находит узел по пути"""
        if path is None:
            path = self.current_path
        if path.startswith("/"):
            node = self.root
            parts = self._split_path(path)
        else:
            node = self._get_node(self.current_path)
            parts = self._split_path(path)
        for part in parts:
            if part in (".", ""):
                continue
            if part == "..":
                continue
            if node["type"] != "dir":
                raise VFSError(f"не папка: {path}")
            if part not in node["children"]:
                raise VFSError(f"не найдено: {path}")
            node = node["children"][part]
        return node

    def list_dir(self, path: str = None):
        """Возвращает содержимое папки"""
        node = self._get_node(path)
        if node["type"] != "dir":
            raise VFSError(f"не папка: {path}")
        return sorted(node["children"].keys())

    def read_file(self, path: str):
        """Читает содержимое файла"""
        node = self._get_node(path)
        if node["type"] != "file":
            raise VFSError(f"не файл: {path}")
        content = node["content"]
        if isinstance(content, bytes):
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return base64.b64encode(content).decode("ascii")
        return content

    def change_dir(self, path: str):
        """Меняет текущую папку"""
        node = self._get_node(path)
        if node["type"] != "dir":
            raise VFSError(f"не папка: {path}")
        if path.startswith("/"):
            self.current_path = path
        else:
            if self.current_path == "/":
                self.current_path = "/" + path
            else:
                self.current_path = self.current_path + "/" + path

    def make_dir(self, path: str):
        """Создаёт новую папку в VFS"""
        if "/" in path.rstrip("/"):
            parent_path, name = path.rsplit("/", 1)
            if not parent_path:
                parent_path = "/"
        else:
            parent_path = self.current_path
            name = path
        name = name.strip("/")
        if not name:
            raise VFSError("mkdir: не указано имя папки")
        parent = self._get_node(parent_path)
        if parent["type"] != "dir":
            raise VFSError(f"mkdir: не папка: {parent_path}")
        if name in parent["children"]:
            raise VFSError(f"mkdir: уже существует: {name}")
        parent["children"][name] = {"type": "dir", "children": {}}
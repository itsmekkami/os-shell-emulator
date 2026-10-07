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
        
        parts = self._split_path(path)

        if not path.startswith("/"):
            current_parts = self._split_path(self.current_path)
            parts = current_parts + parts
        
        parts = self._normalize_parts(parts)
        
        node = self.root
        for part in parts:
            if node["type"] != "dir":
                raise VFSError(f"не папка: {part}")
            if part not in node["children"]:
                raise VFSError(f"не найдено: {path}")
            node = node["children"][part]
        return node

    def _normalize_parts(self, parts: list):
        """Обрабатывает .. в пути"""
        result = []
        for part in parts:
            if part in (".", ""):
                continue
            if part == "..":
                if result:
                    result.pop()
                continue
            result.append(part)
        return result

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
            parts = self._split_path(path)
        else:
            current = self._split_path(self.current_path)
            parts = current + self._split_path(path)
        
        parts = self._normalize_parts(parts)
        
        if not parts:
            self.current_path = "/"
        else:
            self.current_path = "/" + "/".join(parts)

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

    def list_dir_info(self, path: str = None):
        """Возвращает информацию о содержимом папки"""
        node = self._get_node(path)
        if node["type"] != "dir":
            raise VFSError(f"не папка: {path}")
        
        result = []
        for name in sorted(node["children"].keys()):
            child = node["children"][name]
            if child["type"] == "dir":
                size = 0
                type_str = "d"
            else:
                content = child.get("content", "")
                if isinstance(content, str):
                    size = len(content.encode("utf-8"))
                else:
                    size = len(content)
                type_str = "-"
            result.append({
                "name": name,
                "type": child["type"],
                "type_str": type_str,
                "size": size,
            })
        return result
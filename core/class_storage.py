from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from uuid import uuid4

from .file_manager import read_json, write_json


DEFAULT_CATEGORIES = {
    "team_builder": "Team & Rotation Builder",
    "class_library": "Class Material Library",
}


def _default_data() -> dict:
    return {"classes": [], "files": []}


def _make_class_folder(data_dir: Path, class_id: str) -> Path:
    folder = data_dir / "uploads" / class_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


class ClassStorage:
    def __init__(self, data_dir: Optional[Path] = None):
        data_dir = data_dir or Path(__file__).resolve().parents[1] / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "classes.json"
        self._data = self._load()

    def _load(self) -> dict:
        return read_json(self.file_path, default=_default_data()) or _default_data()

    def _save(self) -> None:
        write_json(self.file_path, self._data)

    def get_classes(self, category_key: str) -> List[Dict]:
        return [
            item
            for item in self._data["classes"]
            if item.get("category") == category_key
        ]

    def get_class(self, class_id: str) -> Optional[Dict]:
        for item in self._data["classes"]:
            if item.get("id") == class_id:
                return item
        return None

    def get_all_classes(self) -> List[Dict]:
        return list(self._data["classes"])

    def get_category_label(self, category_key: str) -> str:
        return DEFAULT_CATEGORIES.get(category_key, "Unknown")

    def add_class(self, name: str, category_key: str) -> Tuple[bool, Union[str, Dict]]:
        name = name.strip()
        if not name:
            return False, "Class name cannot be empty."

        if category_key not in DEFAULT_CATEGORIES:
            return False, "Invalid category selected."

        existing = [
            item
            for item in self._data["classes"]
            if item.get("category") == category_key
            and item.get("name", "").strip().lower() == name.lower()
        ]

        if existing:
            return False, "A class with that name already exists in this folder."

        new_class = {
            "id": uuid4().hex,
            "name": name,
            "category": category_key,
            "folder": DEFAULT_CATEGORIES[category_key],
        }
        self._data["classes"].append(new_class)
        self._save()
        return True, new_class

    def delete_class(self, class_id: str) -> tuple[bool, str]:
        before = len(self._data["classes"])
        self._data["classes"] = [
            item for item in self._data["classes"] if item.get("id") != class_id
        ]
        self._data["files"] = [
            file_item for file_item in self._data["files"] if file_item.get("class_id") != class_id
        ]
        if len(self._data["classes"]) == before:
            return False, "Class not found."

        self._save()
        return True, "Class deleted successfully."

    def get_files_for_class(self, class_id: str) -> List[Dict]:
        return [
            file_item
            for file_item in self._data["files"]
            if file_item.get("class_id") == class_id
        ]

    def upload_file(self, class_id: str, file_name: str, content: bytes, mime_type: str) -> Tuple[bool, Union[str, Dict]]:
        class_item = self.get_class(class_id)
        if not class_item:
            return False, "Class folder not found."

        safe_name = Path(file_name).name
        upload_folder = _make_class_folder(self.data_dir, class_id)
        target_path = upload_folder / safe_name
        if target_path.exists():
            return False, "A file with that name already exists in this class folder."

        target_path.write_bytes(content)

        file_item = {
            "id": uuid4().hex,
            "class_id": class_id,
            "name": safe_name,
            "path": str(target_path.relative_to(self.data_dir)),
            "mime_type": mime_type,
        }
        self._data["files"].append(file_item)
        self._save()
        return True, file_item

    def delete_file(self, file_id: str) -> tuple[bool, str]:
        file_item = None
        for item in self._data["files"]:
            if item.get("id") == file_id:
                file_item = item
                break

        if not file_item:
            return False, "File not found."

        file_path = self.data_dir / file_item.get("path", "")
        if file_path.exists():
            file_path.unlink()

        self._data["files"] = [
            item for item in self._data["files"] if item.get("id") != file_id
        ]
        self._save()
        return True, "File deleted successfully."

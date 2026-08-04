import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from uuid import uuid4

from .file_manager import read_json, write_json


DEFAULT_MODULES = ["Module 1", "Module 2", "Module 3", "Module 4", "Module 5"]


def _default_data() -> dict:
    return {"classes": [], "files": []}


def _normalize_data(data: Optional[dict]) -> dict:
    if not isinstance(data, dict):
        return _default_data()
    if "classes" not in data or not isinstance(data["classes"], list):
        data["classes"] = []
    if "files" not in data or not isinstance(data["files"], list):
        data["files"] = []
    return data


def _class_upload_folder(data_dir: Path, class_id: str) -> Path:
    folder = data_dir / "uploads" / class_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _module_folder(data_dir: Path, class_id: str, module_name: str) -> Path:
    safe_module = Path(module_name.strip().replace("/", "-").replace("\\", "-")).name
    folder = _class_upload_folder(data_dir, class_id) / safe_module
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class ClassStorage:
    def __init__(self, data_dir: Optional[Path] = None):
        data_dir = data_dir or Path(__file__).resolve().parents[1] / "data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "classes.json"
        self._data = _normalize_data(self._load())

    def _load(self) -> dict:
        return read_json(self.file_path, default=_default_data()) or _default_data()

    def _save(self) -> None:
        write_json(self.file_path, self._data)

    def get_classes(self) -> List[Dict]:
        return list(self._data["classes"])

    def get_class(self, class_id: str) -> Optional[Dict]:
        for item in self._data["classes"]:
            if item.get("id") == class_id:
                return item
        return None

    def add_class(self, name: str) -> Tuple[bool, Union[str, Dict]]:
        name = name.strip()
        if not name:
            return False, "Class name cannot be empty."
        if any(item.get("name", "").strip().lower() == name.lower() for item in self._data["classes"]):
            return False, "A class with that name already exists."

        new_class = {
            "id": uuid4().hex,
            "name": name,
            "created_at": _utc_now_iso(),
            "rotation_history": [],
        }
        self._data["classes"].append(new_class)
        self._save()
        return True, new_class

    def update_class(self, class_id: str, name: str) -> Tuple[bool, str]:
        class_item = self.get_class(class_id)
        if not class_item:
            return False, "Class not found."
        class_item["name"] = name.strip() or class_item["name"]
        self._save()
        return True, "Class updated successfully."

    def delete_class(self, class_id: str) -> Tuple[bool, str]:
        before = len(self._data["classes"])
        self._data["classes"] = [item for item in self._data["classes"] if item.get("id") != class_id]
        self._data["files"] = [item for item in self._data["files"] if item.get("class_id") != class_id]
        if len(self._data["classes"]) == before:
            return False, "Class not found."

        folder = self.data_dir / "uploads" / class_id
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)

        self._save()
        return True, "Class deleted successfully."

    def add_rotation(self, class_id: str, groups: List[List[str]], group_size: int, seed: int, raw_input: str) -> Tuple[bool, Union[str, Dict]]:
        class_item = self.get_class(class_id)
        if not class_item:
            return False, "Class not found."

        rotation_record = {
            "id": uuid4().hex,
            "created_at": _utc_now_iso(),
            "group_size": group_size,
            "seed": seed,
            "student_count": sum(len(group) for group in groups),
            "groups": groups,
            "raw_input": raw_input,
        }
        class_item.setdefault("rotation_history", []).append(rotation_record)
        self._save()
        return True, rotation_record

    def get_rotations(self, class_id: str) -> List[Dict]:
        class_item = self.get_class(class_id)
        return list(class_item.get("rotation_history", [])) if class_item else []

    def get_latest_rotation(self, class_id: str) -> Optional[Dict]:
        rotations = self.get_rotations(class_id)
        return rotations[-1] if rotations else None

    def get_modules_for_class(self, class_id: str) -> List[str]:
        modules = set(DEFAULT_MODULES)
        for file_item in self._data["files"]:
            if file_item.get("class_id") == class_id:
                modules.add(file_item.get("module", "Module 1"))
        return sorted(modules)

    def get_files_for_class(self, class_id: str, module: Optional[str] = None) -> List[Dict]:
        files = [item for item in self._data["files"] if item.get("class_id") == class_id]
        if module:
            files = [item for item in files if item.get("module") == module]
        return files

    def upload_file(self, class_id: str, module: str, file_name: str, content: bytes, mime_type: str) -> Tuple[bool, Union[str, Dict]]:
        class_item = self.get_class(class_id)
        if not class_item:
            return False, "Class not found."

        module_name = module.strip() or "Module 1"
        upload_folder = _module_folder(self.data_dir, class_id, module_name)
        safe_name = Path(file_name).name
        target_path = upload_folder / safe_name
        if target_path.exists():
            return False, "A file with that name already exists in this module."

        target_path.write_bytes(content)
        relative_path = str(target_path.relative_to(self.data_dir))

        file_item = {
            "id": uuid4().hex,
            "class_id": class_id,
            "module": module_name,
            "name": safe_name,
            "path": relative_path,
            "mime_type": mime_type,
            "created_at": _utc_now_iso(),
        }
        self._data["files"].append(file_item)
        self._save()
        return True, file_item

    def delete_file(self, file_id: str) -> Tuple[bool, str]:
        file_item = next((item for item in self._data["files"] if item.get("id") == file_id), None)
        if not file_item:
            return False, "File not found."

        file_path = self.data_dir / file_item.get("path", "")
        if file_path.exists():
            file_path.unlink()

        self._data["files"] = [item for item in self._data["files"] if item.get("id") != file_id]
        self._save()
        return True, "File deleted successfully."

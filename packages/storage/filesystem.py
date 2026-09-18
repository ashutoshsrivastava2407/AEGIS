"""Filesystem Implementation of ObjectStorage Interface for Local S3 Compatibility."""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from packages.storage.base import ObjectStorage


class FilesystemObjectStorage(ObjectStorage):
    """Stores objects on local filesystem adhering to S3 bucket prefix paths."""

    def __init__(self, base_dir: str = "data/object_store") -> None:
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        # Prevent path traversal
        clean_key = key.lstrip("/").replace("..", "_")
        return os.path.join(self.base_dir, clean_key)

    async def put_object(self, key: str, data: bytes, content_type: str = "application/json") -> Dict[str, Any]:
        file_path = self._get_path(key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(data)

        checksum = hashlib.sha256(data).hexdigest()
        byte_size = len(data)

        meta = {
            "key": key,
            "byte_size": byte_size,
            "checksum": checksum,
            "content_type": content_type,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        meta_path = file_path + ".meta.json"
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump(meta, mf)

        return meta

    async def get_object(self, key: str) -> bytes:
        file_path = self._get_path(key)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Object key '{key}' not found in storage")
        with open(file_path, "rb") as f:
            return f.read()

    async def delete_object(self, key: str) -> bool:
        file_path = self._get_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)
            meta_path = file_path + ".meta.json"
            if os.path.exists(meta_path):
                os.remove(meta_path)
            return True
        return False

    async def list_objects(self, prefix: str = "") -> List[str]:
        prefix_path = self._get_path(prefix)
        keys: List[str] = []

        if not os.path.exists(prefix_path):
            return keys

        for root, _, files in os.walk(prefix_path):
            for file in files:
                if file.endswith(".meta.json"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.base_dir).replace("\\", "/")
                keys.append(rel_path)

        return keys

    async def object_exists(self, key: str) -> bool:
        file_path = self._get_path(key)
        return os.path.exists(file_path)

    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        file_path = self._get_path(key)
        meta_path = file_path + ".meta.json"
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as mf:
                return json.load(mf)
        elif os.path.exists(file_path):
            stat = os.stat(file_path)
            return {
                "key": key,
                "byte_size": stat.st_size,
                "checksum": "",
                "updated_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            }
        return None


storage = FilesystemObjectStorage()

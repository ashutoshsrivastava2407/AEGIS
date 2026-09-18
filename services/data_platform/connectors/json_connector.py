"""Real JSON and JSONL Data Source Connector."""

import json
import os
import io
from typing import Dict, Any, List, Tuple
from services.data_platform.connectors.base import BaseConnector


class JSONConnector(BaseConnector):
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        if "file_path" not in config and "raw_content" not in config and "json_data" not in config:
            return False, "JSON configuration requires 'file_path', 'raw_content', or 'json_data'"
        return True, "JSON configuration valid"

    async def test_connection(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        valid, msg = self.validate_config(config)
        if not valid:
            return False, msg
        file_path = config.get("file_path")
        if file_path and not os.path.exists(file_path):
            return False, f"JSON file not found at path '{file_path}'"
        return True, "JSON source connection test successful"

    async def discover_schema(self, config: Dict[str, Any]) -> Dict[str, Any]:
        records = await self.read(config)
        if not records:
            return {"columns": []}
        sample = records[0]
        columns = []
        for k, v in sample.items():
            t = "string"
            if isinstance(v, int): t = "integer"
            elif isinstance(v, float): t = "float"
            elif isinstance(v, bool): t = "boolean"
            elif isinstance(v, (dict, list)): t = "json_object"
            columns.append({"name": k, "type": t, "nullable": True})
        return {"columns": columns, "detected_rows": len(records)}

    async def estimate_records(self, config: Dict[str, Any]) -> int:
        records = await self.read(config)
        return len(records)

    async def read(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        json_data = config.get("json_data")
        if json_data is not None:
            if isinstance(json_data, list):
                return json_data
            elif isinstance(json_data, dict):
                return [json_data]

        raw_content = config.get("raw_content")
        file_path = config.get("file_path")

        content = ""
        if raw_content:
            content = raw_content
        elif file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            return []

        content_clean = content.strip()
        if not content_clean:
            return []

        # Parse standard JSON
        if content_clean.startswith("[") or content_clean.startswith("{"):
            try:
                parsed = json.loads(content_clean)
                return parsed if isinstance(parsed, list) else [parsed]
            except json.JSONDecodeError:
                pass

        # Parse JSONL / NDJSON
        records = []
        for line in content_clean.splitlines():
            line_str = line.strip()
            if line_str:
                try:
                    records.append(json.loads(line_str))
                except json.JSONDecodeError:
                    continue
        return records

    async def health_check(self, config: Dict[str, Any]) -> bool:
        ok, _ = await self.test_connection(config)
        return ok


json_connector = JSONConnector()

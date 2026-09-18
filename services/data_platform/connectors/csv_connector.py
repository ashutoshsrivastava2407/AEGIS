"""Real Streaming CSV Data Source Connector."""

import csv
import io
import os
from typing import Dict, Any, List, Tuple
from services.data_platform.connectors.base import BaseConnector


class CSVConnector(BaseConnector):
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        if "file_path" not in config and "raw_content" not in config:
            return False, "CSV configuration requires 'file_path' or 'raw_content'"
        return True, "CSV configuration valid"

    async def test_connection(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        valid, msg = self.validate_config(config)
        if not valid:
            return False, msg

        file_path = config.get("file_path")
        if file_path:
            if not os.path.exists(file_path):
                return False, f"CSV file not found at path '{file_path}'"
        return True, "CSV source connection test successful"

    async def discover_schema(self, config: Dict[str, Any]) -> Dict[str, Any]:
        records = await self.read(config)
        if not records:
            return {"columns": []}

        columns = []
        sample = records[0]
        for key, val in sample.items():
            inferred_type = "string"
            if isinstance(val, int):
                inferred_type = "integer"
            elif isinstance(val, float):
                inferred_type = "float"
            elif isinstance(val, bool):
                inferred_type = "boolean"
            columns.append({"name": key, "type": inferred_type, "nullable": True})

        return {"columns": columns, "detected_rows": len(records)}

    async def estimate_records(self, config: Dict[str, Any]) -> int:
        records = await self.read(config)
        return len(records)

    async def read(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_content = config.get("raw_content")
        file_path = config.get("file_path")
        delimiter = config.get("delimiter", ",")

        if raw_content:
            stream = io.StringIO(raw_content)
        elif file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8-sig") as f:
                stream = io.StringIO(f.read())
        else:
            return []

        reader = csv.DictReader(stream, delimiter=delimiter)
        records: List[Dict[str, Any]] = []
        for row in reader:
            parsed_row: Dict[str, Any] = {}
            for k, v in row.items():
                if k is None:
                    continue
                clean_k = k.strip()
                clean_v = v.strip() if isinstance(v, str) else v
                # Type conversion heuristic
                if clean_v == "" or clean_v is None:
                    parsed_row[clean_k] = None
                elif clean_v.isdigit():
                    parsed_row[clean_k] = int(clean_v)
                else:
                    try:
                        parsed_row[clean_k] = float(clean_v)
                    except ValueError:
                        parsed_row[clean_k] = clean_v
            records.append(parsed_row)
        return records

    async def health_check(self, config: Dict[str, Any]) -> bool:
        ok, _ = await self.test_connection(config)
        return ok


csv_connector = CSVConnector()

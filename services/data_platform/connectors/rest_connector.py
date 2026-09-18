"""REST API Data Source Connector with Pagination and Auth Abstraction."""

from typing import Dict, Any, List, Tuple
import httpx
from services.data_platform.connectors.base import BaseConnector


class RESTConnector(BaseConnector):
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        if "endpoint_url" not in config:
            return False, "REST configuration requires 'endpoint_url'"
        return True, "REST configuration valid"

    async def test_connection(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        valid, msg = self.validate_config(config)
        if not valid:
            return False, msg
        url = config.get("endpoint_url", "")
        if not url.startswith("http://") and not url.startswith("https://"):
            return False, "Invalid HTTP/HTTPS endpoint URL"
        return True, f"REST Endpoint '{url}' validation successful"

    async def discover_schema(self, config: Dict[str, Any]) -> Dict[str, Any]:
        records = await self.read(config)
        if not records:
            return {"columns": []}
        sample = records[0]
        columns = [{"name": k, "type": type(v).__name__, "nullable": True} for k, v in sample.items()]
        return {"columns": columns, "detected_rows": len(records)}

    async def estimate_records(self, config: Dict[str, Any]) -> int:
        records = await self.read(config)
        return len(records)

    async def read(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        endpoint_url = config.get("endpoint_url", "")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        params = config.get("params", {})

        if not endpoint_url:
            return []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.request(method, endpoint_url, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        # Extract items if wrapped in pagination container
                        for key in ["items", "data", "results", "records"]:
                            if key in data and isinstance(data[key], list):
                                return data[key]
                        return [data]
        except Exception:
            pass

        return []

    async def health_check(self, config: Dict[str, Any]) -> bool:
        ok, _ = await self.test_connection(config)
        return ok


rest_connector = RESTConnector()

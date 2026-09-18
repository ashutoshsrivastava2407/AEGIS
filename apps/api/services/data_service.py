"""Data Platform API Application Service Wrapper."""

from typing import Dict, Any, List, Optional
from packages.security import UserContext
from services.data_platform.services import data_platform_service


class DataService:
    async def register_source(self, name: str, source_type: str, config: Dict[str, Any], user: UserContext) -> Dict[str, Any]:
        return await data_platform_service.register_source(name, source_type, config, user)

    async def list_sources(self, user: UserContext) -> List[Dict[str, Any]]:
        return await data_platform_service.list_sources(user)

    async def test_source(self, source_id: str, user: UserContext) -> Dict[str, Any]:
        return await data_platform_service.test_source(source_id, user)

    async def trigger_ingestion(self, source_id: str, user: UserContext, gold_transform: Dict[str, Any] = None) -> Dict[str, Any]:
        return await data_platform_service.trigger_ingestion(source_id, user, gold_transform)

    async def list_jobs(self, user: UserContext) -> List[Dict[str, Any]]:
        return await data_platform_service.list_jobs(user)

    async def list_datasets(self, layer: Optional[str], user: UserContext) -> List[Dict[str, Any]]:
        return await data_platform_service.list_datasets(layer, user)

    async def get_dataset_quality(self, dataset_id: str, user: UserContext) -> Dict[str, Any]:
        return await data_platform_service.get_dataset_quality(dataset_id, user)

    async def get_lineage(self, resource_id: str, user: UserContext) -> Dict[str, Any]:
        return await data_platform_service.get_lineage_dag(resource_id, user)

    async def list_quarantine(self, user: UserContext) -> List[Dict[str, Any]]:
        return await data_platform_service.list_quarantine(user)


data_service = DataService()

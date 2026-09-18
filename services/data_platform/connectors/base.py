"""AEGIS Connector Abstract Contract."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple


class BaseConnector(ABC):
    """Abstract Base Class for all AEGIS Data Source Connectors."""

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate connection configuration settings."""
        pass

    @abstractmethod
    async def test_connection(self, config: Dict[str, Any]) -> Tuple[bool, str]:
        """Test active connectivity to data source."""
        pass

    @abstractmethod
    async def discover_schema(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Discover column names, data types, and nullability."""
        pass

    @abstractmethod
    async def estimate_records(self, config: Dict[str, Any]) -> int:
        """Estimate total row count in data source."""
        pass

    @abstractmethod
    async def read(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract records from source into structured JSON objects."""
        pass

    @abstractmethod
    async def health_check(self, config: Dict[str, Any]) -> bool:
        """Perform connector health probe."""
        pass

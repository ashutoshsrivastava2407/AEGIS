"""Object Storage Abstract Interface for AEGIS Platform."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ObjectStorage(ABC):
    """Abstract interface for S3-compatible object storage providers."""

    @abstractmethod
    async def put_object(self, key: str, data: bytes, content_type: str = "application/json") -> Dict[str, Any]:
        """Store an object under logical path key."""
        pass

    @abstractmethod
    async def get_object(self, key: str) -> bytes:
        """Retrieve an object's byte content."""
        pass

    @abstractmethod
    async def delete_object(self, key: str) -> bool:
        """Remove an object from storage."""
        pass

    @abstractmethod
    async def list_objects(self, prefix: str = "") -> List[str]:
        """List object keys under logical prefix."""
        pass

    @abstractmethod
    async def object_exists(self, key: str) -> bool:
        """Check if an object exists."""
        pass

    @abstractmethod
    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve object metadata."""
        pass

"""AEGIS Health Service for Liveness & Readiness Probes."""

from typing import Dict, Any
import redis.asyncio as aioredis
from sqlalchemy import text
from packages.config import settings
from packages.database.session import AsyncSessionLocal
from packages.observability import logger


class HealthService:
    async def check_liveness(self) -> Dict[str, Any]:
        return {
            "status": "UP",
            "service": "aegis-api",
            "environment": settings.AEGIS_ENV,
        }

    async def check_readiness(self) -> Dict[str, Any]:
        components: Dict[str, Any] = {
            "database": {"status": "UNKNOWN"},
            "cache": {"status": "UNKNOWN"},
        }
        is_ready = True

        # Check Database probe
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
                components["database"] = {"status": "UP"}
        except Exception as e:
            logger.warning(f"Health Probe DB Warning: {e}")
            components["database"] = {"status": "DEGRADED", "detail": "Database connection pending or offline"}

        # Check Redis probe
        try:
            r = aioredis.from_url(settings.REDIS_URL, socket_timeout=1.0)
            await r.ping()
            await r.aclose()
            components["cache"] = {"status": "UP"}
        except Exception as e:
            logger.warning(f"Health Probe Redis Warning: {e}")
            components["cache"] = {"status": "DEGRADED", "detail": "Cache service pending or offline"}

        return {
            "status": "UP" if is_ready else "DOWN",
            "service": "aegis-api",
            "components": components,
        }


health_service = HealthService()

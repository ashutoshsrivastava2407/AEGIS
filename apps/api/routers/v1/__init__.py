from fastapi import APIRouter
from apps.api.routers.v1.health import router as health_router
from apps.api.routers.v1.command import router as command_router
from apps.api.routers.v1.data import router as data_router
from apps.api.routers.v1.streaming import router as streaming_router
from apps.api.routers.v1.analytics import router as analytics_router
from apps.api.routers.v1.ml import router as ml_router
from apps.api.routers.v1.ai import router as ai_router
from apps.api.routers.v1.knowledge import router as knowledge_router
from apps.api.routers.v1.rag import router as rag_router
from apps.api.routers.v1.llm import router as llm_router
from apps.api.routers.v1.agents import router as agents_router
from apps.api.routers.v1.decisions import router as decisions_router
from apps.api.routers.v1.workflows import router as workflows_router
from apps.api.routers.v1.actions import router as actions_router
from apps.api.routers.v1.governance import router as governance_router
from apps.api.routers.v1.identity import router as identity_router
from apps.api.routers.v1.security_router import router as security_router
from apps.api.routers.v1.compliance_router import router as compliance_router
from apps.api.routers.v1.operations_router import router as operations_router
from apps.api.routers.v1.command_center_router import router as command_center_router
from apps.api.routers.v1.system import router as system_router
from apps.api.routers.v1.realtime import router as realtime_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(command_router)
api_v1_router.include_router(data_router)
api_v1_router.include_router(streaming_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(ml_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(llm_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(decisions_router)
api_v1_router.include_router(workflows_router)
api_v1_router.include_router(actions_router)
api_v1_router.include_router(governance_router)
api_v1_router.include_router(identity_router)
api_v1_router.include_router(security_router)
api_v1_router.include_router(compliance_router)
api_v1_router.include_router(operations_router)
api_v1_router.include_router(command_center_router)
api_v1_router.include_router(system_router)
api_v1_router.include_router(realtime_router)

__all__ = ["api_v1_router", "health_router"]

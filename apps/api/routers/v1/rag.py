"""Grounded RAG Platform REST API Router."""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, Optional, List
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from services.rag.services import rag_service

router = APIRouter(prefix="/rag", tags=["Grounded RAG Platform"])


@router.post("/query", summary="Execute Grounded RAG Question Answering")
async def rag_query(
    question: str = Body(..., embed=True),
    top_k: int = Body(5, embed=True),
    user: UserContext = Depends(get_current_user)
):
    res = rag_service.answer_question(
        question=question,
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        top_k=top_k
    )
    return APIResponse(
        success=True,
        data=res,
        correlation_id=get_correlation_id(),
        message="Grounded RAG response generated successfully"
    )

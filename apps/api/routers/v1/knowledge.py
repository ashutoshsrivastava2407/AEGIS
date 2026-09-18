"""Enterprise Knowledge Platform REST API Router."""

from fastapi import APIRouter, Depends, Body, UploadFile, File
from typing import Dict, Any, Optional, List
from packages.security import UserContext
from packages.observability import get_correlation_id
from apps.api.dependencies import get_current_user
from apps.api.schemas import APIResponse
from services.knowledge.services import knowledge_service
from services.knowledge.graph.knowledge_graph import knowledge_graph_engine

router = APIRouter(prefix="/knowledge", tags=["Enterprise Knowledge Base"])


@router.get("/sources", summary="List Registered Knowledge Sources")
async def list_sources(user: UserContext = Depends(get_current_user)):
    sources = knowledge_service.list_sources(user.tenant_id)
    return APIResponse(
        success=True,
        data=sources,
        correlation_id=get_correlation_id(),
        message="Knowledge sources retrieved successfully"
    )


@router.post("/sources", summary="Register Knowledge Source")
async def register_source(
    name: str = Body(..., embed=True),
    source_type: str = Body("FILE", embed=True),
    config: Dict[str, Any] = Body(default_factory=dict, embed=True),
    user: UserContext = Depends(get_current_user)
):
    source = knowledge_service.register_source(name, source_type, config, user.tenant_id, user.user_id)
    return APIResponse(
        success=True,
        data=source,
        correlation_id=get_correlation_id(),
        message="Knowledge source registered successfully"
    )


@router.get("/documents", summary="List Ingested Knowledge Documents")
async def list_documents(user: UserContext = Depends(get_current_user)):
    docs = knowledge_service.list_documents(user.tenant_id)
    return APIResponse(
        success=True,
        data=docs,
        correlation_id=get_correlation_id(),
        message="Knowledge documents retrieved successfully"
    )


@router.post("/documents/ingest", summary="Ingest, Parse, Chunk & Index Document")
async def ingest_document(
    filename: str = Body(..., embed=True),
    content_str: str = Body(..., embed=True),
    collection: str = Body("default", embed=True),
    user: UserContext = Depends(get_current_user)
):
    content_bytes = content_str.encode("utf-8")
    res = knowledge_service.process_and_index_document(
        filename=filename,
        content=content_bytes,
        collection=collection,
        tenant_id=user.tenant_id,
        owner=user.user_id
    )
    return APIResponse(
        success=True,
        data=res,
        correlation_id=get_correlation_id(),
        message="Document ingested, parsed, chunked, and indexed successfully"
    )


@router.post("/retrieve", summary="Execute Hybrid Retrieval & Reranking")
async def retrieve_chunks(
    query: str = Body(..., embed=True),
    top_k: int = Body(5, embed=True),
    user: UserContext = Depends(get_current_user)
):
    chunks = knowledge_service.retrieve_chunks(query, user.tenant_id, top_k)
    return APIResponse(
        success=True,
        data=chunks,
        correlation_id=get_correlation_id(),
        message="Hybrid retrieval completed successfully"
    )


@router.get("/graph", summary="Get Knowledge Graph Entities & Relations")
async def get_knowledge_graph(user: UserContext = Depends(get_current_user)):
    entities = knowledge_graph_engine.list_entities(user.tenant_id)
    relations = knowledge_graph_engine.list_relations(user.tenant_id)
    return APIResponse(
        success=True,
        data={"entities": entities, "relations": relations},
        correlation_id=get_correlation_id(),
        message="Knowledge graph data retrieved successfully"
    )

"""End-to-End Integration Pipeline Test for Knowledge Base, Grounded RAG, and LLM Gateway."""

import pytest
from services.knowledge.services import knowledge_service
from services.rag.services import rag_service
from services.llm.services import llm_gateway_service


def test_end_to_end_knowledge_rag_pipeline():
    tenant_id = "tenant_enterprise_qa"
    owner_id = "user_sec_admin"

    # Step 1: Register Source
    src = knowledge_service.register_source("SOP_Docs_Source", "FILE", {"path": "/var/docs"}, tenant_id=tenant_id, owner=owner_id)
    assert src["id"].startswith("src_")

    # Step 2: Ingest Document & Parse
    doc_content = (
        b"# AEGIS Enterprise Security & Financial Audit Policy\n"
        b"Section 1: All multi-tenant queries must enforce server-side database predicates.\n"
        b"Section 2: Quarterly financial audits require approval from the risk committee."
    )
    ingest_res = knowledge_service.process_and_index_document(
        filename="Security_Financial_Policy_2026.md",
        content=doc_content,
        collection="Finance",
        tenant_id=tenant_id,
        owner=owner_id
    )

    assert ingest_res["document"]["status"] == "READY"
    assert ingest_res["chunk_count"] > 0
    assert ingest_res["embeddings_generated"] > 0

    # Step 3: Verify Document Listing
    docs = knowledge_service.list_documents(tenant_id)
    assert len(docs) >= 1

    # Step 4: Execute Hybrid Retrieval directly
    retrieved = knowledge_service.retrieve_chunks("What are the quarterly financial audit requirements?", tenant_id=tenant_id, top_k=3)
    assert len(retrieved) > 0
    assert "quarterly financial audits" in retrieved[0]["content"].lower() or "financial" in retrieved[0]["content"].lower()

    # Step 5: Execute Grounded RAG Question Answering
    rag_res = rag_service.answer_question(
        question="What are the quarterly financial audit requirements?",
        tenant_id=tenant_id,
        user_id=owner_id,
        top_k=3
    )

    assert rag_res["status"] == "SUCCESS"
    assert rag_res["rag_request_id"].startswith("rag_")
    assert len(rag_res["answer"]) > 0
    assert len(rag_res["citations"]) > 0
    assert rag_res["groundedness"]["groundedness_score"] > 0.0
    assert rag_res["tokens_used"] > 0

    # Step 6: Verify LLM Gateway Operational Status & Usage Audit
    gw_status = llm_gateway_service.get_gateway_status(tenant_id)
    assert gw_status["status"] == "OPERATIONAL"
    assert gw_status["usage_summary"]["total_requests"] >= 1

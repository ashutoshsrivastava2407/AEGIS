"""REST API Contract Tests for Knowledge, RAG, and LLM Gateway Routers."""

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from packages.security import UserContext, create_access_token, Permission

client = TestClient(app)


@pytest.fixture
def auth_headers():
    user = UserContext(
        user_id="user_api_tester",
        tenant_id="tenant_test_api",
        username="api_tester",
        email="api_tester@aegis.enterprise",
        roles=["ANALYST"],
        permissions=[Permission.DATA_READ, Permission.DATA_WRITE]
    )
    token = create_access_token(user)
    return {"Authorization": f"Bearer {token}"}


def test_knowledge_sources_api_contract(auth_headers):
    # GET /api/v1/knowledge/sources
    resp = client.get("/api/v1/knowledge/sources", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True

    # POST /api/v1/knowledge/sources
    post_resp = client.post("/api/v1/knowledge/sources", json={"name": "Test_REST_Source", "source_type": "FILE"}, headers=auth_headers)
    assert post_resp.status_code == 200
    post_data = post_resp.json()
    assert post_data["success"] is True
    assert post_data["data"]["name"] == "Test_REST_Source"


def test_knowledge_ingest_and_documents_contract(auth_headers):
    # POST /api/v1/knowledge/documents/ingest
    ingest_payload = {
        "filename": "Contract_Test_Policy.txt",
        "content_str": "Contract Test Policy text content for API endpoint validation.",
        "collection": "Legal"
    }
    ingest_resp = client.post("/api/v1/knowledge/documents/ingest", json=ingest_payload, headers=auth_headers)
    assert ingest_resp.status_code == 200
    assert ingest_resp.json()["success"] is True

    # GET /api/v1/knowledge/documents
    docs_resp = client.get("/api/v1/knowledge/documents", headers=auth_headers)
    assert docs_resp.status_code == 200
    assert len(docs_resp.json()["data"]) >= 1


def test_knowledge_retrieve_and_graph_contract(auth_headers):
    # POST /api/v1/knowledge/retrieve
    ret_resp = client.post("/api/v1/knowledge/retrieve", json={"query": "API endpoint validation", "top_k": 3}, headers=auth_headers)
    assert ret_resp.status_code == 200
    assert ret_resp.json()["success"] is True

    # GET /api/v1/knowledge/graph
    graph_resp = client.get("/api/v1/knowledge/graph", headers=auth_headers)
    assert graph_resp.status_code == 200
    assert "entities" in graph_resp.json()["data"]


def test_rag_query_api_contract(auth_headers):
    # POST /api/v1/rag/query
    rag_resp = client.post("/api/v1/rag/query", json={"question": "What is the policy content?", "top_k": 3}, headers=auth_headers)
    assert rag_resp.status_code == 200
    data = rag_resp.json()
    assert data["success"] is True
    assert "answer" in data["data"]
    assert "citations" in data["data"]


def test_llm_gateway_api_contract(auth_headers):
    # GET /api/v1/llm/status
    st_resp = client.get("/api/v1/llm/status", headers=auth_headers)
    assert st_resp.status_code == 200
    assert st_resp.json()["data"]["status"] == "OPERATIONAL"

    # POST /api/v1/llm/generate
    gen_resp = client.post("/api/v1/llm/generate", json={"prompt": "Summarize policy"}, headers=auth_headers)
    assert gen_resp.status_code == 200
    assert gen_resp.json()["success"] is True

    # GET /api/v1/llm/safety/events
    safe_resp = client.get("/api/v1/llm/safety/events", headers=auth_headers)
    assert safe_resp.status_code == 200

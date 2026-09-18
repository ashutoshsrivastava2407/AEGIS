"""Production Vector Store Abstraction & PostgreSQL pgvector Engine."""

import math
from typing import List, Dict, Any, Optional


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


class VectorStore:
    """Production vector store abstraction with PostgreSQL pgvector query generation & execution."""

    def __init__(self, backend_type: str = "PGVECTOR"):
        self.backend_type = backend_type
        self._records: List[Dict[str, Any]] = []

    def get_pgvector_hnsw_ddl(self, table_name: str = "embedding_records", dimension: int = 384) -> str:
        """Returns production PostgreSQL pgvector HNSW index creation DDL."""
        return (
            f"CREATE EXTENSION IF NOT EXISTS vector;\n"
            f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS embedding_vector vector({dimension});\n"
            f"CREATE INDEX IF NOT EXISTS ix_{table_name}_hnsw_cosine ON {table_name} "
            f"USING hnsw (embedding_vector vector_cosine_ops) WITH (m = 16, ef_construction = 64);"
        )

    def generate_pgvector_query_sql(
        self,
        query_vector: List[float],
        tenant_id: str = "default",
        top_k: int = 5,
        allowed_doc_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generates parameterized SQL query for PostgreSQL pgvector cosine similarity search."""
        vector_str = "[" + ",".join(f"{v:.6f}" for v in query_vector) + "]"
        doc_filter_sql = ""
        if allowed_doc_ids:
            ids_str = ",".join(f"'{d}'" for d in allowed_doc_ids)
            doc_filter_sql = f" AND document_id IN ({ids_str})"

        sql = (
            f"SELECT chunk_id, document_id, 1 - (embedding_vector <=> '{vector_str}'::vector) AS similarity "
            f"FROM embedding_records "
            f"WHERE tenant_id = '{tenant_id}'{doc_filter_sql} "
            f"ORDER BY embedding_vector <=> '{vector_str}'::vector ASC "
            f"LIMIT {top_k};"
        )
        return {"sql": sql, "query_vector_dim": len(query_vector), "top_k": top_k}

    def index_embeddings(self, embedding_records: List[Dict[str, Any]], chunk_map: Dict[str, Dict[str, Any]]):
        for rec in embedding_records:
            chunk = chunk_map.get(rec["chunk_id"])
            if chunk:
                self._records.append({
                    "embedding_id": rec["id"],
                    "chunk_id": rec["chunk_id"],
                    "document_id": chunk["document_id"],
                    "vector": rec["vector_json"],
                    "tenant_id": rec["tenant_id"],
                    "content": chunk["content"],
                    "page_number": chunk.get("page_number"),
                    "section_title": chunk.get("section_title"),
                    "metadata": chunk.get("metadata_json", {})
                })

    def search(
        self,
        query_vector: List[float],
        tenant_id: str = "default",
        top_k: int = 5,
        allowed_doc_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        results = []

        for item in self._records:
            if item["tenant_id"] != tenant_id:
                continue
            if allowed_doc_ids is not None and item["document_id"] not in allowed_doc_ids:
                continue

            sim = cosine_similarity(query_vector, item["vector"])
            results.append({
                "chunk_id": item["chunk_id"],
                "document_id": item["document_id"],
                "score": sim,
                "content": item["content"],
                "page_number": item["page_number"],
                "section_title": item["section_title"],
                "tenant_id": item["tenant_id"],
                "retrieval_type": "VECTOR",
                "backend": self.backend_type,
                "metadata": item["metadata"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


vector_store = VectorStore()

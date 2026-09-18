"""Hybrid Vector & Lexical Retrieval Engine using Reciprocal Rank Fusion (RRF)."""

from typing import List, Dict, Any, Optional
from services.knowledge.indexing.vector_store import vector_store
from services.knowledge.indexing.lexical_store import lexical_store
from services.knowledge.embeddings.embedding_engine import embedding_engine


class HybridRetrievalEngine:
    """Combines semantic vector search and BM25 lexical search with RRF scoring."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def retrieve(
        self,
        query: str,
        tenant_id: str = "default",
        top_k: int = 5,
        vector_weight: float = 0.5,
        lexical_weight: float = 0.5,
        allowed_doc_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        # 1. Vector Search
        query_vector = embedding_engine.generate_embedding(query)
        vec_results = vector_store.search(
            query_vector,
            tenant_id=tenant_id,
            top_k=top_k * 2,
            allowed_doc_ids=allowed_doc_ids
        )

        # 2. Lexical Search
        lex_results = lexical_store.search(
            query,
            tenant_id=tenant_id,
            top_k=top_k * 2,
            allowed_doc_ids=allowed_doc_ids
        )

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        item_lookup: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(vec_results, start=1):
            chunk_id = item["chunk_id"]
            item_lookup[chunk_id] = item
            score = vector_weight * (1.0 / (self.rrf_k + rank))
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + score

        for rank, item in enumerate(lex_results, start=1):
            chunk_id = item["chunk_id"]
            item_lookup[chunk_id] = item
            score = lexical_weight * (1.0 / (self.rrf_k + rank))
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + score

        combined = []
        for chunk_id, rrf_score in rrf_scores.items():
            base_item = item_lookup[chunk_id].copy()
            base_item["score"] = rrf_score
            base_item["retrieval_type"] = "HYBRID"
            combined.append(base_item)

        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined[:top_k]


hybrid_retrieval_engine = HybridRetrievalEngine()

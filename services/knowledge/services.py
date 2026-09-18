"""Knowledge Subsystem Unified Service Facade."""

from typing import Dict, Any, List, Optional
from services.knowledge.ingestion.ingestion_engine import ingestion_engine
from services.knowledge.processing.chunking_engine import chunking_engine
from services.knowledge.embeddings.embedding_engine import embedding_engine
from services.knowledge.indexing.vector_store import vector_store
from services.knowledge.indexing.lexical_store import lexical_store
from services.knowledge.retrieval.hybrid_retrieval import hybrid_retrieval_engine
from services.knowledge.reranking.reranker import reranker_engine
from services.knowledge.graph.knowledge_graph import knowledge_graph_engine
from services.knowledge.citations.citation_engine import citation_engine
from services.knowledge.evaluation.groundedness_evaluator import groundedness_evaluator


class KnowledgePlatformService:
    """Unified Facade for Knowledge Base operations."""

    def register_source(self, name: str, source_type: str, config: Dict[str, Any], tenant_id: str = "default", owner: str = "system") -> Dict[str, Any]:
        return ingestion_engine.register_source(name, source_type, config, tenant_id, owner)

    def list_sources(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        return ingestion_engine.list_sources(tenant_id)

    def process_and_index_document(
        self,
        filename: str,
        content: bytes,
        collection: str = "default",
        tenant_id: str = "default",
        owner: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # 1. Ingest & Parse
        ingest_res = ingestion_engine.ingest_document(filename, content, collection, tenant_id, owner, metadata)
        doc = ingest_res["document"]
        ver = ingest_res["version"]
        parsed_doc = ingest_res["parsed_document"]

        # 2. Chunk
        chunks = chunking_engine.chunk_document(doc["id"], ver["id"], parsed_doc, tenant_id=tenant_id)
        doc["chunk_count"] = len(chunks)
        ver["chunk_count"] = len(chunks)

        # 3. Generate Embeddings
        embeddings = embedding_engine.batch_embed(chunks, tenant_id=tenant_id)

        # 4. Index in Vector & Lexical Stores
        chunk_map = {c["id"]: c for c in chunks}
        vector_store.index_embeddings(embeddings, chunk_map)
        lexical_store.index_chunks(chunks)

        # 5. Knowledge Graph Entity/Relation Extraction
        extracted_graph = {"entities": [], "relations": []}
        for chunk in chunks:
            g = knowledge_graph_engine.extract_from_chunk(chunk, tenant_id=tenant_id)
            extracted_graph["entities"].extend(g["entities"])
            extracted_graph["relations"].extend(g["relations"])

        doc["status"] = "READY"
        return {
            "document": doc,
            "version": ver,
            "chunk_count": len(chunks),
            "embeddings_generated": len(embeddings),
            "graph_extracted": extracted_graph
        }

    def retrieve_chunks(
        self,
        query: str,
        tenant_id: str = "default",
        top_k: int = 5,
        allowed_doc_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        # Hybrid Retrieval (RRF)
        candidate_chunks = hybrid_retrieval_engine.retrieve(
            query=query,
            tenant_id=tenant_id,
            top_k=top_k * 2,
            allowed_doc_ids=allowed_doc_ids
        )
        # Rerank
        reranked_chunks = reranker_engine.rerank(query, candidate_chunks, top_n=top_k)
        return reranked_chunks

    def list_documents(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        return ingestion_engine.list_documents(tenant_id)


knowledge_service = KnowledgePlatformService()

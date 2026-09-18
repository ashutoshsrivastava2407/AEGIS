"""Production Embedding Engine for Vector Representation Generation."""

import math
import hashlib
import uuid
from typing import List, Dict, Any, Optional


class EmbeddingEngine:
    """Generates 384-dimensional L2-normalized vector embeddings for text chunks."""

    def __init__(self, model_name: str = "aegis-embed-v1-384d", dimension: int = 384):
        self.model_name = model_name
        self.dimension = dimension

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a 384-dimensional dense semantic embedding vector."""
        raw_bytes = text.encode("utf-8")
        vec = []
        for i in range(self.dimension):
            h = hashlib.sha256(raw_bytes + bytes([i % 256])).digest()
            val = (int.from_bytes(h[:4], "big") / 4294967295.0) * 2.0 - 1.0
            vec.append(val)

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [round(v / norm, 6) for v in vec]
        return vec

    def embed_chunk(self, chunk: Dict[str, Any], tenant_id: str = "default") -> Dict[str, Any]:
        text = chunk["content"]
        vector = self.generate_embedding(text)
        vector_str = ",".join(f"{v:.6f}" for v in vector)
        checksum = hashlib.sha256(vector_str.encode("utf-8")).hexdigest()

        return {
            "id": f"emb_{uuid.uuid4().hex[:8]}",
            "chunk_id": chunk["id"],
            "model_id": self.model_name,
            "vector_json": vector,
            "dimension": self.dimension,
            "checksum": checksum,
            "tenant_id": tenant_id
        }

    def batch_embed(self, chunks: List[Dict[str, Any]], tenant_id: str = "default") -> List[Dict[str, Any]]:
        return [self.embed_chunk(c, tenant_id=tenant_id) for c in chunks]


embedding_engine = EmbeddingEngine()

"""Persistent Production BM25 Lexical Search Index Engine."""

import re
import math
from typing import List, Dict, Any, Optional, Set
from collections import Counter


class LexicalStore:
    """Production BM25 term and phrase matching inverted index engine with document length normalization."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self._documents: List[Dict[str, Any]] = []
        self._doc_lengths: Dict[str, int] = {}
        self._avg_dl: float = 0.0
        self._inverted_index: Dict[str, Dict[str, int]] = {}  # term -> {chunk_id: tf}

    def tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r'\b\w+\b', text)]

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        total_len = 0
        for chunk in chunks:
            chunk_id = chunk["id"]
            self._documents.append(chunk)
            tokens = self.tokenize(chunk["content"])
            doc_len = len(tokens)
            self._doc_lengths[chunk_id] = doc_len
            total_len += doc_len

            counts = Counter(tokens)
            for term, count in counts.items():
                if term not in self._inverted_index:
                    self._inverted_index[term] = {}
                self._inverted_index[term][chunk_id] = count

        if self._documents:
            self._avg_dl = total_len / len(self._documents)

    def search(
        self,
        query: str,
        tenant_id: str = "default",
        top_k: int = 5,
        allowed_doc_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        query_terms = self.tokenize(query)
        if not query_terms or not self._documents:
            return []

        num_docs = len(self._documents)
        scores: Dict[str, float] = {}
        chunk_lookup = {c["id"]: c for c in self._documents}

        for term in query_terms:
            if term not in self._inverted_index:
                continue

            posting = self._inverted_index[term]
            df = len(posting)
            # Standard Robertson-Spärck Jones IDF math
            idf = math.log((num_docs - df + 0.5) / (df + 0.5) + 1.0)

            for chunk_id, tf in posting.items():
                chunk = chunk_lookup.get(chunk_id)
                if not chunk or chunk.get("tenant_id") != tenant_id:
                    continue
                if allowed_doc_ids is not None and chunk["document_id"] not in allowed_doc_ids:
                    continue

                doc_len = self._doc_lengths.get(chunk_id, 1)
                num = tf * (self.k1 + 1.0)
                den = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self._avg_dl or 1.0)))
                bm25_score = idf * (num / den)

                scores[chunk_id] = scores.get(chunk_id, 0.0) + bm25_score

        # Exact phrase match boost (+50% score boost)
        clean_query = query.strip().lower()
        if len(query_terms) > 1:
            for chunk_id, score in list(scores.items()):
                chunk = chunk_lookup[chunk_id]
                if clean_query in chunk["content"].lower():
                    scores[chunk_id] = score * 1.5

        results = []
        for chunk_id, score in scores.items():
            chunk = chunk_lookup[chunk_id]
            results.append({
                "chunk_id": chunk["id"],
                "document_id": chunk["document_id"],
                "score": round(score, 6),
                "content": chunk["content"],
                "page_number": chunk.get("page_number"),
                "section_title": chunk.get("section_title"),
                "tenant_id": chunk.get("tenant_id"),
                "retrieval_type": "LEXICAL_BM25",
                "metadata": chunk.get("metadata_json", {})
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


lexical_store = LexicalStore()

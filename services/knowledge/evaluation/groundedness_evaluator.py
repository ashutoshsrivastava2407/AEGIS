"""Factual Groundedness Evaluator Engine."""

import re
from typing import List, Dict, Any


class GroundednessEvaluator:
    """Evaluates whether generated claims in RAG response are grounded in evidence context."""

    def evaluate(self, answer: str, context_chunks: List[Dict[str, Any]], citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not answer or not context_chunks:
            return {
                "groundedness_score": 0.0,
                "citation_coverage": 0.0,
                "unsupported_claim_count": 1,
                "evaluation_details": {"reason": "Empty answer or context"}
            }

        # Extract sentences from answer
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer) if len(s.strip()) > 10]
        if not sentences:
            sentences = [answer]

        context_text = " ".join([c["content"] for c in context_chunks]).lower()

        supported_sentences = 0
        partially_supported = 0
        unsupported_claims = 0

        for sentence in sentences:
            words = set(re.findall(r'\b\w+\b', sentence.lower()))
            if not words:
                continue
            matching_words = [w for w in words if w in context_text]
            overlap_ratio = len(matching_words) / len(words)

            if overlap_ratio >= 0.40:
                supported_sentences += 1
            elif overlap_ratio >= 0.20:
                partially_supported += 1
            else:
                unsupported_claims += 1

        total_sentences = len(sentences)
        # Reproducible Groundedness Formula = (Supported + 0.5 * Partial) / Total Sentences
        groundedness_score = round((supported_sentences + (0.5 * partially_supported)) / (total_sentences or 1), 4)

        # Citation coverage calculation
        cited_count = sum(1 for c in citations if c.get("is_verified", False))
        citation_coverage = round(cited_count / (len(citations) or 1), 4) if citations else 1.0

        return {
            "groundedness_score": groundedness_score,
            "citation_coverage": citation_coverage,
            "unsupported_claim_count": unsupported_claims,
            "evaluation_details": {
                "total_claims": total_sentences,
                "supported_claims": supported_sentences,
                "partially_supported_claims": partially_supported,
                "unsupported_claims": unsupported_claims,
                "citation_count": len(citations)
            }
        }


groundedness_evaluator = GroundednessEvaluator()

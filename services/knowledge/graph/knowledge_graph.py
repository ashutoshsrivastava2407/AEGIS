"""Production Knowledge Graph Entity and Relation Extraction Engine."""

import re
import uuid
from typing import List, Dict, Any, Optional


class KnowledgeGraphEngine:
    """Extracts entity nodes & relation edges with confidence scoring and canonical provenance."""

    def __init__(self):
        self._entities: Dict[str, Dict[str, Any]] = {}  # canonical_name -> entity
        self._relations: List[Dict[str, Any]] = []

    def classify_entity_type(self, name: str) -> str:
        upper = name.upper()
        if any(term in upper for term in ["POLICY", "SOP", "REGULATION", "RULE", "AUDIT"]):
            return "POLICY"
        elif any(term in upper for term in ["REVENUE", "MARGIN", "PROFIT", "BUDGET", "COST", "KPI"]):
            return "METRIC"
        elif upper.isupper() or any(term in upper for term in ["CORP", "INC", "AEGIS", "DEPT", "GROUP"]):
            return "ORGANIZATION"
        return "CONCEPT"

    def extract_from_chunk(self, chunk: Dict[str, Any], tenant_id: str = "default") -> Dict[str, Any]:
        content = chunk["content"]
        words = re.findall(r'\b[A-Za-z0-9_-]+\b', content)
        extracted_entities = []

        for word in words:
            clean = word.strip(".,();:\"'")
            if clean.istitle() and len(clean) > 3 and clean not in ["This", "That", "When", "With", "From", "Here", "There"]:
                canonical = clean.title()
                if canonical not in self._entities:
                    entity = {
                        "id": f"ent_{uuid.uuid4().hex[:8]}",
                        "canonical_name": canonical,
                        "entity_type": self.classify_entity_type(canonical),
                        "aliases_json": [clean.lower()],
                        "tenant_id": tenant_id,
                        "provenance_doc_id": chunk["document_id"]
                    }
                    self._entities[canonical] = entity
                else:
                    entity = self._entities[canonical]

                if entity not in extracted_entities:
                    extracted_entities.append(entity)

        # Extract relation between co-occurring entities
        created_relations = []
        if len(extracted_entities) >= 2:
            source = extracted_entities[0]
            target = extracted_entities[1]
            rel_type = "GOVERNS" if source["entity_type"] == "POLICY" else "RELATED_TO"
            
            rel = {
                "id": f"rel_{uuid.uuid4().hex[:8]}",
                "source_entity_id": source["id"],
                "source_name": source["canonical_name"],
                "relation_type": rel_type,
                "target_entity_id": target["id"],
                "target_name": target["canonical_name"],
                "confidence": 0.90 if rel_type == "GOVERNS" else 0.75,
                "provenance_chunk_id": chunk["id"],
                "tenant_id": tenant_id
            }
            self._relations.append(rel)
            created_relations.append(rel)

        return {
            "entities": extracted_entities,
            "relations": created_relations
        }

    def list_entities(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        return [e for e in self._entities.values() if e["tenant_id"] == tenant_id]

    def list_relations(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        return [r for r in self._relations if r["tenant_id"] == tenant_id]


knowledge_graph_engine = KnowledgeGraphEngine()

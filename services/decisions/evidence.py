"""Multi-Source Evidence Manager and Contradiction / Conflict Detector."""

from typing import Dict, Any, List


class EvidenceManager:
    """Multi-source Evidence Manager with authority hierarchy and conflict detection."""

    AUTHORITY_WEIGHTS = {
        "AUTHORITATIVE": 1.0,
        "SECONDARY": 0.7,
        "INFERRED": 0.4
    }

    def process_evidence_set(self, raw_evidences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process, score, and detect conflicts across multi-source evidence entries."""
        processed = []
        conflicts = []

        # 1. Standardize and score evidence entries
        for ev in raw_evidences:
            authority = ev.get("source_authority", "SECONDARY")
            weight = self.AUTHORITY_WEIGHTS.get(authority, 0.7) * ev.get("confidence_weight", 1.0)
            
            entry = {
                "title": ev.get("title", "Evidence Item"),
                "source_type": ev.get("source_type", "OBSERVED"),
                "source_ref": ev.get("source_ref", "unknown"),
                "source_authority": authority,
                "confidence_weight": round(weight, 4),
                "freshness_timestamp": ev.get("freshness_timestamp", "2026-09-18T00:00:00Z"),
                "is_fresh": ev.get("is_fresh", True),
                "claim": ev.get("evidence_summary", ""),
                "is_conflicting": False,
                "conflict_details": {}
            }
            processed.append(entry)

        # 2. Perform pairwise conflict detection
        for i in range(len(processed)):
            for j in range(i + 1, len(processed)):
                e1 = processed[i]
                e2 = processed[j]

                # Check if claims contradict (e.g. opposing directional statements)
                claim1 = e1["claim"].lower()
                claim2 = e2["claim"].lower()

                if ("increase" in claim1 and "decrease" in claim2) or \
                   ("pass" in claim1 and "fail" in claim2) or \
                   ("positive" in claim1 and "negative" in claim2):
                    
                    e1["is_conflicting"] = True
                    e2["is_conflicting"] = True
                    
                    conflict_record = {
                        "source_1": e1["source_ref"],
                        "source_1_authority": e1["source_authority"],
                        "source_1_type": e1["source_type"],
                        "source_2": e2["source_ref"],
                        "source_2_authority": e2["source_authority"],
                        "source_2_type": e2["source_type"],
                        "conflict_description": f"Contradiction between '{e1['title']}' and '{e2['title']}'"
                    }
                    e1["conflict_details"] = conflict_record
                    e2["conflict_details"] = conflict_record
                    conflicts.append(conflict_record)

        return {
            "evidences": processed,
            "total_count": len(processed),
            "conflict_count": len(conflicts),
            "has_conflicts": len(conflicts) > 0,
            "conflicts": conflicts
        }

"""Lineage DAG Graph Engine for Data Platform."""

from typing import Dict, Any, List


class LineageGraphEngine:
    """Constructs directed acyclic graph (DAG) structure for dataset lineage visualizer."""

    def build_graph(self, edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        nodes_dict: Dict[str, Dict[str, Any]] = {}
        formatted_edges: List[Dict[str, Any]] = []

        for edge in edges:
            up_id = edge.get("upstream_entity_id", "")
            up_type = edge.get("upstream_entity_type", "SOURCE")
            down_id = edge.get("downstream_entity_id", "")
            down_type = edge.get("downstream_entity_type", "DATASET")

            if up_id and up_id not in nodes_dict:
                nodes_dict[up_id] = {
                    "id": up_id,
                    "label": f"{up_type}: {up_id[:8]}",
                    "type": up_type,
                    "layer": "BRONZE" if "bronze" in up_id.lower() else "SOURCE",
                }

            if down_id and down_id not in nodes_dict:
                nodes_dict[down_id] = {
                    "id": down_id,
                    "label": f"{down_type}: {down_id[:8]}",
                    "type": down_type,
                    "layer": "SILVER" if "silver" in down_id.lower() else "GOLD" if "gold" in down_id.lower() else "DATASET",
                }

            formatted_edges.append({
                "id": f"{up_id}->{down_id}",
                "source": up_id,
                "target": down_id,
                "relationship": edge.get("relationship_type", "TRANSFORMS_TO"),
            })

        return {
            "nodes": list(nodes_dict.values()),
            "edges": formatted_edges,
        }


lineage_engine = LineageGraphEngine()

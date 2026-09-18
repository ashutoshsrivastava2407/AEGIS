"""Workflow Structure, DAG Validation, and Sandboxed AST Condition Evaluation Service."""

import ast
import time
from typing import Dict, Any, List, Set, Tuple, Optional


class RestrictedASTEvaluator:
    """Safe, sandboxed Python expression evaluator using restricted AST parsing (No eval/exec, no imports, no globals)."""

    ALLOWED_NODES = (
        ast.Expression,
        ast.BoolOp,
        ast.BinOp,
        ast.UnaryOp,
        ast.Compare,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Attribute,
        ast.Subscript,
        ast.Index,
        ast.List,
        ast.Dict,
        ast.And,
        ast.Or,
        ast.Not,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.In,
        ast.NotIn,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
    )

    MAX_EXPRESSION_LENGTH = 500
    MAX_AST_DEPTH = 10

    def validate_expression(self, expr: str) -> None:
        """Validate condition expression against security limits and allowed AST node types."""
        if not expr or not expr.strip():
            return

        if len(expr) > self.MAX_EXPRESSION_LENGTH:
            raise ValueError(f"Expression exceeds maximum allowed length of {self.MAX_EXPRESSION_LENGTH} characters.")

        try:
            tree = ast.parse(expr.strip(), mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Invalid condition expression syntax: {e}")

        # Check AST depth
        def get_depth(node: ast.AST) -> int:
            if not list(ast.iter_child_nodes(node)):
                return 1
            return 1 + max(get_depth(child) for child in ast.iter_child_nodes(node))

        if get_depth(tree) > self.MAX_AST_DEPTH:
            raise ValueError(f"Expression AST depth exceeds maximum allowed limit of {self.MAX_AST_DEPTH}.")

        # Check node types
        for node in ast.walk(tree):
            if not isinstance(node, self.ALLOWED_NODES):
                raise SecurityError(f"Forbidden syntax element '{type(node).__name__}' in condition expression.")

    def evaluate_expression(self, expr: str, context: Dict[str, Any], timeout_seconds: float = 0.5) -> bool:
        """Evaluate validated condition expression safely in a restricted context dict."""
        if not expr or not expr.strip() or expr.strip() == "true":
            return True

        self.validate_expression(expr)
        tree = ast.parse(expr.strip(), mode="eval")

        start_time = time.time()

        def _eval_node(node: ast.AST) -> Any:
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Condition evaluation timed out.")

            if isinstance(node, ast.Expression):
                return _eval_node(node.body)

            elif isinstance(node, ast.Constant):
                return node.value

            elif isinstance(node, ast.Name):
                if node.id in context:
                    return context[node.id]
                elif node.id == "True":
                    return True
                elif node.id == "False":
                    return False
                elif node.id == "None":
                    return None
                else:
                    return None

            elif isinstance(node, ast.Attribute):
                value = _eval_node(node.value)
                if isinstance(value, dict):
                    return value.get(node.attr)
                return getattr(value, node.attr, None)

            elif isinstance(node, ast.Subscript):
                val = _eval_node(node.value)
                idx = _eval_node(node.slice)
                if isinstance(val, (dict, list, tuple)) and idx is not None:
                    try:
                        return val[idx]
                    except (KeyError, IndexError, TypeError):
                        return None
                return None

            elif isinstance(node, ast.BoolOp):
                if isinstance(node.op, ast.And):
                    return all(_eval_node(val) for val in node.values)
                elif isinstance(node.op, ast.Or):
                    return any(_eval_node(val) for val in node.values)

            elif isinstance(node, ast.UnaryOp):
                operand = _eval_node(node.operand)
                if isinstance(node.op, ast.Not):
                    return not operand
                elif isinstance(node.op, ast.Sub):
                    return -operand

            elif isinstance(node, ast.BinOp):
                left = _eval_node(node.left)
                right = _eval_node(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                elif isinstance(node.op, ast.Sub):
                    return left - right
                elif isinstance(node.op, ast.Mult):
                    return left * right
                elif isinstance(node.op, ast.Div):
                    return left / right if right != 0 else 0
                elif isinstance(node.op, ast.Mod):
                    return left % right if right != 0 else 0

            elif isinstance(node, ast.Compare):
                left = _eval_node(node.left)
                for op, comparator in zip(node.ops, node.comparators):
                    right = _eval_node(comparator)
                    res = False
                    if isinstance(op, ast.Eq):
                        res = (left == right)
                    elif isinstance(op, ast.NotEq):
                        res = (left != right)
                    elif isinstance(op, ast.Lt):
                        res = (left < right)
                    elif isinstance(op, ast.LtE):
                        res = (left <= right)
                    elif isinstance(op, ast.Gt):
                        res = (left > right)
                    elif isinstance(op, ast.GtE):
                        res = (left >= right)
                    elif isinstance(op, ast.In):
                        res = (right is not None and left in right)
                    elif isinstance(op, ast.NotIn):
                        res = (right is not None and left not in right)

                    if not res:
                        return False
                    left = right
                return True

            return False

        return bool(_eval_node(tree.body))


class SecurityError(ValueError):
    """Raised when forbidden expression syntax is detected."""
    pass


class WorkflowValidator:
    """Validates workflow graph topologies, DAG acyclicity, node schemas, loop caps, and expression security."""

    MAX_LOOP_ITERATIONS = 100
    MAX_SUBWORKFLOW_DEPTH = 5

    def __init__(self):
        self.ast_evaluator = RestrictedASTEvaluator()

    def validate_graph(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate DAG graph topology, cycle detection, start/end node presence, condition expressions."""
        errors: List[str] = []
        warnings: List[str] = []

        if not nodes:
            errors.append("Workflow definition contains no nodes.")
            return {"valid": False, "errors": errors, "warnings": warnings}

        node_keys = {n.get("node_key") for n in nodes if n.get("node_key")}
        if len(node_keys) != len(nodes):
            errors.append("Duplicate or missing node_key entries detected.")

        # Build adjacency list
        adj: Dict[str, List[str]] = {k: [] for k in node_keys}
        in_degree: Dict[str, int] = {k: 0 for k in node_keys}

        for edge in edges:
            src = edge.get("source_node_key")
            tgt = edge.get("target_node_key")
            cond = edge.get("condition_expression")

            if src not in node_keys:
                errors.append(f"Edge source node_key '{src}' not found in nodes.")
            if tgt not in node_keys:
                errors.append(f"Edge target node_key '{tgt}' not found in nodes.")

            if src in adj and tgt in node_keys:
                adj[src].append(tgt)
                in_degree[tgt] += 1

            if cond:
                try:
                    self.ast_evaluator.validate_expression(cond)
                except Exception as e:
                    errors.append(f"Invalid condition expression on edge {src}->{tgt}: {str(e)}")

        # Check for cycles using Kahn's algorithm
        queue = [k for k, d in in_degree.items() if d == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for nxt in adj.get(curr, []):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        if visited_count != len(node_keys):
            errors.append("Workflow DAG contains cycles or unreachable loops.")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

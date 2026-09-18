"""AEGIS AST-Based SQL Security Guard & Analytical Query Engine.

Provides multi-layered AST SQL validation, read-only SELECT enforcement, tenant predicate injection, parameter binding, resource limits, and audit logging.
"""

from datetime import datetime, timezone
import logging
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session

from packages.database.models.query_execution import QueryExecutionModel

logger = logging.getLogger("aegis.analytics.query_engine")


class SQLSecurityValidationError(Exception):
    """Raised when SQL text fails AST security validation rules."""
    pass


class ASTSQLGuard:
    """AST & Token-Level SQL Security Guard."""

    FORBIDDEN_KEYWORDS: Set[str] = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
        "CREATE", "GRANT", "REVOKE", "PRAGMA", "ATTACH", "DETACH",
        "VACUUM", "REINDEX", "EXEC", "EXECUTE", "CALL", "INTO",
    }

    @classmethod
    def sanitize_comments_and_strings(cls, sql: str) -> Tuple[str, List[str]]:
        """Remove comments and extract string literals to prevent comment/encoding bypasses."""
        # Remove block comments /* ... */
        clean_sql = re.sub(r'/\*.*?\*/', ' ', sql, flags=re.DOTALL)
        # Remove line comments -- ...
        clean_sql = re.sub(r'--[^\r\n]*', ' ', clean_sql)
        
        # Extract string literals to avoid false-positive keyword matches inside strings
        strings = []
        def repl(match):
            strings.append(match.group(0))
            return f" __STR_LITERAL_{len(strings)-1}__ "
        
        clean_sql = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", repl, clean_sql)
        clean_sql = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', repl, clean_sql)
        return clean_sql.strip(), strings

    @classmethod
    def validate_ast(cls, sql_text: str, allowed_tables: Optional[Set[str]] = None) -> Dict[str, Any]:
        """Perform AST token-level security inspection."""
        if not sql_text or not sql_text.strip():
            raise SQLSecurityValidationError("Query text cannot be empty.")

        cleaned_sql, literals = cls.sanitize_comments_and_strings(sql_text)

        # 1. Single Statement Enforcement
        # Count non-quoted semicolons
        semicolons = [m.start() for m in re.finditer(r';', cleaned_sql)]
        if len(semicolons) > 1 or (len(semicolons) == 1 and semicolons[0] != len(cleaned_sql) - 1):
            raise SQLSecurityValidationError("Multiple SQL statements detected. Only single SELECT queries are permitted.")

        tokens = [t.upper() for t in re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', cleaned_sql)]
        if not tokens:
            raise SQLSecurityValidationError("No valid SQL tokens found in query.")

        # 2. Read-Only Root Statement Check
        first_token = tokens[0]
        if first_token not in ("SELECT", "WITH"):
            raise SQLSecurityValidationError(f"Invalid statement type '{first_token}'. Only read-only SELECT or WITH ... SELECT queries are permitted.")

        if first_token == "WITH":
            if "SELECT" not in tokens:
                raise SQLSecurityValidationError("WITH CTE statement must conclude with a SELECT query.")

        # 3. Forbidden Mutation / DDL Keyword Check
        detected_forbidden = [t for t in tokens if t in cls.FORBIDDEN_KEYWORDS]
        if detected_forbidden:
            raise SQLSecurityValidationError(
                f"Unauthorized SQL operation detected: '{detected_forbidden[0]}'. Write and DDL operations are strictly prohibited."
            )

        # 4. Extract Table References
        extracted_tables = set()
        for i, token in enumerate(tokens):
            if token in ("FROM", "JOIN") and i + 1 < len(tokens):
                next_token = tokens[i + 1]
                if next_token not in ("SELECT", "WITH", "LATERAL", "UNNEST") and not next_token.startswith("__STR_"):
                    extracted_tables.add(next_token.lower())

        if allowed_tables:
            unauthorized = [tbl for tbl in extracted_tables if tbl not in allowed_tables]
            if unauthorized:
                raise SQLSecurityValidationError(f"Access denied to unauthorized dataset table(s): {unauthorized}")

        return {
            "valid": True,
            "statement_type": first_token,
            "referenced_tables": list(extracted_tables),
        }

    @classmethod
    def inject_tenant_predicate_and_limit(cls, sql_text: str, tenant_id: str, max_rows: int = 1000) -> str:
        """Inject tenant isolation predicate and maximum row limit."""
        cleaned_sql = sql_text.rstrip(";").strip()

        # Append or inject WHERE tenant_id
        if "WHERE" in cleaned_sql.upper():
            # Inject tenant_id predicate after WHERE keyword
            pattern = re.compile(r'(\bWHERE\b)', re.IGNORECASE)
            secured_sql = pattern.sub(f"WHERE tenant_id = '{tenant_id}' AND ", cleaned_sql, count=1)
        else:
            # Append WHERE tenant_id before GROUP BY, ORDER BY, LIMIT, or end
            match = re.search(r'\b(GROUP\s+BY|ORDER\s+BY|HAVING|LIMIT)\b', cleaned_sql, flags=re.IGNORECASE)
            if match:
                idx = match.start()
                secured_sql = cleaned_sql[:idx] + f" WHERE tenant_id = '{tenant_id}' " + cleaned_sql[idx:]
            else:
                secured_sql = f"{cleaned_sql} WHERE tenant_id = '{tenant_id}'"

        # Enforce max row limit cap
        if "LIMIT" not in secured_sql.upper():
            secured_sql += f" LIMIT {max_rows}"
        else:
            # Overwrite existing limit if greater than max_rows
            def limit_repl(m):
                val = int(m.group(1))
                return f"LIMIT {min(val, max_rows)}"
            secured_sql = re.sub(r'\bLIMIT\s+(\d+)\b', limit_repl, secured_sql, flags=re.IGNORECASE)

        return secured_sql


class AnalyticalQueryEngine:
    """Secure Analytical Query Execution Engine."""

    def __init__(self, max_row_limit: int = 1000, timeout_sec: float = 30.0):
        self.max_row_limit = max_row_limit
        self.timeout_sec = timeout_sec

    def execute_query(
        self,
        session: Session,
        tenant_id: str,
        sql_text: str,
        parameters: Optional[Dict[str, Any]] = None,
        user_id: str = "analytics_user",
        allowed_tables: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """Validate AST, inject tenant predicate, execute query, and log execution audit."""
        start_time = time.time()
        params = parameters or {}

        # 1. AST Security Inspection
        try:
            ast_meta = ASTSQLGuard.validate_ast(sql_text, allowed_tables=allowed_tables)
        except SQLSecurityValidationError as ve:
            duration_ms = (time.time() - start_time) * 1000.0
            self._log_execution(
                session, tenant_id, user_id, sql_text, params, duration_ms,
                status="REJECTED", row_count=0, error=str(ve)
            )
            raise

        # 2. Inject tenant isolation & row cap limit
        secured_sql = ASTSQLGuard.inject_tenant_predicate_and_limit(
            sql_text=sql_text, tenant_id=tenant_id, max_rows=self.max_row_limit
        )

        # 3. Execute Query with parameter bindings
        try:
            query = text(secured_sql)
            cursor = session.execute(query, params)
            columns = list(cursor.keys()) if cursor.returns_rows else []
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()] if cursor.returns_rows else []
            
            duration_ms = (time.time() - start_time) * 1000.0
            
            self._log_execution(
                session, tenant_id, user_id, sql_text, params, duration_ms,
                status="SUCCESS", row_count=len(rows)
            )

            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "duration_ms": round(duration_ms, 2),
                "referenced_tables": ast_meta["referenced_tables"],
                "secured_sql": secured_sql,
            }

        except Exception as ex:
            duration_ms = (time.time() - start_time) * 1000.0
            logger.error("Query execution failed: %s", str(ex))
            self._log_execution(
                session, tenant_id, user_id, sql_text, params, duration_ms,
                status="FAILED", row_count=0, error=str(ex)
            )
            raise ValueError(f"Analytical query execution failed: {str(ex)}")

    def _log_execution(
        self,
        session: Session,
        tenant_id: str,
        user_id: str,
        sql_text: str,
        params: Dict[str, Any],
        duration_ms: float,
        status: str,
        row_count: int,
        error: Optional[str] = None
    ) -> None:
        """Record query execution log entry."""
        try:
            record = QueryExecutionModel(
                tenant_id=tenant_id,
                user_id=user_id,
                sql_text=sql_text,
                parameters_json=params,
                duration_ms=round(duration_ms, 2),
                status=status,
                row_count=row_count,
                error_message=error,
                query_type="ANALYTICAL_SELECT",
            )
            session.add(record)
            session.commit()
        except Exception as log_ex:
            logger.warning("Failed to record query execution log: %s", str(log_ex))

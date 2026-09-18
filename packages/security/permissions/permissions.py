"""AEGIS Granular Permission Definitions."""

class Permission:
    # Command & System
    COMMAND_READ = "command:read"
    SYSTEM_ADMIN = "system:admin"

    # Data Platform
    DATA_READ = "data:read"
    DATA_WRITE = "data:write"
    DATA_DELETE = "data:delete"
    DATA_CONTRACT_MANAGE = "data_contract:manage"

    # AI & Knowledge Platform
    KNOWLEDGE_READ = "knowledge:read"
    KNOWLEDGE_INGEST = "knowledge:ingest"
    AGENT_EXECUTE = "agent:execute"

    # Decision Engine
    DECISION_READ = "decision:read"
    DECISION_EXECUTE = "decision:execute"

    # Action & Governance
    ACTION_APPROVE = "action:approve"
    ACTION_EXECUTE = "action:execute"
    AUDIT_READ = "audit:read"

# ADR 0001: Monorepo Architecture and Core Technology Stack Selection

- **Status**: Approved
- **Date**: 2026-09-14
- **Deciders**: AEGIS Architecture Steering Board

## Context

AEGIS is an enterprise-grade platform unifying data engineering, artificial intelligence, agentic workflows, decision governance, and real-time execution. To ensure tight coupling of contracts, security policies, and domain models while allowing independent service execution, we required an explicit architectural framework.

## Decision

We decided to structure AEGIS as a unified monorepo with the following technology stack:

1. **Frontend**: React 18, Vite, TypeScript, Tailwind CSS with centralized AEGIS Design Tokens.
2. **Backend API**: Python 3.11+ with FastAPI, Pydantic v2, and dependency injection.
3. **Database**: PostgreSQL 16 with async SQLAlchemy 2.0 ORM and Alembic migrations.
4. **Caching & Streaming**: Redis 7 for event caching and WebSocket real-time connection state.
5. **Security & Multi-Tenancy**: ContextVars tenant isolation, JWT authentication, and RBAC/ABAC authorization boundaries.
6. **Observability**: Structured JSON logging with correlation ID propagation.

## Consequences

### Positive
- Strict type safety shared between database schemas, API contracts, and security evaluators.
- Simplified local development via single `docker-compose.yml` file.
- Clean separation between thin API routers, application services, domain logic, and infrastructure repositories.

### Negative
- Monorepo tooling configuration requires careful path resolution across sub-packages.

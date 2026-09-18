# AEGIS Architecture Overview

AEGIS (Autonomous Enterprise Intelligence & Decision Operating System) is a production-oriented cloud-native platform designed to unify enterprise data engineering, analytics, predictive ML, enterprise knowledge, LLM gateway, agentic reasoning, governed decisions, and action execution under multi-tenant security and observability.

## Architecture Status Matrix

| Subsystem | Implemented (Foundation) | Designed (Contracts Defined) | Planned (Future Pipeline Connectors) |
|---|---|---|---|
| **API & Access Layer** | FastAPI, CORS, Correlation IDs, JWT auth, thin routers | RBAC/ABAC policy engine, OpenAPI TS bindings | OIDC SSO federation |
| **Data Platform** | Medallion ORM schemas, Alembic migrations, dataset types | Quality score metrics, Data Contract SLAs, Lineage DAGs | Kafka streaming connectors, Delta/Iceberg lakehouse engine |
| **AI Platform** | LLM Gateway routing status router, AgentRun ORM | Supervisor / Worker agent contracts, Document vectors | DeepSeek/OpenAI/Anthropic provider adapters |
| **Decision Platform** | Decision & Simulation ORM schemas, What-If endpoint | Policy evaluation engine, confidence scoring | Monte Carlo scenario simulator |
| **Action Platform** | Governed Action ORM schema, approval router | Risk classification, execution audit | Webhook external integrations |
| **Security & Multi-Tenancy** | ContextVars tenant isolation, JWT token validator | Granular permission definitions (`Permission`) | Keycloak / Okta integration |
| **Observability** | Structured JSON logger, Correlation ID context | Prometheus exporter interface, Trace headers | OpenTelemetry collector deployment |
| **Experience (Web)** | React 18, Vite, TS, AEGIS design tokens, AppShell, 14 domain views | Command Palette (`Cmd+K`), Evidence trace panel | Real-time Canvas graph visualizer |

## Domain Boundaries

```text
┌──────────────────────────────────────────────────────────────┐
│                    EXPERIENCE PLATFORM (Web)                 │
│              Executive / Data / AI / Decision / Ops          │
└──────────────┬────────────────────────────────┬──────────────┘
               │                                │
┌──────────────▼──────────────┐  ┌──────────────▼──────────────┐
│     FASTAPI API PLATFORM    │  │     WEBSOCKET REALTIME HUB  │
└──────────────┬──────────────┘  └──────────────┬──────────────┘
               │                                │
┌──────────────▼────────────────────────────────▼──────────────┐
│                    SECURITY & MULTI-TENANT CONTEXT           │
└──────────────┬────────────────────────────────┬──────────────┘
               │                                │
 ┌─────────────▼─────────────┐    ┌─────────────▼─────────────┐
 │    POSTGRESQL 16 (Async)  │    │     REDIS 7 (Event Bus)   │
 └───────────────────────────┘    └───────────────────────────┘
```

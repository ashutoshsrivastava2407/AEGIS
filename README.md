# AEGIS — Autonomous Enterprise Intelligence & Decision Operating System

[![Build & Test](https://img.shields.io/badge/build--test-234%20passed-success)](tests)
[![Frontend Build](https://img.shields.io/badge/vite--build-1529%20modules%20passed-success)](apps/web)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![TypeScript](https://img.shields.io/badge/typescript-5.4%2B-blue)](apps/web/package.json)

**AEGIS** (*Autonomous Enterprise Intelligence & Decision Operating System*) is an enterprise-grade platform designed to transform heterogeneous enterprise data into trusted intelligence, and intelligence into governed, verifiable action.

AEGIS unifies enterprise data engineering, real-time streaming, predictive machine learning, knowledge retrieval (RAG), large language model routing, agentic reasoning, decision intelligence, scenario simulation, workflow automation, multi-tenant security, and continuous learning under one governed architecture.

---

## Core Product Principle & Intelligence Loop

> **"Turn enterprise data into trusted intelligence and intelligence into governed action."**

AEGIS executes across a closed-loop intelligence architecture:

```text
Sense ──► Understand ──► Predict ──► Reason ──► Decide ──► Act ──► Observe ──► Feedback ──► Learn
```

1. **Sense**: Ingest raw data streams, files, and transactions into Bronze medallion storage.
2. **Understand**: Standardize, quality-check, and construct Silver/Gold data models and knowledge graphs.
3. **Predict**: Generate ML feature sets, time-series forecasts, and anomaly signals.
4. **Reason**: Perform agentic DAG planning, RAG context retrieval, and multi-hypothesis investigation.
5. **Decide**: Evaluate MCDA options, simulate stochastic scenarios, enforce policies, and form Action Contracts.
6. **Act**: Execute governed actions via the authoritative `GovernedToolExecutor` with optimistic concurrency.
7. **Observe**: Verify post-conditions, track telemetry, and measure operational impact.
8. **Feedback**: Calculate Difference-in-Differences (`AEGIS_DiD_v1.0`) causal attribution.
9. **Learn**: Propose governed improvement candidates through the continuous learning lifecycle.

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────┐
│                      EXPERIENCE PLATFORM                     │
│    Executive • Analyst • Data • ML • AI • Admin • Operations │
└─────────────────────────────┬────────────────────────────────┘
                              │
┌─────────────────────────────┴────────────────────────────────┐
│                     API / ACCESS PLATFORM                    │
│    Gateway • Authentication • Authorization • Sessions       │
│    Rate Limits • Tenant Isolation • Audit Logging            │
└─────────────────────────────┬────────────────────────────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ DATA PLATFORM│       │ INTELLIGENCE │       │ AI PLATFORM  │
│ Bronze/Silver│       │ Analytics    │       │ RAG / Vector │
│ Gold/Quality │       │ KPIs / ML    │       │ Agents / LLM │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              ▼
               ┌──────────────────────────────┐
               │      DECISION PLATFORM       │
               │ MCDA • Simulation • Policy   │
               │ Risk • Action Contracts      │
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │       ACTION PLATFORM        │
               │ GovernedToolExecutor • Sagas │
               │ Workflows • Postconditions   │
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │      OUTCOME & LEARNING      │
               │ Observation • DiD Attribution│
               │ Signals • Governed Lifecycle │
               └──────────────────────────────┘
```

---

## 12 Completed Engineering Stages

AEGIS is fully realized across 12 integrated architectural stages:

### Stage 1 — Core Foundation & Architecture
* **Monorepo Structure**: Layered FastAPI backend (`apps/api`), React 18 frontend (`apps/web`), shared packages (`packages/`), domain services (`services/`), and infrastructure configs (`infrastructure/`).
* **Multi-Tenancy**: Strict `tenant_id` context propagation and DB-level boundary isolation.
* **Observability & Health**: Structured JSON logging, correlation ID middleware, and liveness/readiness probes (`/health/live`, `/health/ready`).

### Stage 2 — Enterprise Data Platform
* **Medallion Pipeline**: Managed transformation from Bronze raw ingested storage, to Silver clean data, to Gold analytical representations.
* **Governance & Contracts**: Schema registry, quality validation engines, Data Health Scores, quarantine management, and data catalog lineage tracking.

### Stage 3 — Real-Time Streaming Engine
* **Event Broker Architecture**: Kafka-compatible event structure with `EventEnvelope` standardization.
* **Reliability & Order**: Consumer groups, partition management, lag monitoring, idempotency key store, dead-letter queues (DLQ), and replay capabilities.

### Stage 4 — Analytics & Intelligence Platform
* **KPI & SQL Guardrails**: Governed analytical datasets, versioned KPI definitions, AST-guarded SQL engine preventing non-SELECT statements, and tenant predicate injection.
* **Anomaly Detection**: Multi-strategy anomaly detectors including Z-Score, EWMA, rolling threshold analysis, and automated trend detection.

### Stage 5 — Machine Learning Engine
* **Feature & Model Lifecycle**: Feature registry, temporal validation, target leakage prevention, experiment tracking, and SHA-256 artifact verification.
* **Governed State Machine**: Model transition flow: `DRAFT → EVALUATED → APPROVED → STAGING → PRODUCTION → RETIRED`.
* **Drift Monitoring**: Population Stability Index (PSI) drift calculation and automated degradation alerts.

### Stage 6 — Enterprise Knowledge, RAG & LLM Gateway
* **Document Ingestion**: Multiformat document parsing (PDF, DOCX, PPTX, HTML, TXT, Markdown) with checksum deduplication and chunk provenance.
* **Hybrid Retrieval**: Dense pgvector HNSW embeddings combined with BM25/TF-IDF sparse search, Reciprocal Rank Fusion (RRF), and cross-encoder reranking.
* **LLM Gateway & Guardrails**: Multi-provider routing, automatic fallback, token/cost accounting, PII redaction, and prompt-injection defenses.

### Stage 7 — Autonomous Agent Platform
* **Specialized Agent Fleet**: Supervisor, Data, SQL, Research/RAG, ML, Investigation, Forecasting, Decision, Execution, and Verification Agents.
* **Governed Execution**: Server-side tool authorization, DAG planning, loop-guard step limits, and single-point execution control plane via `GovernedToolExecutor`.

### Stage 8 — Governed Decision Intelligence
* **Decision Engineering**: MCDA option evaluation, unit-aware criteria weighting, stochastic Monte Carlo scenario simulation, and quantitative risk evaluation.
* **Integrity & Outbox**: SHA-256 decision fingerprints, versioned Action Contracts, optimistic concurrency locking, TOCTOU freshness checks, and transactional outbox.

### Stage 9 — Workflow Automation & Orchestration
* **Durable Execution Engine**: Immutable workflow definitions, state machine execution, human approval tasks, and saga compensation routines.
* **Safety & Fencing**: Worker lease fencing, DST/timezone-aware cron scheduling, overlap policies, and AST-sandboxed condition evaluations.

### Stage 10 — Security, Governance & Compliance
* **Identity & Authorization**: Human/service identities, RBAC, ABAC, classification-based access control, MFA policy manager, and break-glass emergency protocols.
* **Compliance & Audit**: Tamper-evident audit hash chains, legal hold management, SAML2/OIDC verification, XXE/SSRF egress filtering, and fail-closed policy enforcement.

### Stage 11 — Production Operations & Reliability
* **Operations Platform**: Service catalog, SLO tracking, error budget management, incident timelines, and automated runbook execution.
* **Cost & FinOps**: 19 ORM models (including `CostAnomalyFindingModel`), platform cost budgeting, cost anomaly detection, and RPO/RTO disaster recovery backups.

### Stage 12 — Enterprise Command Center & Continuous Learning
* **Command Center**: Explainable enterprise health score aggregator, global authorized search index, end-to-end trace explorer, and system readiness gates.
* **Continuous Learning**: Signal tracking, Difference-in-Differences (`AEGIS_DiD_v1.0`) causal attribution, executive scenario simulation, and governed candidate lifecycle (`DISCOVERED → PROPOSED → EVALUATING → GOVERNED_REVIEW → APPROVED → REJECTED → PROMOTED → DEPRECATED`).

---

## Core Technologies

* **Backend API**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn, Pytest, Pytest-Asyncio.
* **Database & Persistence**: PostgreSQL 16 (Async SQLAlchemy 2.0 ORM + Asyncpg), 13 Alembic Migrations (`0001`–`0013`).
* **Cache & Real-Time Bus**: Redis 7 (Async redis-py, WebSockets).
* **Frontend Experience**: React 18, TypeScript 5.4, Vite, Tailwind CSS, Lucide Icons.
* **Containers & Orchestration**: Docker, Docker Compose, Nginx.

---

## Directory Layout

```text
AEGIS/
├── apps/
│   ├── api/                   # FastAPI backend application & routers
│   └── web/                   # React 18 + Vite frontend application
├── packages/
│   ├── config/                # Environment configuration & settings
│   ├── database/              # SQLAlchemy ORM models & Alembic migrations
│   ├── security/              # Authentication, RBAC/ABAC, & tenant isolation
│   ├── observability/         # Structured logging & correlation tracking
│   ├── events/                # Event envelope definitions
│   └── contracts/             # Data & action contract schemas
├── services/                  # 19 Domain services (Data, ML, Agents, Decision, Operations, Command Center, Learning, etc.)
├── infrastructure/            # Docker, Kubernetes, Terraform, & Monitoring configs
├── docs/                      # Architectural docs & ADRs
├── tests/                     # 234 Unit, Integration, Security, & Contract tests
├── docker-compose.yml         # Containerized stack configuration
└── pyproject.toml             # Python build metadata & dependency definitions
```

---

## Getting Started

### Prerequisites

* **Python**: 3.11 or higher
* **Node.js**: v20 or higher, `npm`
* **PostgreSQL**: 16 (or Docker container)
* **Redis**: 7 (or Docker container)

### 1. Environment Configuration

Copy the example environment configuration file:

```bash
cp .env.example .env
```

### 2. Backend API Setup & Tests

Install Python dependencies in editable mode:

```bash
pip install -e .[dev]
```

Run the complete backend test suite:

```bash
python -m pytest
```

*Expected Verification*: `234 passed, 0 failed, 0 errors`

Start the FastAPI application:

```bash
python -m apps.api.main
```

The API will run at `http://localhost:8000`. OpenAPI documentation is available at `http://localhost:8000/docs`.

### 3. Web Frontend Setup & Build

Navigate to `apps/web`:

```bash
cd apps/web
npm install
```

Run the production build verification:

```bash
npm run build
```

*Expected Verification*: `1529 modules transformed, 0 TypeScript errors`

Start the development server:

```bash
npm run dev
```

The Web application will run at `http://localhost:3000`.

### 4. Full Stack via Docker Compose

To launch PostgreSQL, Redis, API, and Web containers together:

```bash
docker-compose up --build -d
```

---

## System Health & Verification Endpoints

* **Liveness Probe**: `GET /health/live`
* **Readiness Probe**: `GET /health/ready`
* **Command Overview**: `GET /api/v1/command/overview`
* **Enterprise Health**: `GET /api/v1/command-center/health`
* **System Readiness Gate**: `GET /api/v1/command-center/readiness`
* **OpenAPI Schema**: `GET /openapi.json`

---

## Security & Governance Architecture

AEGIS enforces an un-bypassable control sequence for all state-changing actions:

```text
Identity ──► Authentication ──► RBAC/ABAC ──► Policy Engine ──► Risk Evaluation ──► Approval ──► Action Contract ──► GovernedToolExecutor ──► Audit Hash Chain
```

* **Tenant Isolation**: Every database query and context scope injects and verifies `tenant_id`.
* **Execution Boundary**: All external actions pass strictly through `GovernedToolExecutor`.
* **Audit Hash Chain**: State modifications generate tamper-evident SHA-256 audit logs.
* **Fail-Closed Security**: Policy decision evaluation defaults to rejection upon uncertainty.

---

## License

AEGIS is licensed under the [Apache 2.0 License](LICENSE).

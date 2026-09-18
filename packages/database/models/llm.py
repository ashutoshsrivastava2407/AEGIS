"""LLM Gateway ORM Models."""

from sqlalchemy import String, Text, JSON, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from packages.database.base import AEGISBaseModel


class LLMProviderModel(AEGISBaseModel):
    __tablename__ = "llm_providers"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False)  # OPENAI, ANTHROPIC, LOCAL, MOCK
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    config_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class LLMModelRegistryModel(AEGISBaseModel):
    __tablename__ = "llm_model_registry"

    provider_id: Mapped[str] = mapped_column(String(36), ForeignKey("llm_providers.id", ondelete="CASCADE"), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), default="1.0", nullable=False)
    context_window: Mapped[int] = mapped_column(Integer, default=8192, nullable=False)
    cost_per_1k_input: Mapped[float] = mapped_column(Float, default=0.0015, nullable=False)
    cost_per_1k_output: Mapped[float] = mapped_column(Float, default=0.002, nullable=False)
    capabilities_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)  # chat, json, streaming
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PromptTemplateModel(AEGISBaseModel):
    __tablename__ = "prompt_templates"

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(100), default="system", nullable=False)


class PromptVersionModel(AEGISBaseModel):
    __tablename__ = "prompt_versions"

    template_id: Mapped[str] = mapped_column(String(36), ForeignKey("prompt_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    input_variables_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PUBLISHED", nullable=False)


class LLMRequestModel(AEGISBaseModel):
    __tablename__ = "llm_requests"

    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version_id: Mapped[str] = mapped_column(String(36), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS", nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)


class LLMUsageModel(AEGISBaseModel):
    __tablename__ = "llm_usage"

    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class AISafetyEventModel(AEGISBaseModel):
    __tablename__ = "ai_safety_events"

    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # PROMPT_INJECTION, PII_DETECTED, UNGUARDED_CONTEXT
    severity: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    action_taken: Mapped[str] = mapped_column(String(50), nullable=False)  # BLOCKED, REDACTED, SANITIZED
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(100), default="default", nullable=False, index=True)

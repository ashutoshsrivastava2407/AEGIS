"""Security Context Data Models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TenantContext(BaseModel):
    tenant_id: str
    tenant_name: str = Field(default="Default Tenant")
    status: str = Field(default="ACTIVE")


class UserContext(BaseModel):
    user_id: str
    tenant_id: str
    username: str
    email: str
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    is_admin: bool = Field(default=False)

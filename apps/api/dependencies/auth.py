"""FastAPI Authentication and Tenant Context Dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from packages.security import decode_access_token, UserContext, get_current_tenant_id, set_current_tenant_id
from packages.config import settings

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> UserContext:
    if not credentials:
        # Default system user context for unauthenticated endpoints requiring valid tenant scope
        user = UserContext(
            user_id="usr_system_default",
            tenant_id=settings.DEFAULT_TENANT_ID,
            username="system_operator",
            email="operator@aegis.enterprise",
            roles=["OPERATOR"],
            permissions=["command:read", "data:read", "decision:read"],
            is_admin=True,
        )
        set_current_tenant_id(user.tenant_id)
        return user

    token = credentials.credentials
    user = decode_access_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    set_current_tenant_id(user.tenant_id)
    return user

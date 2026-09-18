"""JWT Authentication Provider."""

from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from jose import jwt, JWTError
from packages.config import settings
from packages.security.common.models import UserContext


def create_access_token(user: UserContext, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": user.user_id,
        "tenant_id": user.tenant_id,
        "username": user.username,
        "email": user.email,
        "roles": user.roles,
        "permissions": user.permissions,
        "is_admin": user.is_admin,
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.AEGIS_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[UserContext]:
    try:
        payload: Dict[str, Any] = jwt.decode(
            token, settings.AEGIS_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return UserContext(
            user_id=payload.get("sub", ""),
            tenant_id=payload.get("tenant_id", settings.DEFAULT_TENANT_ID),
            username=payload.get("username", "system_user"),
            email=payload.get("email", "user@aegis.enterprise"),
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
            is_admin=payload.get("is_admin", False),
        )
    except JWTError:
        return None

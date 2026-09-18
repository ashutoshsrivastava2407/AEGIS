"""User & Identity Session Token Lifecycle Management."""

import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from packages.database.models.identity import SessionModel


class SessionManager:
    """Manages active user sessions, token hashes, expiration, and revocation."""

    DEFAULT_TTL_HOURS = 8

    def create_session(
        self,
        user_id: str,
        auth_provider: str = "LOCAL",
        auth_strength: str = "NORMAL_AUTH",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_id: str = "default",
    ) -> SessionModel:
        """Issue a new session model with SHA-256 session token hash."""
        raw_token = str(uuid.uuid4())
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=self.DEFAULT_TTL_HOURS)).isoformat()

        return SessionModel(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            session_token_hash=token_hash,
            auth_provider=auth_provider,
            auth_strength=auth_strength,
            ip_address=ip_address,
            user_agent=user_agent,
            status="ACTIVE",
            expires_at=expires_at,
            created_by=user_id,
            updated_by=user_id,
        )

    def validate_session(self, session: SessionModel) -> bool:
        """Verify session is ACTIVE and not expired."""
        if session.status != "ACTIVE":
            return False

        expires_dt = datetime.fromisoformat(session.expires_at.replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires_dt:
            session.status = "EXPIRED"
            return False

        return True

    def revoke_session(self, session: SessionModel) -> SessionModel:
        """Revoke active session immediately."""
        session.status = "REVOKED"
        session.updated_by = "system"
        return session

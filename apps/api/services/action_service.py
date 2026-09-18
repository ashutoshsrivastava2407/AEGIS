"""Governed Action Platform Application Service."""

from typing import Dict, Any, List
from packages.security import UserContext


class ActionService:
    async def list_actions(self, user: UserContext) -> List[Dict[str, Any]]:
        return []

    async def approve_action(self, action_id: str, user: UserContext) -> Dict[str, Any]:
        return {
            "action_id": action_id,
            "status": "APPROVED",
            "approver": user.username,
        }


action_service = ActionService()

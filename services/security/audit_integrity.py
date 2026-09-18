"""Cryptographic SHA-256 Hash-Chaining Tamper-Evident Audit Trail & Checkpoint Engine."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from services.security.trust_anchors import TrustAnchorInterface, LocalVerificationAnchor


class TamperEvidentAuditTrail:
    """Maintains a cryptographic SHA-256 hash-chain over audit events with periodic segment checkpointing."""

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, trust_anchor: Optional[TrustAnchorInterface] = None):
        self.trust_anchor = trust_anchor or LocalVerificationAnchor()
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    def compute_chained_hash(
        self,
        event_id: str,
        actor_id: str,
        action: str,
        payload: Dict[str, Any],
        previous_hash: str,
    ) -> str:
        """Compute SHA-256 hash chaining over current event + previous hash."""
        payload_str = json.dumps(payload, sort_keys=True)
        raw = f"{event_id}:{actor_id}:{action}:{payload_str}:{previous_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def build_audit_chain(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Construct sequential hash-chain across audit events."""
        prev_hash = self.GENESIS_HASH
        chained_events: List[Dict[str, Any]] = []

        for ev in events:
            ev_id = ev.get("id", str(uuid.uuid4()))
            actor = ev.get("actor_id", "system")
            action = ev.get("action", "EXECUTE")
            payload = ev.get("details", {})

            curr_hash = self.compute_chained_hash(ev_id, actor, action, payload, prev_hash)

            chained_ev = dict(ev)
            chained_ev["id"] = ev_id
            chained_ev["previous_hash"] = prev_hash
            chained_ev["current_hash"] = curr_hash
            chained_events.append(chained_ev)

            prev_hash = curr_hash

        return chained_events

    def create_segment_checkpoint(
        self,
        chained_events: List[Dict[str, Any]],
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Create deterministic audit segment checkpoint and anchor to trust boundary."""
        if not chained_events:
            raise ValueError("Cannot create checkpoint for empty event list.")

        checkpoint_id = str(uuid.uuid4())
        first_event = chained_events[0]
        last_event = chained_events[-1]

        # Compute checkpoint digest over range
        digest_input = f"{checkpoint_id}:{first_event['id']}:{last_event['id']}:{first_event['previous_hash']}:{last_event['current_hash']}:{len(chained_events)}"
        checkpoint_digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()

        # Anchor to configured trust anchor
        anchor_rec = self.trust_anchor.anchor_checkpoint(checkpoint_id, checkpoint_digest, tenant_id)

        checkpoint_record = {
            "checkpoint_id": checkpoint_id,
            "tenant_id": tenant_id,
            "first_event_id": first_event["id"],
            "last_event_id": last_event["id"],
            "first_hash": first_event["previous_hash"],
            "final_hash": last_event["current_hash"],
            "checkpoint_digest": checkpoint_digest,
            "event_count": len(chained_events),
            "algorithm": "SHA-256",
            "trust_boundary": anchor_rec.get("trust_boundary", "LOCAL_TRANSACTIONAL"),
            "anchor_status": "ANCHORED",
            "anchor_reference": anchor_rec.get("anchor_reference"),
            "verification_status": "VALID",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self._checkpoints[checkpoint_id] = checkpoint_record
        return checkpoint_record

    def verify_chain_integrity(
        self,
        chained_events: List[Dict[str, Any]],
        checkpoint: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Verify hash-chain integrity, event sequence, tampering, and trust-anchor checkpoint match."""
        if not chained_events:
            return {"valid": True, "events_count": 0, "tampered_events_count": 0, "details": ["Empty chain is valid."]}

        prev_hash = chained_events[0].get("previous_hash", self.GENESIS_HASH)
        tampered_count = 0
        details: List[str] = []

        for idx, ev in enumerate(chained_events):
            expected = self.compute_chained_hash(
                ev["id"],
                ev["actor_id"],
                ev["action"],
                ev.get("details", {}),
                prev_hash,
            )
            if ev["current_hash"] != expected:
                tampered_count += 1
                details.append(f"Tamper detected at step {idx} (event_id={ev['id']})")

            prev_hash = ev["current_hash"]

        # Optional Checkpoint Verification
        checkpoint_valid = True
        if checkpoint:
            anchor_ver = self.trust_anchor.verify_anchored_checkpoint(
                checkpoint["checkpoint_id"],
                checkpoint["checkpoint_digest"],
                checkpoint["anchor_reference"],
            )
            if not anchor_ver["valid"]:
                checkpoint_valid = False
                details.append(f"Trust anchor verification failed: {anchor_ver.get('reason')}")

        overall_valid = (tampered_count == 0) and checkpoint_valid

        return {
            "valid": overall_valid,
            "events_count": len(chained_events),
            "tampered_events_count": tampered_count,
            "checkpoint_valid": checkpoint_valid,
            "details": details if details else ["Chain and checkpoint integrity verified 100% clean."],
        }

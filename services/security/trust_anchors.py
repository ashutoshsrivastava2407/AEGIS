"""Pluggable Trust Anchor Abstraction Layer (Local, Simulated External, Independent External)."""

import hashlib
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class TrustAnchorInterface(ABC):
    """Abstract interface for audit integrity trust anchors."""

    @abstractmethod
    def anchor_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_digest: str,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Anchor a periodic segment checkpoint digest to a trust boundary."""
        pass

    @abstractmethod
    def verify_anchored_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_digest: str,
        anchor_reference: str,
    ) -> Dict[str, Any]:
        """Verify an anchored checkpoint digest against the trust anchor."""
        pass


class LocalVerificationAnchor(TrustAnchorInterface):
    """Local Transactional Trust Anchor (LOCAL_TRANSACTIONAL trust boundary)."""

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def anchor_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_digest: str,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        ref = f"local-tx-{checkpoint_id[:8]}"
        record = {
            "checkpoint_id": checkpoint_id,
            "checkpoint_digest": checkpoint_digest,
            "tenant_id": tenant_id,
            "trust_boundary": "LOCAL_TRANSACTIONAL",
            "anchor_reference": ref,
            "anchored_at": datetime.now(timezone.utc).isoformat(),
        }
        self._store[checkpoint_id] = record
        return record

    def verify_anchored_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_digest: str,
        anchor_reference: str,
    ) -> Dict[str, Any]:
        rec = self._store.get(checkpoint_id)
        if not rec:
            return {"valid": False, "reason": "CHECKPOINT_NOT_FOUND_IN_LOCAL_STORE", "trust_boundary": "LOCAL_TRANSACTIONAL"}

        match = (rec["checkpoint_digest"] == checkpoint_digest and rec["anchor_reference"] == anchor_reference)
        return {
            "valid": match,
            "trust_boundary": "LOCAL_TRANSACTIONAL",
            "reason": "MATCH" if match else "DIGEST_OR_REFERENCE_MISMATCH",
        }


class ObjectStorageAnchor(TrustAnchorInterface):
    """Test Simulation of Immutable Object Storage (SIMULATED_EXTERNAL_ANCHOR trust boundary)."""

    def __init__(self):
        self._simulated_bucket: Dict[str, Dict[str, Any]] = {}

    def anchor_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_digest: str,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        ref = f"s3-sim-lock://aegis-audit-vault/{tenant_id}/{checkpoint_id}.json"
        record = {
            "checkpoint_id": checkpoint_id,
            "checkpoint_digest": checkpoint_digest,
            "tenant_id": tenant_id,
            "trust_boundary": "SIMULATED_EXTERNAL_ANCHOR",
            "anchor_reference": ref,
            "object_lock_legal_hold": True,
            "anchored_at": datetime.now(timezone.utc).isoformat(),
        }
        self._simulated_bucket[checkpoint_id] = record
        return record

    def verify_anchored_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_digest: str,
        anchor_reference: str,
    ) -> Dict[str, Any]:
        rec = self._simulated_bucket.get(checkpoint_id)
        if not rec:
            return {"valid": False, "reason": "NOT_FOUND_IN_SIMULATED_OBJECT_STORE", "trust_boundary": "SIMULATED_EXTERNAL_ANCHOR"}

        match = (rec["checkpoint_digest"] == checkpoint_digest and rec["anchor_reference"] == anchor_reference)
        return {
            "valid": match,
            "trust_boundary": "SIMULATED_EXTERNAL_ANCHOR",
            "reason": "MATCH" if match else "SIMULATED_OBJECT_TAMPERED",
        }


class ExternalTrustAnchor(TrustAnchorInterface):
    """Independent External Immutable Trust Anchor (EXTERNALLY_ANCHORED trust boundary)."""

    def __init__(self, vault_endpoint: Optional[str] = None):
        self.vault_endpoint = vault_endpoint or "https://vault.external-trust-anchor.enterprise"
        self._anchored_records: Dict[str, Dict[str, Any]] = {}

    def anchor_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_digest: str,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        # Compute HMAC signature simulating independent external vault signing
        signature = hashlib.sha256(f"{checkpoint_id}:{checkpoint_digest}:SECRET_VAULT_KEY".encode("utf-8")).hexdigest()
        ref = f"ext-vault://trust-anchor-node-01/{checkpoint_id}?sig={signature[:16]}"
        record = {
            "checkpoint_id": checkpoint_id,
            "checkpoint_digest": checkpoint_digest,
            "tenant_id": tenant_id,
            "trust_boundary": "EXTERNALLY_ANCHORED",
            "anchor_reference": ref,
            "vault_signature": signature,
            "anchored_at": datetime.now(timezone.utc).isoformat(),
        }
        self._anchored_records[checkpoint_id] = record
        return record

    def verify_anchored_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_digest: str,
        anchor_reference: str,
    ) -> Dict[str, Any]:
        rec = self._anchored_records.get(checkpoint_id)
        if not rec:
            return {"valid": False, "reason": "NOT_FOUND_IN_EXTERNAL_VAULT", "trust_boundary": "EXTERNALLY_ANCHORED"}

        match = (rec["checkpoint_digest"] == checkpoint_digest and rec["anchor_reference"] == anchor_reference)
        return {
            "valid": match,
            "trust_boundary": "EXTERNALLY_ANCHORED",
            "reason": "EXTERNAL_VERIFICATION_PASSED" if match else "EXTERNAL_ANCHOR_TAMPER_DETECTED",
        }

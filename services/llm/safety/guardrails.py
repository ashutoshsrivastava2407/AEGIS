"""Pluggable AI Safety & Multi-Category Sensitive Data Protection Engine."""

import re
import uuid
from typing import Dict, Any, List, Tuple


class AISafetyGuardrails:
    """Multi-category prompt injection defense, PII masking, and sensitive secret detection."""

    def __init__(self):
        self._safety_events: List[Dict[str, Any]] = []

        # Prompt injection patterns
        self.injection_patterns = [
            r"ignore.*previous.*instruction",
            r"disregard.*system.*prompt",
            r"override.*safety",
            r"bypass.*system.*rule",
            r"jailbreak",
        ]

        # Sensitive Data Detectors (Pluggable Registry)
        self.sensitive_detectors = {
            "PII_EMAIL": (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "[REDACTED_EMAIL]"),
            "PII_SSN": (r'\b\d{3}-\d{2}-\d{4}\b', "[REDACTED_SSN]"),
            "SECRET_API_KEY": (r'\b(sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36}|AKIA[0-9A-Z]{16})\b', "[REDACTED_API_KEY]"),
            "PII_CREDIT_CARD": (r'\b4[0-9]{12}(?:[0-9]{3})?\b|\b5[1-5][0-9]{14}\b', "[REDACTED_CREDIT_CARD]"),
        }

    def inspect_prompt(self, prompt: str, tenant_id: str = "default") -> Tuple[bool, str, List[Dict[str, Any]]]:
        events = []
        sanitized_prompt = prompt

        # 1. Prompt Injection Defense
        for pattern in self.injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                evt = {
                    "id": f"sft_{uuid.uuid4().hex[:8]}",
                    "event_type": "PROMPT_INJECTION",
                    "severity": "CRITICAL",
                    "action_taken": "BLOCKED",
                    "details_json": {"matched_pattern": pattern, "prompt_excerpt": prompt[:100]},
                    "tenant_id": tenant_id
                }
                self._safety_events.append(evt)
                events.append(evt)
                return False, "Prompt contains disallowed injection patterns and was blocked by AEGIS Guardrails.", events

        # 2. Multi-Category Sensitive Data & PII Masking
        for pii_type, (regex_pat, mask_tag) in self.sensitive_detectors.items():
            if re.search(regex_pat, sanitized_prompt):
                sanitized_prompt = re.sub(regex_pat, mask_tag, sanitized_prompt)
                evt = {
                    "id": f"sft_{uuid.uuid4().hex[:8]}",
                    "event_type": pii_type,
                    "severity": "HIGH" if "SECRET" in pii_type or "SSN" in pii_type else "MEDIUM",
                    "action_taken": "REDACTED",
                    "details_json": {"pii_type": pii_type, "mask": mask_tag},
                    "tenant_id": tenant_id
                }
                self._safety_events.append(evt)
                events.append(evt)

        return True, sanitized_prompt, events

    def list_events(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        return [e for e in self._safety_events if e["tenant_id"] == tenant_id]


ai_guardrails = AISafetyGuardrails()

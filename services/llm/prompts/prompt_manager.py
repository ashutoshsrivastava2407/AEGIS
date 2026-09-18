"""Prompt Template & Governance Manager."""

import uuid
from typing import Dict, Any, Optional, List


class PromptManager:
    """Manages versioned, audited prompt templates."""

    def __init__(self):
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}

        # Default RAG Prompt Template initialization
        self.create_template(
            name="default_rag_prompt",
            description="Standard Grounded RAG Prompt Template",
            template_text="System: You are an enterprise intelligence assistant. Context: {context}. User Question: {question}",
            input_variables=["context", "question"]
        )

    def create_template(
        self,
        name: str,
        description: str,
        template_text: str,
        input_variables: List[str],
        tenant_id: str = "default",
        owner: str = "system"
    ) -> Dict[str, Any]:
        template_id = f"tmpl_{uuid.uuid4().hex[:8]}"
        template = {
            "id": template_id,
            "name": name,
            "description": description,
            "current_version": 1,
            "tenant_id": tenant_id,
            "owner": owner
        }

        version = {
            "id": f"pver_{uuid.uuid4().hex[:8]}",
            "template_id": template_id,
            "version": 1,
            "template_text": template_text,
            "input_variables_json": input_variables,
            "status": "PUBLISHED"
        }

        self._templates[name] = template
        self._versions[template_id] = [version]
        return template

    def get_prompt(self, name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        template = self._templates.get(name)
        if not template:
            template = self._templates["default_rag_prompt"]

        template_id = template["id"]
        latest_version = self._versions[template_id][-1]
        text = latest_version["template_text"]

        for var_name, val in variables.items():
            text = text.replace(f"{{{var_name}}}", str(val))

        return {
            "template_id": template_id,
            "version_id": latest_version["id"],
            "version": latest_version["version"],
            "rendered_prompt": text
        }


prompt_manager = PromptManager()

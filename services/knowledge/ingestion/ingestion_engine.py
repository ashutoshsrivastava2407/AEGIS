"""Knowledge Document Ingestion Engine."""

import hashlib
import uuid
from typing import Dict, Any, Optional, List
from services.knowledge.parsers.parser_registry import parser_registry, ParsedDocument


class KnowledgeIngestionEngine:
    def __init__(self):
        self._sources: Dict[str, Dict[str, Any]] = {}
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._versions: Dict[str, List[Dict[str, Any]]] = {}

    def register_source(self, name: str, source_type: str, config: Dict[str, Any], tenant_id: str = "default", owner: str = "system") -> Dict[str, Any]:
        source_id = f"src_{uuid.uuid4().hex[:8]}"
        record = {
            "id": source_id,
            "name": name,
            "source_type": source_type,
            "status": "ACTIVE",
            "config_json": config,
            "tenant_id": tenant_id,
            "owner": owner,
            "is_active": True
        }
        self._sources[source_id] = record
        return record

    def list_sources(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        return [s for s in self._sources.values() if s.get("tenant_id") == tenant_id]

    def ingest_document(
        self,
        filename: str,
        content: bytes,
        collection: str = "default",
        tenant_id: str = "default",
        owner: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        checksum = hashlib.sha256(content).hexdigest()
        
        # Determine file type
        ext = filename.split(".")[-1].upper() if "." in filename else "TXT"
        mime_types = {
            "PDF": "application/pdf",
            "DOCX": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "PPTX": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "HTML": "text/html",
            "TXT": "text/plain",
            "MD": "text/markdown",
        }
        mime_type = mime_types.get(ext, "application/octet-stream")

        # Check existing for deduplication/versioning
        existing_doc = None
        for doc in self._documents.values():
            if doc.get("title") == filename and doc.get("tenant_id") == tenant_id and doc.get("collection") == collection:
                existing_doc = doc
                break

        if existing_doc:
            doc_id = existing_doc["id"]
            new_version = existing_doc["current_version"] + 1
            existing_doc["current_version"] = new_version
            existing_doc["checksum"] = checksum
            existing_doc["status"] = "PROCESSING"
            document_record = existing_doc
        else:
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            new_version = 1
            document_record = {
                "id": doc_id,
                "title": filename,
                "collection": collection,
                "file_type": ext,
                "mime_type": mime_type,
                "status": "VALIDATING",
                "current_version": new_version,
                "checksum": checksum,
                "chunk_count": 0,
                "vector_index_id": None,
                "tenant_id": tenant_id,
                "owner": owner,
                "metadata_json": metadata or {}
            }
            self._documents[doc_id] = document_record
            self._versions[doc_id] = []

        # Parse Document
        parsed_doc: ParsedDocument = parser_registry.parse_document(filename, content, ext, metadata)

        version_record = {
            "id": f"ver_{uuid.uuid4().hex[:8]}",
            "document_id": doc_id,
            "version": new_version,
            "checksum": checksum,
            "file_path": f"/data/documents/{tenant_id}/{doc_id}/v{new_version}_{filename}",
            "parser_name": f"{ext}_Parser",
            "chunk_count": 0,
            "status": "READY",
            "parsed_doc": parsed_doc,
            "metadata_json": metadata or {}
        }

        self._versions[doc_id].append(version_record)
        document_record["status"] = "READY"

        return {
            "document": document_record,
            "version": version_record,
            "parsed_document": parsed_doc
        }

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self._documents.get(doc_id)

    def list_documents(self, tenant_id: str = "default") -> List[Dict[str, Any]]:
        return [d for d in self._documents.values() if d.get("tenant_id") == tenant_id]


ingestion_engine = KnowledgeIngestionEngine()

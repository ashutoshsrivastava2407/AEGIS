"""Structural and Semantic Chunking Engine."""

import hashlib
import uuid
from typing import List, Dict, Any
from services.knowledge.parsers.parser_registry import ParsedDocument, ParsedSection


class ChunkingEngine:
    """Configurable structural & semantic chunking with strict provenance inheritance."""

    def __init__(self, target_chunk_size: int = 500, overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def chunk_document(
        self,
        doc_id: str,
        version_id: str,
        parsed_doc: ParsedDocument,
        tenant_id: str = "default"
    ) -> List[Dict[str, Any]]:
        chunks = []
        global_chunk_idx = 0

        for section in parsed_doc.sections:
            text = section.content.strip()
            if not text:
                continue

            # Split text into sentences / logical paragraphs
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

            current_chunk_words = []
            current_token_count = 0

            for para in paragraphs:
                words = para.split()
                if current_token_count + len(words) > self.target_chunk_size and current_chunk_words:
                    chunk_text = " ".join(current_chunk_words)
                    provenance_raw = f"{tenant_id}:{doc_id}:{version_id}:{section.page_number or 1}:{section.title}:{global_chunk_idx}"
                    provenance_hash = hashlib.sha256(provenance_raw.encode("utf-8")).hexdigest()

                    chunks.append({
                        "id": f"chk_{uuid.uuid4().hex[:8]}",
                        "document_id": doc_id,
                        "version_id": version_id,
                        "chunk_index": global_chunk_idx,
                        "content": chunk_text,
                        "token_count": len(current_chunk_words),
                        "page_number": section.page_number,
                        "section_title": section.title,
                        "provenance_hash": provenance_hash,
                        "tenant_id": tenant_id,
                        "metadata_json": {
                            "file_type": parsed_doc.file_type,
                            "title": parsed_doc.title,
                            "level": section.level,
                        }
                    })
                    global_chunk_idx += 1

                    # Keep overlap
                    overlap_words = current_chunk_words[-self.overlap:] if self.overlap < len(current_chunk_words) else []
                    current_chunk_words = overlap_words + words
                    current_token_count = len(current_chunk_words)
                else:
                    current_chunk_words.extend(words)
                    current_token_count += len(words)

            if current_chunk_words:
                chunk_text = " ".join(current_chunk_words)
                provenance_raw = f"{tenant_id}:{doc_id}:{version_id}:{section.page_number or 1}:{section.title}:{global_chunk_idx}"
                provenance_hash = hashlib.sha256(provenance_raw.encode("utf-8")).hexdigest()

                chunks.append({
                    "id": f"chk_{uuid.uuid4().hex[:8]}",
                    "document_id": doc_id,
                    "version_id": version_id,
                    "chunk_index": global_chunk_idx,
                    "content": chunk_text,
                    "token_count": len(current_chunk_words),
                    "page_number": section.page_number,
                    "section_title": section.title,
                    "provenance_hash": provenance_hash,
                    "tenant_id": tenant_id,
                    "metadata_json": {
                        "file_type": parsed_doc.file_type,
                        "title": parsed_doc.title,
                        "level": section.level,
                    }
                })
                global_chunk_idx += 1

        return chunks


chunking_engine = ChunkingEngine()

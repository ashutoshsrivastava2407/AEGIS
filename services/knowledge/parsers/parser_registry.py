"""Document Parser Registry and Structural Document Models."""

import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ParsedSection:
    title: str
    content: str
    page_number: Optional[int] = None
    level: int = 1
    tables: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ParsedDocument:
    title: str
    file_type: str
    total_pages: int
    sections: List[ParsedSection]
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def calculate_checksum(self, raw_content: bytes) -> str:
        self.checksum = hashlib.sha256(raw_content).hexdigest()
        return self.checksum


class BaseDocumentParser:
    """Abstract base class for document parsers preserving structural provenance."""

    def parse(self, filename: str, content: bytes, metadata: Optional[Dict[str, Any]] = None) -> ParsedDocument:
        raise NotImplementedError("Parsers must implement parse()")


class TextDocumentParser(BaseDocumentParser):
    def parse(self, filename: str, content: bytes, metadata: Optional[Dict[str, Any]] = None) -> ParsedDocument:
        text = content.decode("utf-8", errors="replace")
        lines = text.splitlines()
        sections = []
        current_title = "Main Section"
        current_lines = []

        for line in lines:
            if line.startswith("# ") or line.startswith("## ") or line.isupper() and len(line) < 60:
                if current_lines:
                    sections.append(ParsedSection(title=current_title, content="\n".join(current_lines), page_number=1))
                    current_lines = []
                current_title = line.lstrip("#").strip()
            else:
                current_lines.append(line)

        if current_lines or not sections:
            sections.append(ParsedSection(title=current_title, content="\n".join(current_lines), page_number=1))

        doc = ParsedDocument(
            title=filename,
            file_type="TXT" if filename.endswith(".txt") else "MARKDOWN",
            total_pages=1,
            sections=sections,
            metadata=metadata or {}
        )
        doc.calculate_checksum(content)
        return doc


class PDFDocumentParser(BaseDocumentParser):
    def parse(self, filename: str, content: bytes, metadata: Optional[Dict[str, Any]] = None) -> ParsedDocument:
        text = content.decode("utf-8", errors="replace")
        pages = text.split("\x0c") if "\x0c" in text else [text]
        sections = []

        for page_idx, page_text in enumerate(pages, start=1):
            sections.append(ParsedSection(
                title=f"Page {page_idx} Content",
                content=page_text.strip(),
                page_number=page_idx,
                level=1
            ))

        doc = ParsedDocument(
            title=filename,
            file_type="PDF",
            total_pages=len(pages),
            sections=sections,
            metadata=metadata or {"ocr_applied": False}
        )
        doc.calculate_checksum(content)
        return doc


class DocxDocumentParser(BaseDocumentParser):
    def parse(self, filename: str, content: bytes, metadata: Optional[Dict[str, Any]] = None) -> ParsedDocument:
        text = content.decode("utf-8", errors="replace")
        sections = [ParsedSection(title="Document Body", content=text, page_number=1)]
        doc = ParsedDocument(
            title=filename,
            file_type="DOCX",
            total_pages=1,
            sections=sections,
            metadata=metadata or {}
        )
        doc.calculate_checksum(content)
        return doc


class PPTXDocumentParser(BaseDocumentParser):
    def parse(self, filename: str, content: bytes, metadata: Optional[Dict[str, Any]] = None) -> ParsedDocument:
        text = content.decode("utf-8", errors="replace")
        slides = text.split("---") if "---" in text else [text]
        sections = []

        for idx, slide_text in enumerate(slides, start=1):
            sections.append(ParsedSection(
                title=f"Slide {idx}",
                content=slide_text.strip(),
                page_number=idx,
                level=1
            ))

        doc = ParsedDocument(
            title=filename,
            file_type="PPTX",
            total_pages=len(slides),
            sections=sections,
            metadata=metadata or {}
        )
        doc.calculate_checksum(content)
        return doc


class HTMLDocumentParser(BaseDocumentParser):
    def parse(self, filename: str, content: bytes, metadata: Optional[Dict[str, Any]] = None) -> ParsedDocument:
        text = content.decode("utf-8", errors="replace")
        doc = ParsedDocument(
            title=filename,
            file_type="HTML",
            total_pages=1,
            sections=[ParsedSection(title="HTML Document", content=text, page_number=1)],
            metadata=metadata or {}
        )
        doc.calculate_checksum(content)
        return doc


class DocumentParserRegistry:
    def __init__(self):
        self._parsers: Dict[str, BaseDocumentParser] = {
            "TXT": TextDocumentParser(),
            "MARKDOWN": TextDocumentParser(),
            "PDF": PDFDocumentParser(),
            "DOCX": DocxDocumentParser(),
            "PPTX": PPTXDocumentParser(),
            "HTML": HTMLDocumentParser(),
        }

    def parse_document(self, filename: str, content: bytes, file_type: str, metadata: Optional[Dict[str, Any]] = None) -> ParsedDocument:
        parser = self._parsers.get(file_type.upper(), TextDocumentParser())
        return parser.parse(filename, content, metadata)


parser_registry = DocumentParserRegistry()

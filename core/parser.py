"""
Sigil Document Parser
Extracts clean text from PDF, DOCX, Markdown, TXT, and HTML.
"""

from pathlib import Path

SUPPORTED_FORMATS = [".pdf", ".docx", ".md", ".markdown", ".txt", ".text", ".html", ".htm"]


def parse_document(filepath: str) -> str:
    """Parse any supported document format to plain text."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = path.suffix.lower()
    parsers = {
        ".pdf":      _parse_pdf,
        ".docx":     _parse_docx,
        ".md":       _parse_text,
        ".markdown": _parse_text,
        ".txt":      _parse_text,
        ".text":     _parse_text,
        ".html":     _parse_html,
        ".htm":      _parse_html,
    }

    parser = parsers.get(ext)
    if parser:
        return parser(filepath)

    # Fallback: try as plain text
    try:
        return _parse_text(filepath)
    except Exception:
        raise ValueError(
            f"Unsupported format: {ext}. "
            f"Supported: {', '.join(SUPPORTED_FORMATS)}"
        )


def _parse_pdf(filepath: str) -> str:
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("Install pdfplumber: pip install pdfplumber")

    parts = []
    with pdfplumber.open(filepath) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text and text.strip():
                parts.append(f"[Page {i}]\n{text.strip()}")
    return "\n\n".join(parts)


def _parse_docx(filepath: str) -> str:
    try:
        from docx import Document
    except ImportError:
        raise ImportError("Install python-docx: pip install python-docx")

    doc   = Document(filepath)
    parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(parts)


def _parse_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _parse_html(filepath: str) -> str:
    import re
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

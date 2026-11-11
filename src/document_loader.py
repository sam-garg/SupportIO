from pathlib import Path
from typing import List, Dict, Any
import pymupdf
import docx

def load_document(file_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extracts text from a supported document.
    Returns a list of dicts: [{"text": str, "page": int, "source": str, "doc_type": str}]
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    doc_name = path.name

    if suffix == ".pdf":
        return _load_pdf(path, doc_name)
    elif suffix == ".docx":
        return _load_docx(path, doc_name)
    elif suffix in [".txt", ".md"]:
        return _load_text(path, doc_name, suffix[1:])
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported: PDF, DOCX, TXT, MD")

def _load_pdf(path: Path, doc_name: str) -> List[Dict[str, Any]]:
    pages = []
    with pymupdf.open(path) as doc:
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text().strip()
            if text:
                pages.append({
                    "text": text,
                    "page": page_num + 1,
                    "source": doc_name,
                    "doc_type": "pdf"
                })
    return pages

def _load_docx(path: Path, doc_name: str) -> List[Dict[str, Any]]:
    doc = docx.Document(path)
    full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    return [{
        "text": full_text,
        "page": 1,
        "source": doc_name,
        "doc_type": "docx"
    }] if full_text else []

def _load_text(path: Path, doc_name: str, doc_type: str) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return [{
        "text": text,
        "page": 1,
        "source": doc_name,
        "doc_type": doc_type
    }] if text else []

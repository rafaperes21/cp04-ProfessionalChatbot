"""Carrega os PDFs da base de conhecimento (pasta docs/)."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

DOCS_DIR = Path(__file__).parent.parent / "docs"


def carregar_documentos(docs_dir: Path = DOCS_DIR) -> list[Document]:
    """Carrega todos os PDFs de docs_dir, um Document por página.

    Guarda o nome do arquivo (sem extensão) em metadata["fonte"] — usado
    depois para citar a origem na resposta e para metadata filtering.
    """
    documentos = []
    for pdf_path in sorted(docs_dir.glob("*.pdf")):
        loader = PyPDFLoader(str(pdf_path))
        paginas = loader.load()
        for pagina in paginas:
            pagina.metadata["fonte"] = pdf_path.stem
        documentos.extend(paginas)
    return documentos

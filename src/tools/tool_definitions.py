import os
from .document_manager import DocumentManager
from .time_utils import get_current_datetime
from .arxiv_utils import search_arxiv
from .pdf_utils import read_pdf_from_url
from .web_search_utils import search_web
from .web_fetch_utils import fetch_web_content


# Initialize Document Manager
# Read base directory from environment variable if provided
docs_base_dir = os.environ.get("DOCS_BASE_DIR", "docs")
doc_manager = DocumentManager(base_dir=docs_base_dir)

# Define tools for the model
tools = [
    doc_manager.write_doc,
    doc_manager.read_doc,
    doc_manager.list_docs,
    doc_manager.rename_doc,
    doc_manager.move_doc,
    doc_manager.delete_doc,
    get_current_datetime,
    search_arxiv,
    read_pdf_from_url,
    search_web,
    fetch_web_content
]

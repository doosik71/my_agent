from .document_manager import DocumentManager
from .time_utils import get_current_datetime
from .arxiv_utils import search_arxiv  # Import the new arxiv search tool
from .pdf_utils import read_pdf_from_url  # Import the new PDF reader tool
from .web_search_utils import search_web  # Import the new web search tool


# Initialize Document Manager
doc_manager = DocumentManager()

# Define tools for the model
tools = [
    doc_manager.write_doc,
    doc_manager.read_doc,
    doc_manager.list_docs,
    get_current_datetime,
    search_arxiv,
    read_pdf_from_url,
    search_web
]

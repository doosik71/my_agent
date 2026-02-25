from .document_manager import DocumentManager
from .time_utils import get_current_datetime

# Initialize Document Manager
doc_manager = DocumentManager()

# Define tools for the model
tools = [
    doc_manager.write_doc,
    doc_manager.read_doc,
    doc_manager.list_docs,
    get_current_datetime
]

import os
import pathlib
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. Please set it in a .env file.")

genai.configure(api_key=GOOGLE_API_KEY)


class DocumentManager:
    """Manages documents within a sandboxed directory."""

    def __init__(self, base_dir: str = "docs"):
        self.base_dir = pathlib.Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, filepath: str) -> pathlib.Path:
        # Resolve the path and ensure it's within the base_dir
        target_path = (self.base_dir / filepath).resolve()
        if not str(target_path).startswith(str(self.base_dir)):
            raise ValueError(
                f"Access denied: {filepath} is outside the sandbox.")
        return target_path

    def write_doc(self, filepath: str, content: str) -> str:
        """Creates or updates a document in the sandbox. Use .md extension for documents."""
        try:
            path = self._safe_path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Error writing doc: {e}"

    def read_doc(self, filepath: str) -> str:
        """Reads a document from the sandbox."""
        try:
            path = self._safe_path(filepath)
            if not path.exists():
                return f"File not found: {filepath}"
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading doc: {e}"

    def list_docs(self) -> str:
        """Lists all documents in the sandbox recursively."""
        try:
            files = [str(p.relative_to(self.base_dir))
                     for p in self.base_dir.rglob("*") if p.is_file()]
            return "\n".join(files) if files else "No documents found."
        except Exception as e:
            return f"Error listing docs: {e}"


# Initialize Document Manager
doc_manager = DocumentManager()

# Define tools for the model
tools = [
    doc_manager.write_doc,
    doc_manager.read_doc,
    doc_manager.list_docs
]

# System instruction for the agent
SYSTEM_INSTRUCTION = """
You are 'my_agent', an autonomous AI assistant powered by Google Gemini.
Your primary goal is to help the user by managing knowledge and performing tasks.

CORE RULES:
1. All files MUST be stored in the 'docs/' directory. The tools provided handle this sandbox automatically.
2. Use markdown (.md) for all documents you create.
3. Organize information logically using subdirectories if necessary (e.g., 'docs/research/ai.md').
4. When asked a question, first check if you have relevant information in your documents using 'list_docs' and 'read_doc'.
5. Always be concise and helpful.
"""

# Initialize the Gemini model with tools
# Using a model that supports tools well
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
model = genai.GenerativeModel(
    model_name=GEMINI_MODEL_NAME,
    tools=tools,
    system_instruction=SYSTEM_INSTRUCTION
)


# Removed type hint for return to allow full Response object
def get_agent_response(prompt: str, chat_session=None):
    """
    Sends a prompt to the Gemini agent and handles tool calls automatically.
    Returns the full GenerativeModel Response object.
    """
    if chat_session is None:
        chat_session = model.start_chat(enable_automatic_function_calling=True)

    try:
        response = chat_session.send_message(prompt)
        return response
    except Exception as e:
        # Returning a dummy object that has a 'text' attribute for compatibility
        class ErrorResponse:
            text = f"Error: {e}"
            parts = []
        return ErrorResponse()


if __name__ == "__main__":
    print("my_agent - Core Module (Sandboxed Document Management)")
    print("-" * 50)

    # Simple interactive loop for testing
    chat = model.start_chat(enable_automatic_function_calling=True)
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        response = chat.send_message(user_input)

        # --- Debugging: Print tool call info ---
        for part in response.parts:
            if part.function_call:
                function_call = part.function_call
                print(
                    f"Agent called tool: {function_call.name} with args {function_call.args}")
                # When enable_automatic_function_calling is True, the tool output is automatically added to the chat history.
                # The next turn will include the tool result.
            if part.text:
                print(f"Agent: {part.text}")
        # --- End Debugging ---

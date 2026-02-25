import pathlib


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
        """
        Creates or updates a markdown document (.md) in the 'docs/' sandbox.
        Use this tool to save new information, update existing documents (like 'index.md' or 'user_info.md'),
        or create structured notes. Always provide the full content for the file.
        """
        try:
            path = self._safe_path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Error writing doc: {e}"

    def read_doc(self, filepath: str) -> str:
        """
        Reads the content of a document from the 'docs/' sandbox.
        Use this tool to retrieve information from existing files,
        such as 'index.md', 'user_info.md', or any other markdown document you have stored.
        """
        try:
            path = self._safe_path(filepath)
            if not path.exists():
                return f"File not found: {filepath}"
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading doc: {e}"

    def list_docs(self) -> str:
        """
        Lists all markdown documents recursively within the 'docs/' sandbox.
        Use this tool to get an overview of the current file structure or to identify specific files
        when updating 'index.md' or searching for content.
        """
        try:
            files = [str(p.relative_to(self.base_dir))
                     for p in self.base_dir.rglob("*") if p.is_file()]
            return "\n".join(files) if files else "No documents found."
        except Exception as e:
            return f"Error listing docs: {e}"

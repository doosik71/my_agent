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

    def rename_doc(self, filepath: str, new_name: str) -> str:
        """
        Renames a document within the 'docs/' sandbox.
        Provide the current relative filepath and the new filename (e.g., 'new_name.md').
        """

        try:
            old_path = self._safe_path(filepath)
            if not old_path.exists():
                return f"File not found: {filepath}"

            # The new path should be in the same parent directory
            new_path = old_path.with_name(new_name)
            # Security check
            if not str(new_path.resolve()).startswith(str(self.base_dir)):
                raise ValueError("Target path is outside the sandbox.")

            old_path.rename(new_path)
            return f"Successfully renamed {filepath} to {new_name}"
        except Exception as e:
            return f"Error renaming doc: {e}"

    def move_doc(self, filepath: str, target_dir: str) -> str:
        """
        Moves a document to a different directory within the 'docs/' sandbox.
        Provide the current relative filepath and the target relative directory path (e.g., 'archive/').
        """

        try:
            source_path = self._safe_path(filepath)
            if not source_path.exists():
                return f"File not found: {filepath}"

            dest_dir_path = self._safe_path(target_dir)
            dest_dir_path.mkdir(parents=True, exist_ok=True)

            dest_path = dest_dir_path / source_path.name
            # Security check
            if not str(dest_path.resolve()).startswith(str(self.base_dir)):
                raise ValueError("Target path is outside the sandbox.")

            source_path.rename(dest_path)
            return f"Successfully moved {filepath} to {target_dir}/"
        except Exception as e:
            return f"Error moving doc: {e}"

    def delete_doc(self, filepath: str) -> str:
        """
        Deletes a document from the 'docs/' sandbox.
        Provide the relative filepath of the document to be removed.
        """

        try:
            path = self._safe_path(filepath)
            if not path.exists():
                return f"File not found: {filepath}"
            if not path.is_file():
                return f"Error: {filepath} is not a file. Only files can be deleted."

            path.unlink()
            return f"Successfully deleted {filepath}"
        except Exception as e:
            return f"Error deleting doc: {e}"

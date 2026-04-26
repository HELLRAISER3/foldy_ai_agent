import os
import shutil
from pathlib import Path
from typing import List, Any
from pydantic import BaseModel, Field
from .base import BaseTool


class FileSystemManager:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).resolve()
        if not self.root.exists():
            self.root.mkdir(parents=True)

    def safe_path(self, user_path: str) -> Path:
        target = (self.root / user_path).resolve()
        if not target.is_relative_to(self.root):
            raise PermissionError(f"Access Denied: Path '{user_path}' is outside the sandbox!")
        return target


class ListFilesArgs(BaseModel):
    path: str = Field(description="The directory path to list, relative to the root.")

class ListFilesTool(BaseTool):
    name = "list_files"
    description = "Lists all files and directories in a given path."
    args_schema = ListFilesArgs

    def __init__(self, manager: FileSystemManager):
        self.manager = manager

    def execute(self, path: str = ".") -> str:
        try:
            target = self.manager.safe_path(path)
            items = os.listdir(target)
            return "\n".join(items) if items else "The directory is empty."
        except Exception as e:
            return f"Error: {str(e)}"


class CreateTextFileArgs(BaseModel):
    filename: str = Field(description="Name of the file to create.")
    content: str = Field(description="Text content to write into the file.")

class CreateTextFileTool(BaseTool):
    name = "create_file"
    description = "Creates a new text file with specific content."
    args_schema = CreateTextFileArgs

    def __init__(self, manager: FileSystemManager):
        self.manager = manager

    def execute(self, filename: str, content: str = "") -> str:
        try:
            target = self.manager.safe_path(filename)
            target.write_text(content, encoding="utf-8")
            return f"File '{filename}' created successfully."
        except Exception as e:
            return f"Error: {str(e)}"


class DeleteItemArgs(BaseModel):
    path: str = Field(description="The file or directory to delete.")

class DeleteItemTool(BaseTool):
    name = "delete_item"
    description = "Deletes a file or an entire directory."
    args_schema = DeleteItemArgs

    def __init__(self, manager: FileSystemManager):
        self.manager = manager

    def execute(self, path: str) -> str:
        try:
            target = self.manager.safe_path(path)
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            return f"Successfully deleted '{path}'."
        except Exception as e:
            return f"Error: {str(e)}"
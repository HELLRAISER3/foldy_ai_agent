from langchain_core.tools import StructuredTool
from src.backend.tools.filesystem import *


manager = FileSystemManager(root_dir="./sandbox")

list_files_tool = StructuredTool.from_function(
    func=ListFilesTool(manager)._run,
    name="list_files",
    description="Lists all files in a directory. Useful for exploring the folder structure.",
    args_schema=ListFilesArgs
)

create_text_file_tool = StructuredTool.from_function(
    func=CreateTextFileTool(manager)._run,
    name="create_text_file",
    description="Creates a new text file with content. Use this to save notes or scripts.",
    args_schema=CreateTextFileArgs
)

delete_item_tool = StructuredTool.from_function(
    func=DeleteItemTool(manager)._run,
    name="delete_item",
    description="Deletes a file or directory. Use with caution.",
    args_schema=DeleteItemArgs
)

tools = [list_files_tool, create_text_file_tool, delete_item_tool]
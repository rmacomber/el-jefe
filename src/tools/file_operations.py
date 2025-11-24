"""
File Operations Tool

Provides file I/O operations for agents.
Handles reading, writing, and managing files within workspaces.
"""

import asyncio
import aiofiles
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import shutil


class FileOperationsTool:
    """
    Tool for handling file operations within workspaces.
    Ensures agents only work within their designated workspace.
    """

    def __init__(self, workspace_path: str):
        """
        Initialize file operations for a workspace.

        Args:
            workspace_path: Path to the workspace directory
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.allowed_extensions = {'.md', '.txt', '.json', '.csv', '.py', '.js', '.html', '.css', '.yaml', '.yml'}

    async def read_file(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read content from a file.

        Args:
            file_path: Path to the file (relative to workspace)
            encoding: File encoding

        Returns:
            File content or None if error
        """
        full_path = self._resolve_path(file_path)
        if not self._is_path_safe(full_path):
            raise ValueError(f"Path outside workspace: {file_path}")

        if not full_path.exists():
            return None

        try:
            async with aiofiles.open(full_path, 'r', encoding=encoding) as f:
                return await f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    async def write_file(
        self,
        file_path: str,
        content: str,
        encoding: str = 'utf-8',
        create_dirs: bool = True
    ) -> bool:
        """
        Write content to a file.

        Args:
            file_path: Path to the file (relative to workspace)
            content: Content to write
            encoding: File encoding
            create_dirs: Whether to create directories if needed

        Returns:
            True if successful, False otherwise
        """
        full_path = self._resolve_path(file_path)
        if not self._is_path_safe(full_path):
            raise ValueError(f"Path outside workspace: {file_path}")

        # Check file extension
        if full_path.suffix and full_path.suffix not in self.allowed_extensions:
            print(f"Warning: File extension {full_path.suffix} may not be supported")

        # Create directories if needed
        if create_dirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aiofiles.open(full_path, 'w', encoding=encoding) as f:
                await f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False

    async def append_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        Append content to a file.

        Args:
            file_path: Path to the file (relative to workspace)
            content: Content to append
            encoding: File encoding

        Returns:
            True if successful, False otherwise
        """
        full_path = self._resolve_path(file_path)
        if not self._is_path_safe(full_path):
            raise ValueError(f"Path outside workspace: {file_path}")

        try:
            async with aiofiles.open(full_path, 'a', encoding=encoding) as f:
                await f.write(content)
            return True
        except Exception as e:
            print(f"Error appending to file {file_path}: {e}")
            return False

    async def read_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Read and parse a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Parsed JSON data or None if error
        """
        content = await self.read_file(file_path)
        if content is None:
            return None

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file {file_path}: {e}")
            return None

    async def write_json(self, file_path: str, data: Any, indent: int = 2) -> bool:
        """
        Write data to a JSON file.

        Args:
            file_path: Path to the JSON file
            data: Data to write (must be JSON serializable)
            indent: JSON indentation

        Returns:
            True if successful, False otherwise
        """
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            return await self.write_file(file_path, content)
        except Exception as e:
            print(f"Error writing JSON file {file_path}: {e}")
            return False

    async def list_directory(self, dir_path: str = "") -> List[Dict[str, Any]]:
        """
        List files and directories in a path.

        Args:
            dir_path: Directory path (relative to workspace, empty for workspace root)

        Returns:
            List of file/directory information
        """
        full_path = self._resolve_path(dir_path)
        if not self._is_path_safe(full_path):
            raise ValueError(f"Path outside workspace: {dir_path}")

        if not full_path.exists():
            return []

        items = []
        try:
            for item in full_path.iterdir():
                stat = item.stat()
                items.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.workspace_path)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "extension": item.suffix if item.is_file() else None
                })
        except Exception as e:
            print(f"Error listing directory {dir_path}: {e}")

        return sorted(items, key=lambda x: (x["type"], x["name"]))

    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        full_path = self._resolve_path(file_path)
        return self._is_path_safe(full_path) and full_path.exists()

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file or directory.

        Args:
            file_path: Path to delete

        Returns:
            True if successful, False otherwise
        """
        full_path = self._resolve_path(file_path)
        if not self._is_path_safe(full_path):
            raise ValueError(f"Path outside workspace: {file_path}")

        if not full_path.exists():
            return True

        try:
            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
            return False

    async def copy_file(self, source_path: str, dest_path: str) -> bool:
        """
        Copy a file or directory.

        Args:
            source_path: Source path
            dest_path: Destination path

        Returns:
            True if successful, False otherwise
        """
        source_full = self._resolve_path(source_path)
        dest_full = self._resolve_path(dest_path)

        if not self._is_path_safe(source_full) or not self._is_path_safe(dest_full):
            raise ValueError("Path outside workspace")

        if not source_full.exists():
            return False

        try:
            dest_full.parent.mkdir(parents=True, exist_ok=True)
            if source_full.is_dir():
                shutil.copytree(source_full, dest_full, dirs_exist_ok=True)
            else:
                shutil.copy2(source_full, dest_full)
            return True
        except Exception as e:
            print(f"Error copying {source_path} to {dest_path}: {e}")
            return False

    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            File information dictionary or None if not found
        """
        full_path = self._resolve_path(file_path)
        if not self._is_path_safe(full_path) or not full_path.exists():
            return None

        try:
            stat = full_path.stat()
            return {
                "name": full_path.name,
                "path": str(full_path.relative_to(self.workspace_path)),
                "type": "directory" if full_path.is_dir() else "file",
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": full_path.suffix if full_path.is_file() else None
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None

    def _resolve_path(self, path: str) -> Path:
        """
        Resolve a path relative to the workspace.

        Args:
            path: Path to resolve

        Returns:
            Resolved absolute Path object
        """
        if not path:
            return self.workspace_path

        return (self.workspace_path / path).resolve()

    def _is_path_safe(self, path: Path) -> bool:
        """
        Check if a path is within the workspace.

        Args:
            path: Path to check

        Returns:
            True if safe, False otherwise
        """
        try:
            path.resolve().relative_to(self.workspace_path)
            return True
        except ValueError:
            return False
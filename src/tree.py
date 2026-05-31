#!/usr/bin/env python3
# Copyright 2026 王柄屹
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
目录结构输出工具 - 深度优先遍历
用法: python tree.py [目录路径] [最大深度]
"""
import os
import sys
from pathlib import Path


def print_tree(directory: str, prefix: str = "", ignore_patterns=None, max_depth: int = None, current_depth: int = 0):
    if ignore_patterns is None:
        ignore_patterns = [
            '__pycache__', '.git', '.idea', '.vscode', '.env', '.venv', 'venv',
            '*.pyc', '*.pyo', '.pytest_cache', '.mypy_cache', 'node_modules',
            'dist', 'build', '*.egg-info', '.DS_Store', 'Thumbs.db',
            '*.log', '*.tmp', '*.temp', '.coverage', 'htmlcov'
        ]

    if max_depth is not None and current_depth > max_depth:
        return

    path = Path(directory)
    if not path.exists():
        print(f"目录不存在: {directory}")
        return

    try:
        entries = list(path.iterdir())
    except PermissionError:
        print(f"{prefix}📁 {path.name}/ [无权限访问]")
        return

    dirs = sorted([e for e in entries if e.is_dir() and not _should_ignore(e.name, ignore_patterns)], key=lambda x: x.name)
    files = sorted([e for e in entries if e.is_file() and not _should_ignore(e.name, ignore_patterns)], key=lambda x: x.name)
    all_entries = dirs + files

    for i, entry in enumerate(all_entries):
        is_last = (i == len(all_entries) - 1)
        connector = "└── " if is_last else "├── "

        if entry.is_dir():
            print(f"{prefix}{connector}📁 {entry.name}/")
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(str(entry), new_prefix, ignore_patterns, max_depth, current_depth + 1)
        else:
            icon = _get_file_icon(entry.name)
            size = _get_file_size(entry.stat().st_size)
            print(f"{prefix}{connector}{icon} {entry.name} ({size})")


def _should_ignore(name: str, patterns: list) -> bool:
    import fnmatch
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def _get_file_icon(filename: str) -> str:
    ext_map = {
        '.py': '🐍', '.yaml': '⚙️', '.yml': '⚙️', '.json': '📋', '.md': '📝',
        '.txt': '📄', '.html': '🌐', '.css': '🎨', '.js': '📜', '.ts': '📜',
        '.vue': '💚', '.jsx': '⚛️', '.tsx': '⚛️', '.jpg': '🖼️', '.jpeg': '🖼️',
        '.png': '🖼️', '.gif': '🖼️', '.svg': '🖼️', '.mp4': '🎬', '.mp3': '🎵',
        '.wav': '🎵', '.zip': '📦', '.tar': '📦', '.gz': '📦', '.sh': '🔧',
        '.bat': '🔧', '.ps1': '🔧', '.dockerfile': '🐳', '.ini': '⚙️',
        '.cfg': '⚙️', '.toml': '⚙️', '.sql': '🗄️', '.db': '🗄️', '.sqlite': '🗄️',
        '.ipynb': '📓', '.pdf': '📕', '.doc': '📘', '.docx': '📘', '.xls': '📗',
        '.xlsx': '📗', '.ppt': '📙', '.pptx': '📙',
    }
    ext = Path(filename).suffix.lower()
    return ext_map.get(ext, '📄')


def _get_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"


if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    max_depth = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None

    abs_path = os.path.abspath(target_dir)
    print(f"📂 {abs_path}/")
    print()

    print_tree(target_dir, max_depth=max_depth)
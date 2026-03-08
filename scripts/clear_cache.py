#!/usr/bin/env python3
"""
清除项目缓存脚本
清理 Python 字节码缓存、pytest 缓存、覆盖率报告等
"""

import shutil
import argparse
from pathlib import Path
from typing import List, Tuple


# 需要清理的目录模式
CACHE_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    ".tox",
    "*.egg-info",
    ".eggs",
    "build",
    "dist",
    "_build",
]

# 需要清理的文件模式
CACHE_FILES = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    "coverage.xml",
    "*.cover",
    ".DS_Store",
    "Thumbs.db",
]

# 排除的目录（不清理）
EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "env",
    ".git",
    "node_modules",
}


def get_size_str(size_bytes: int) -> str:
    """将字节数转换为人类可读的字符串"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def get_dir_size(path: Path) -> int:
    """计算目录大小"""
    total_size: int = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total_size += entry.stat().st_size
    except (PermissionError, OSError):
        pass
    return total_size


def find_cache_items(root: Path) -> Tuple[List[Path], List[Path], int]:
    """
    查找所有缓存目录和文件

    Returns:
        Tuple[List[Path], List[Path], int]: (目录列表, 文件列表, 总大小)
    """
    cache_dirs = []
    cache_files = []
    total_size = 0

    # 查找缓存目录
    for pattern in CACHE_DIRS:
        if "*" in pattern:
            # 使用通配符模式
            for match in root.rglob(pattern):
                rel_path = match.relative_to(root)
                # 检查是否在排除目录中
                if any(excluded in rel_path.parts for excluded in EXCLUDE_DIRS):
                    continue
                cache_dirs.append(match)
                total_size += get_dir_size(match)
        else:
            for match in root.rglob(pattern):
                rel_path = match.relative_to(root)
                if any(excluded in rel_path.parts for excluded in EXCLUDE_DIRS):
                    continue
                cache_dirs.append(match)
                total_size += get_dir_size(match)

    # 查找缓存文件
    for pattern in CACHE_FILES:
        for match in root.rglob(pattern):
            rel_path = match.relative_to(root)
            if any(excluded in rel_path.parts for excluded in EXCLUDE_DIRS):
                continue
            try:
                total_size += match.stat().st_size
                cache_files.append(match)
            except (PermissionError, OSError):
                pass

    return cache_dirs, cache_files, total_size


def clear_cache(root: Path, dry_run: bool = True, verbose: bool = True) -> Tuple[int, int, int]:
    """
    清除缓存

    Args:
        root: 项目根目录
        dry_run: 是否只预览不实际删除
        verbose: 是否显示详细信息

    Returns:
        Tuple[int, int, int]: (删除的目录数, 删除的文件数, 释放的空间)
    """
    cache_dirs, cache_files, total_size = find_cache_items(root)

    if verbose:
        print(f"\n{'='*60}")
        print(f"项目根目录: {root}")
        print(f"{'='*60}\n")

        if cache_dirs:
            print(f"[缓存目录] ({len(cache_dirs)} 个):")
            for d in sorted(cache_dirs):
                rel_path = d.relative_to(root)
                size = get_dir_size(d)
                print(f"  - {rel_path} ({get_size_str(size)})")

        if cache_files:
            print(f"\n[缓存文件] ({len(cache_files)} 个):")
            for f in sorted(cache_files)[:20]:  # 只显示前20个
                rel_path = f.relative_to(root)
                print(f"  - {rel_path}")
            if len(cache_files) > 20:
                print(f"  ... 还有 {len(cache_files) - 20} 个文件")

        print(f"\n{'='*60}")
        print(f"总计: {len(cache_dirs)} 个目录, {len(cache_files)} 个文件")
        print(f"可释放空间: {get_size_str(total_size)}")
        print(f"{'='*60}\n")

    if dry_run:
        print("[预览模式] 使用 --execute 参数执行实际删除")
        return 0, 0, 0

    # 实际删除
    dirs_removed = 0
    files_removed = 0

    for d in cache_dirs:
        try:
            shutil.rmtree(d)
            dirs_removed += 1
            if verbose:
                print(f"[删除目录] {d.relative_to(root)}")
        except (PermissionError, OSError) as e:
            print(f"[删除失败] {d.relative_to(root)}: {e}")

    for f in cache_files:
        try:
            f.unlink()
            files_removed += 1
            if verbose:
                print(f"[删除文件] {f.relative_to(root)}")
        except (PermissionError, OSError) as e:
            print(f"[删除失败] {f.relative_to(root)}: {e}")

    print(f"\n完成! 删除了 {dirs_removed} 个目录, {files_removed} 个文件")
    print(f"释放空间: {get_size_str(total_size)}")

    return dirs_removed, files_removed, total_size


def main():
    parser = argparse.ArgumentParser(
        description="清除项目缓存",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python clear_cache.py              # 预览将要删除的内容
  python clear_cache.py --execute    # 执行实际删除
  python clear_cache.py -q           # 静默模式
        """
    )
    parser.add_argument(
        "--execute", "-e",
        action="store_true",
        help="执行实际删除（默认只预览）"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，减少输出"
    )
    parser.add_argument(
        "--path", "-p",
        type=str,
        default=None,
        help="指定清理路径（默认为脚本所在项目的根目录）"
    )

    args = parser.parse_args()

    # 确定项目根目录
    if args.path:
        root = Path(args.path).resolve()
    else:
        # 脚本在 scripts/ 目录下，项目根目录是上级目录
        root = Path(__file__).parent.parent.resolve()

    if not root.exists():
        print(f"错误: 路径不存在 - {root}")
        return 1

    clear_cache(root, dry_run=not args.execute, verbose=not args.quiet)
    return 0


if __name__ == "__main__":
    exit(main())

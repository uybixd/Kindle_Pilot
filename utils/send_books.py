# 发送某个目录下的所有书籍，除了已经存在的
# 先设定固定目录，后面加到配置文件

"""
Minimal skeleton for syncing books to Kindle (same-name skip only).

Usage (from your main entrypoint):

    from utils.send_books import send_books
    send_books(ip="192.168.1.15", local_dir="./books")

Notes
-----
- Skeleton only: keep it small.
- No format filtering/conversion here; caller decides what files to place in local_dir.
- Dedup rule: skip if a file with the same name already exists on Kindle (case-insensitive).
- Only files with Kindle-supported extensions are synced.
- Optional: trigger Kindle indexer rescan after upload.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import stat
import posixpath as ppath

from .ssh_client import create_ssh_connection  # expects your existing helper

SUPPORTED_EXTS = {".azw3", ".mobi", ".pdf", ".txt", ".azw", ".epub"}

# Defaults (can be overridden by arguments)
DEFAULT_REMOTE_DIR = "/mnt/us/documents/Downloads/Items01"
DEFAULT_LOCAL_DIR = "./books"


def _collect_local_files(base_dir: Path) -> List[Path]:
    """Collect files under base_dir (recursive).
    TODO: consider excluding temp files (e.g., .DS_Store) if needed.
    """
    if not base_dir.exists():
        return []
    return [p for p in base_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS]


def _list_remote_names_casefold(sftp, remote_dir: str) -> Dict[str, str]:
    """Return a map of lowercase filename -> actual remote name for case-insensitive lookup."""
    try:
        names = sftp.listdir(remote_dir)
    except FileNotFoundError:
        # If the directory doesn't exist, create it and continue
        sftp.mkdir(remote_dir)
        names = []
    return {name.lower(): name for name in names}


# Recursively collect all filenames under base_dir (case-insensitive)
def _list_remote_all_names_casefold(sftp, base_dir: str) -> Dict[str, str]:
    """Recursively collect all filenames under base_dir (case-insensitive).
    Returns a map: lowercase filename -> actual remote name (last occurrence wins).
    """
    mapping: Dict[str, str] = {}

    def _recurse(dir_path: str) -> None:
        try:
            entries = sftp.listdir_attr(dir_path)
        except FileNotFoundError:
            return
        for entry in entries:
            name = entry.filename
            full = f"{dir_path.rstrip('/')}/{name}"
            if stat.S_ISDIR(entry.st_mode):
                _recurse(full)
            else:
                mapping[name.lower()] = name

    _recurse(base_dir)
    return mapping


def _put_with_progress(sftp, local_path: Path, remote_path: str) -> None:
    """Upload with a tiny console progress indicator (optional nicety)."""
    total = local_path.stat().st_size

    def _cb(sent, _total=total):
        pct = (sent / _total * 100) if _total else 100
        print(f"\r[UP] {local_path.name}  {sent}/{_total}  {pct:5.1f}%", end="", flush=True)

    sftp.put(str(local_path), remote_path, callback=_cb)
    print()  # newline after progress line


def send_books(
    ip: str,
    username: str = "root",
    password: str = "",
    *,
    port: int = 22,
    local_dir: str | os.PathLike[str] = DEFAULT_LOCAL_DIR,
    remote_dir: str = DEFAULT_REMOTE_DIR,
    trigger_rescan: bool = True,
) -> Dict[str, List[str]]:
    """Sync files from local_dir to Kindle's remote_dir.

    Minimal behavior:
    - Same-name skip only (case-insensitive) on the remote folder.
    - Upload everything else.
    - Optionally trigger indexer rescan.

    Returns a summary dict: {"uploaded": [...], "skipped": [...], "failed": [...]}.
    """
    base = Path(local_dir).expanduser().resolve()
    summary: Dict[str, List[str]] = {"uploaded": [], "skipped": [], "failed": []}

    candidates = _collect_local_files(base)
    if not candidates:
        print(f"[INFO] No files found under: {base}")
        return summary

    # Connect via SSH/SFTP
    ssh = create_ssh_connection(ip, username, password, port=port)
    sftp = ssh.open_sftp()
    try:
        remote_names = _list_remote_names_casefold(sftp, remote_dir)
        # Build a case-insensitive set of *all* existing book filenames on Kindle (documents root)
        docs_root = ppath.dirname(remote_dir.rstrip('/'))  # e.g., /mnt/us/documents
        remote_all_names = _list_remote_all_names_casefold(sftp, docs_root)

        for path in candidates:
            name = path.name
            rel = str(path.relative_to(base))

            # Same-name (case-insensitive) skip rule (anywhere on Kindle)
            if name.lower() in remote_all_names:
                print(f"[SKIP] Exists on Kindle (any folder): {name}")
                summary["skipped"].append(rel)
                continue

            # Upload
            remote_path = f"{remote_dir.rstrip('/')}/{name}"
            try:
                _put_with_progress(sftp, path, remote_path)
                summary["uploaded"].append(rel)
            except Exception as e:
                print(f"[FAIL] {name}: {e}")
                summary["failed"].append(rel)

        # Optional: trigger indexer rescan so items show up quickly in UI
        if trigger_rescan:
            try:
                ssh.exec_command("lipc-set-prop com.lab126.indexer rescan 1", timeout=5)
                print("[INFO] Requested Kindle indexer rescan")
            except Exception:
                # Not fatal if this isn't available
                print("[INFO] Could not trigger indexer rescan (non-fatal)")
    finally:
        # Cleanly close resources
        try:
            sftp.close()
        finally:
            ssh.close()

    # Final summary
    print("\n===== SYNC SUMMARY =====")
    print(f"Uploaded: {len(summary['uploaded'])}")
    print(f"Skipped : {len(summary['skipped'])}")
    print(f"Failed  : {len(summary['failed'])}")

    return summary
import os
import stat
import types
from pathlib import Path
import posixpath as ppath

import pytest

# Unit under test
from utils import send_books as sb


class _Attr:
    """Simple container to mimic paramiko.SFTPAttributes for listdir_attr."""
    def __init__(self, filename: str, is_dir: bool = False):
        self.filename = filename
        self.st_mode = (stat.S_IFDIR | 0o755) if is_dir else (stat.S_IFREG | 0o644)


class FakeSFTP:
    def __init__(self, remote_dir: str, existing_files_by_dir: dict[str, list[str]]):
        # existing_files_by_dir maps absolute directory -> list of filenames
        self.remote_dir = remote_dir
        self._by_dir = {d.rstrip('/'): list(names) for d, names in existing_files_by_dir.items()}
        self.put_calls = []  # (local_path, remote_path)
        self.mkdir_calls = []

    # --- API used by send_books ---
    def listdir(self, path: str):
        path = path.rstrip('/')
        if path not in self._by_dir:
            raise FileNotFoundError(path)
        return list(self._by_dir[path])

    def listdir_attr(self, path: str):
        path = path.rstrip('/')
        if path not in self._by_dir:
            # unknown path -> treat as empty (like a missing subdir)
            return []
        entries = []
        for name in self._by_dir[path]:
            # if this name is also a directory key, assume it's a subdir
            full = f"{path}/{name}".rstrip('/')
            is_dir = full in self._by_dir and any(isinstance(n, str) for n in self._by_dir[full])
            entries.append(_Attr(name, is_dir=is_dir))
        return entries

    def mkdir(self, path: str):
        path = path.rstrip('/')
        self._by_dir.setdefault(path, [])
        self.mkdir_calls.append(path)

    def put(self, local_path: str, remote_path: str, callback=None):
        # record call and simulate progress
        size = os.path.getsize(local_path)
        if callback:
            callback(size, size)
        self.put_calls.append((local_path, remote_path))

    def close(self):
        pass


class FakeSSH:
    def __init__(self, sftp: FakeSFTP):
        self._sftp = sftp
        self.exec_calls = []

    def open_sftp(self):
        return self._sftp

    def exec_command(self, cmd: str, timeout: int = 5):
        self.exec_calls.append((cmd, timeout))
        # return simple tuple placeholders
        return (None, types.SimpleNamespace(read=lambda: b""), None)

    def close(self):
        pass


@pytest.fixture()
def local_book_dir(tmp_path: Path):
    # Create files: three supported (AZW3, MOBI, EPUB)
    (tmp_path / "A.azw3").write_bytes(b"azw3")
    (tmp_path / "B.mobi").write_bytes(b"mobi")
    (tmp_path / "C.epub").write_bytes(b"epub")  # unsupported by current filter
    return tmp_path


@pytest.fixture()
def fake_env(monkeypatch):
    """Patch create_ssh_connection to return a FakeSSH with a FakeSFTP.
    Remote tree defaults to /mnt/us/documents/Downloads/Items01 (send_books default)
    and its parent /mnt/us/documents used for recursive duplicate detection.
    """
    remote_dir = sb.DEFAULT_REMOTE_DIR
    docs_root = ppath.dirname(remote_dir.rstrip('/'))

    # Default: Items01 exists and is empty; also provide an Items02 directory for recursion tests
    remote_tree = {
        docs_root: ["Downloads"],
        f"{docs_root}/Downloads": [ppath.basename(remote_dir)],
        remote_dir: [],
    }

    sftp = FakeSFTP(remote_dir=remote_dir, existing_files_by_dir=remote_tree)
    ssh = FakeSSH(sftp)

    def _fake_create_ssh_connection(ip, username, password, port=22, **kwargs):
        return ssh

    monkeypatch.setattr(sb, "create_ssh_connection", _fake_create_ssh_connection)
    return sftp, ssh


def test_upload_supported_and_skip_unsupported(local_book_dir, fake_env, capsys):
    sftp, ssh = fake_env

    summary = sb.send_books(
        ip="1.2.3.4",
        username="root",
        password="",
        local_dir=str(local_book_dir),
        trigger_rescan=True,
    )

    # EPUB is supported now; AZW3, MOBI, and EPUB uploaded
    uploaded_names = [Path(p).name for _, p in sftp.put_calls]
    assert set(uploaded_names) == {"A.azw3", "B.mobi", "C.epub"}
    assert summary["uploaded"] and len(summary["uploaded"]) == 3
    assert not summary["failed"]

    # Ensure indexer rescan was requested
    assert any("indexer rescan" in msg for msg in capsys.readouterr().out.splitlines())


def test_skip_if_name_exists_anywhere(local_book_dir, monkeypatch):
    # Build a remote tree where another folder already contains 'B.mobi'
    remote_dir = sb.DEFAULT_REMOTE_DIR
    docs_root = ppath.dirname(remote_dir.rstrip('/'))

    remote_tree = {
        docs_root: ["Downloads", "Other"],
        f"{docs_root}/Downloads": [ppath.basename(remote_dir)],
        remote_dir: [],  # target is empty
        f"{docs_root}/Other": ["Sub"],
        f"{docs_root}/Other/Sub": ["B.mobi"],  # duplicate name elsewhere on device
    }

    sftp = FakeSFTP(remote_dir=remote_dir, existing_files_by_dir=remote_tree)
    ssh = FakeSSH(sftp)

    def _fake_create_ssh_connection(ip, username, password, port=22, **kwargs):
        return ssh

    monkeypatch.setattr(sb, "create_ssh_connection", _fake_create_ssh_connection)

    # Ensure local contains B.mobi (already created in fixture earlier, but we rebuild here)
    (local_book_dir / "B.mobi").write_bytes(b"mobi")

    summary = sb.send_books(
        ip="1.2.3.4",
        username="root",
        password="",
        local_dir=str(local_book_dir),
        trigger_rescan=False,
    )

    # A.azw3 and C.epub should upload; B.mobi should be skipped due to global name collision
    uploaded = [Path(p).name for _, p in sftp.put_calls]
    assert uploaded == ["A.azw3", "C.epub"]

    assert any(rel.endswith("B.mobi") for rel in summary["skipped"])  # B skipped
    assert any(rel.endswith("A.azw3") for rel in summary["uploaded"])  # A uploaded
    assert not summary["failed"]

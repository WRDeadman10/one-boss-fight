"""Atomic same-directory writes for offline tool outputs."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


def _temporary_path(target: Path) -> tuple[int, Path]:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    return fd, Path(name)


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Replace a file only after its complete bytes have been flushed."""
    target = Path(path)
    fd, temporary = _temporary_path(target)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    atomic_write_bytes(path, text.encode(encoding))


def atomic_create_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Publish a new file atomically and fail if the destination already exists."""
    target = Path(path)
    fd, temporary = _temporary_path(target)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(text.encode(encoding))
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise
    temporary.unlink()


def atomic_create_copy(source: Path, path: Path) -> None:
    """Copy to a temporary sibling, then publish without replacing a file."""
    source = Path(source)
    target = Path(path)
    fd, temporary = _temporary_path(target)
    os.close(fd)
    try:
        shutil.copy2(source, temporary)
        with temporary.open("r+b") as stream:
            os.fsync(stream.fileno())
        os.link(temporary, target)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise
    temporary.unlink()

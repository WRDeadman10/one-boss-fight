"""Atomic same-directory writes for offline tool outputs.

Failure contract (BK-241..245, X-2094/X-2096; audit T1-T4 in Documentation/Boss/BK_236_240_ATOMIC_IO_AUDIT.md):
  * write/flush/fsync/copy/link/replace failure -> the ORIGINAL exception propagates, the destination is unchanged
    (old content kept for atomic_write_*, nothing published for atomic_create_*), and the temp sibling is removed
    when the filesystem allows it. A cleanup error never replaces the original exception (T2).
  * the temp file descriptor is owned explicitly: if os.fdopen fails it is closed before cleanup (T4), and
    atomic_create_copy's temporary descriptor is closed inside the guarded block (T3).
  * once os.link / os.replace has published the destination the call SUCCEEDS; a temp that cannot be removed
    afterwards is reported with a RuntimeWarning naming the orphan, never as a failed write (T1).
"""
from __future__ import annotations

import os
import secrets
import shutil
import stat
import warnings
from pathlib import Path


_TEMP_ATTEMPTS = 100
_TEMP_FLAGS = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOINHERIT", 0) | getattr(os, "O_BINARY", 0)


def _temporary_path(target: Path) -> tuple[int, Path]:
    """Create the hidden temp sibling `.<name>.<random>.tmp` with a BOUNDED retry loop (J1, BK-251..255/X-2109).

    tempfile.mkstemp retries FileExistsError up to TMP_MAX (2**31-1 on Windows). Through an NTFS junction,
    O_CREAT|O_EXCL of a NEW name raises FileExistsError, so mkstemp effectively hangs. Here a FileExistsError for a
    name that does not exist switches temp creation to the resolved parent directory (same filesystem; os.link and
    os.replace still publish to the unchanged lexical target entry), and every path gives up after _TEMP_ATTEMPTS.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    directory = target.parent
    resolved = False
    for _ in range(_TEMP_ATTEMPTS):
        candidate = directory / f".{target.name}.{secrets.token_hex(6)}.tmp"
        try:
            return os.open(candidate, _TEMP_FLAGS, 0o600), candidate
        except FileExistsError:
            if not resolved and not os.path.lexists(candidate):
                real = Path(os.path.realpath(directory))
                resolved = True
                if real != directory:
                    directory = real
        except PermissionError:
            # Do not disguise an access failure as an exhausted name-collision retry.
            raise
    raise FileExistsError(f"could not create a temporary file for {target} in {directory} "
                          f"after {_TEMP_ATTEMPTS} attempts")


def _discard_after_failure(temporary: Path) -> None:
    """Best-effort cleanup on a failure path: never raises, so the original exception wins (T2)."""
    try:
        temporary.unlink()
    except OSError:
        pass  # already gone, or locked: the caller still receives the original error


def _discard_after_publish(temporary: Path, target: Path) -> None:
    """The destination is already published: a temp that cannot be removed is a warning, not a failure (T1)."""
    try:
        temporary.unlink()
    except FileNotFoundError:
        pass
    except OSError as error:
        try:
            warnings.warn(f"published {target} but could not remove temporary {temporary}: {error}", RuntimeWarning,
                          stacklevel=3)
        except RuntimeWarning:
            # A warnings-as-errors policy must not turn an already-published create into a reported failure.
            pass


def _open_owned(fd: int, temporary: Path):
    """Wrap the temporary descriptor; if wrapping fails, close it ourselves before cleanup (T4)."""
    try:
        return os.fdopen(fd, "wb")
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        _discard_after_failure(temporary)
        raise


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Replace a file only after its complete bytes have been flushed."""
    target = Path(path)
    fd, temporary = _temporary_path(target)
    stream = _open_owned(fd, temporary)
    try:
        with stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except BaseException:
        _discard_after_failure(temporary)
        raise


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    atomic_write_bytes(path, text.encode(encoding))


def atomic_create_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Publish a new file atomically and fail if the destination already exists."""
    target = Path(path)
    data = text.encode(encoding)
    fd, temporary = _temporary_path(target)
    stream = _open_owned(fd, temporary)
    try:
        with stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, target)
    except BaseException:
        _discard_after_failure(temporary)
        raise
    _discard_after_publish(temporary, target)


def atomic_create_copy(source: Path, path: Path) -> None:
    """Copy to a temporary sibling, then publish without replacing a file."""
    source = Path(source)
    target = Path(path)
    fd, temporary = _temporary_path(target)
    try:
        os.close(fd)  # T3: inside the guarded block, so a close fault still removes the temp
        shutil.copy2(source, temporary)
        # M1 (BK-261..265): copy2 also copies a READ-ONLY source mode; the r+b fsync open and the temp unlink
        # would then fail on Windows (copy refused + orphan temp). Keep the temp owner-writable until it is
        # published and removed; chmod does not change the copied mtime.
        copied_mode = stat.S_IMODE(os.stat(temporary).st_mode)
        writable_mode = copied_mode | stat.S_IWRITE
        if writable_mode != copied_mode:
            os.chmod(temporary, writable_mode)
        with temporary.open("r+b") as stream:
            os.fsync(stream.fileno())
        os.link(temporary, target)
    except BaseException:
        _discard_after_failure(temporary)
        raise
    _discard_after_publish(temporary, target)
    if writable_mode != copied_mode:
        _restore_mode_after_publish(target, copied_mode)


def _restore_mode_after_publish(target: Path, mode: int) -> None:
    """Apply the source's (read-only) mode to the published copy; failure is a warning, never a failed copy (T1)."""
    try:
        os.chmod(target, mode)
    except OSError as error:
        try:
            warnings.warn(f"published {target} but could not apply source mode {oct(mode)}: {error}", RuntimeWarning,
                          stacklevel=3)
        except RuntimeWarning:
            pass

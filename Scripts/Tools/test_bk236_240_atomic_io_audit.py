"""BK-236..240 (C, implementer; X-2086/X-2090/X-2091; hazards T1-T3 fixed in BK-241..245): audit of Scripts/Tools/atomic_io.py and its
direct callers, with synthetic fault injection in throwaway OS temp directories.

atomic_io.py is NOT modified and no production caller is executed (callers are only classified by import text).
Held behaviour is ordinary tests; confirmed hazards are expectedFailure with the rule in the docstring. Faults are
injected by patching os/pathlib calls inside the module; no real output, lock, evidence pack, Unreal, build or PIE.
"""
import ast
import os
import sys
import tempfile
import unittest
import warnings
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import atomic_io as A  # noqa: E402

REPLACE_API = {"atomic_write_bytes", "atomic_write_text"}
CREATE_API = {"atomic_create_text", "atomic_create_copy"}


def callers():
    """BK-236: {caller module: imported atomic_io names} for non-test modules under Scripts/ (static, by AST)."""
    found = {}
    for path in sorted((HERE.parents[1] / "Scripts").rglob("*.py")):
        if path.name.startswith("test_") or path.name == "atomic_io.py" or "__pycache__" in path.parts:
            continue
        with warnings.catch_warnings():  # some scanned scripts contain invalid escape sequences; irrelevant here
            warnings.simplefilter("ignore", (DeprecationWarning, SyntaxWarning))
            tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="replace"))
        names = {alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module == "atomic_io"
                 for alias in node.names}
        if names:
            found[path.name] = names
    return found


def temps(folder):
    return sorted(p.name for p in Path(folder).iterdir() if p.name.endswith(".tmp"))


class Bk236Callers(unittest.TestCase):
    def test_caller_inventory_and_api_split(self):
        found = callers()
        replace = sorted(n for n, names in found.items() if names & REPLACE_API)
        create = sorted(n for n, names in found.items() if names & CREATE_API)
        self.assertEqual(replace, ["evidence_summary.py", "make_source_manifest.py", "summarize_encounter_cost.py",
                                   "summarize_packaged_metrics.py", "token_coverage.py"])
        self.assertEqual(create, ["audit_editor_save_safety.py", "evidence_pack.py", "inventory_editor_asset_writers.py",
                                  "new_rule_scaffold.py"])
        self.assertEqual(set(replace) & set(create), set())  # no caller mixes the two semantics


class Bk237TempSibling(unittest.TestCase):
    def test_temp_is_a_hidden_sibling_in_the_target_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sub" / "out.txt"
            fd, temp = A._temporary_path(target)
            os.close(fd)
            try:
                self.assertEqual(temp.parent, target.parent)              # same directory -> same filesystem for link/replace
                self.assertTrue(temp.name.startswith(".out.txt.") and temp.name.endswith(".tmp"))
            finally:
                temp.unlink()

    def test_parent_directories_are_created_as_a_side_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a" / "b" / "out.txt"
            A.atomic_write_text(target, "x")
            self.assertTrue(target.is_file())


class Bk238FailureCleanup(unittest.TestCase):
    def test_write_and_flush_failures_remove_temp_and_keep_old_target(self):
        real_fdopen = A.os.fdopen

        class FailingStream:
            def __init__(self, stream, phase):
                self.stream = stream
                self.phase = phase

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return self.stream.__exit__(exc_type, exc, traceback)

            def write(self, data):
                if self.phase == "write":
                    raise OSError("synthetic write failure")
                return self.stream.write(data)

            def flush(self):
                if self.phase == "flush":
                    raise OSError("synthetic flush failure")
                return self.stream.flush()

            def fileno(self):
                return self.stream.fileno()

        for phase in ("write", "flush"):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "out.txt"
                target.write_text("old", encoding="utf-8")

                def fdopen(fd, mode):
                    return FailingStream(real_fdopen(fd, mode), phase)

                with mock.patch.object(A.os, "fdopen", side_effect=fdopen), self.assertRaises(OSError):
                    A.atomic_write_text(target, "new")

                self.assertEqual(target.read_text(encoding="utf-8"), "old")
                self.assertEqual(temps(tmp), [])

    def test_fsync_failure_removes_temp_and_keeps_old_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            target.write_text("old", encoding="utf-8")
            with mock.patch.object(A.os, "fsync", side_effect=OSError("synthetic fsync failure")), self.assertRaises(OSError):
                A.atomic_write_text(target, "new")
            self.assertEqual(target.read_text(encoding="utf-8"), "old")
            self.assertEqual(temps(tmp), [])

    def test_replace_failure_removes_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            with mock.patch.object(A.os, "replace", side_effect=OSError("synthetic replace failure")), self.assertRaises(OSError):
                A.atomic_write_text(target, "new")
            self.assertFalse(target.exists())
            self.assertEqual(temps(tmp), [])

    def test_create_link_failure_removes_temp_and_publishes_nothing(self):
        for fn, args in ((A.atomic_create_text, ("x",)), (A.atomic_create_copy, None)):
            with self.subTest(fn=fn.__name__), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "out.txt"
                source = Path(tmp) / "src.bin"
                source.write_bytes(b"data")
                with mock.patch.object(A.os, "link", side_effect=OSError("synthetic link failure")), self.assertRaises(OSError):
                    fn(target, *args) if args else fn(source, target)
                self.assertFalse(target.exists())
                self.assertEqual(temps(tmp), [])

    def test_copy_failure_removes_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "src.bin", Path(tmp) / "out.bin"
            source.write_bytes(b"data")
            with mock.patch.object(A.shutil, "copy2", side_effect=OSError("synthetic copy failure")), self.assertRaises(OSError):
                A.atomic_create_copy(source, target)
            self.assertFalse(target.exists())
            self.assertEqual(temps(tmp), [])


class Bk239NoOverwrite(unittest.TestCase):
    def test_create_never_overwrites_and_leaves_no_temp(self):
        for fn in ("text", "copy"):
            with self.subTest(fn=fn), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "out.txt"
                target.write_text("keep", encoding="utf-8")
                source = Path(tmp) / "src.txt"
                source.write_text("new", encoding="utf-8")
                with self.assertRaises(FileExistsError):
                    A.atomic_create_text(target, "new") if fn == "text" else A.atomic_create_copy(source, target)
                self.assertEqual(target.read_text(encoding="utf-8"), "keep")
                self.assertEqual(temps(tmp), [])

    def test_write_replaces_existing_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            target.write_text("old", encoding="utf-8")
            A.atomic_write_text(target, "new")
            self.assertEqual(target.read_text(encoding="utf-8"), "new")
            self.assertEqual(temps(tmp), [])

    def test_no_parent_directory_fsync(self):
        """Documented limit (X-2091): only the file is fsynced; the parent directory entry is not, so visibility is
        atomic but a crash right after publication may lose the new directory entry on some filesystems."""
        source = Path(A.__file__).read_text(encoding="utf-8")
        self.assertEqual(source.count("os.fsync("), 3)
        self.assertNotIn("O_DIRECTORY", source)


class Bk239PostPublicationHazards(unittest.TestCase):
    def test_post_publication_temp_unlink_failure_state(self):
        """X-2090 (atomic_io.py:54/:74), documented state: os.link already published the target, then the temp
        unlink raises -> the caller sees an exception although the target EXISTS, and the temp remains as a second
        hard link to the same data."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            real_unlink = Path.unlink

            def fail_temp_unlink(self_path, *a, **k):
                if self_path.name.endswith(".tmp"):
                    raise PermissionError("synthetic post-publication unlink failure")
                return real_unlink(self_path, *a, **k)

            # BK-241..245 (X-2094) contract: the published target is a SUCCESS; the orphan temp is reported as a
            # RuntimeWarning (formerly this raised PermissionError - audit hazard T1).
            with mock.patch.object(Path, "unlink", fail_temp_unlink), self.assertWarns(RuntimeWarning) as caught:
                A.atomic_create_text(target, "published")
            self.assertIn("could not remove temporary", str(caught.warning))
            self.assertEqual(target.read_text(encoding="utf-8"), "published")
            self.assertEqual(len(temps(tmp)), 1)

    def test_gap_t1_published_target_is_not_reported_as_a_failure(self):
        """T1 (:54/:74): after a successful os.link the destination is committed; a failing temp unlink still raises,
        so a caller retries and then gets FileExistsError for its own file. Rule: after link succeeds, treat the temp
        unlink as best-effort (suppress OSError, optionally warn) so success is reported for a published target."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            real_unlink = Path.unlink

            def fail_temp_unlink(self_path, *a, **k):
                if self_path.name.endswith(".tmp"):
                    raise PermissionError("synthetic")
                return real_unlink(self_path, *a, **k)

            with mock.patch.object(Path, "unlink", fail_temp_unlink):
                A.atomic_create_text(target, "published")  # must not raise once the target is published

    def test_gap_t2_cleanup_failure_must_not_mask_the_original_error(self):
        """T2 (:27-30, :49-52, :69-72): the cleanup `temporary.unlink()` only suppresses FileNotFoundError; any other
        OSError (e.g. PermissionError on Windows) replaces the original exception, so callers see the cleanup error
        instead of the real cause. Rule: suppress (or log) every OSError from cleanup and re-raise the original."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            with mock.patch.object(A.os, "fsync", side_effect=ValueError("original cause")), \
                    mock.patch.object(Path, "unlink", side_effect=PermissionError("cleanup failure")):
                with self.assertRaises(ValueError):
                    A.atomic_write_text(target, "x")

    def test_gap_t3_copy_close_failure_leaks_the_temp(self):
        """T3 (:61-63): atomic_create_copy closes the mkstemp fd BEFORE its try block, so if os.close raises the empty
        temp sibling is never removed. Rule: close inside the try (or a dedicated try/finally) so cleanup also covers
        a close failure."""
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "src.bin", Path(tmp) / "out.bin"
            source.write_bytes(b"data")
            real_close = os.close

            def fail_close(fd):
                real_close(fd)
                raise OSError("synthetic close failure")

            with mock.patch.object(A.os, "close", fail_close):
                with self.assertRaises(OSError):
                    A.atomic_create_copy(source, target)
            self.assertEqual(temps(tmp), [])


if __name__ == "__main__":
    unittest.main()

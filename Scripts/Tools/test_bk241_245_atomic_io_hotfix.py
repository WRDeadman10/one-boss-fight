"""BK-241..245 (C, implementer; X-2094/X-2096): regressions for the atomic_io.py failure-contract hotfix (T1-T4).

Faults are injected by patching os/pathlib inside atomic_io, in throwaway OS temp directories only. No production
caller, real output, lock, evidence pack, Unreal, build or PIE.
"""
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


def temps(folder):
    return sorted(p.name for p in Path(folder).iterdir() if p.name.endswith(".tmp"))


def fail_temp_unlink(error=PermissionError("synthetic temp unlink failure")):
    real = Path.unlink

    def unlink(self, *a, **k):
        if self.name.endswith(".tmp"):
            raise error
        return real(self, *a, **k)
    return unlink


class T1PublishedTargetIsSuccess(unittest.TestCase):
    def test_create_text_and_copy_succeed_with_a_warning_when_temp_survives(self):
        for kind in ("text", "copy"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                target, source = Path(tmp) / "out.txt", Path(tmp) / "src.txt"
                source.write_text("data", encoding="utf-8")
                with mock.patch.object(Path, "unlink", fail_temp_unlink()), self.assertWarns(RuntimeWarning) as caught:
                    A.atomic_create_text(target, "data") if kind == "text" else A.atomic_create_copy(source, target)
                self.assertEqual(target.read_text(encoding="utf-8"), "data")
                self.assertIn(str(target), str(caught.warning))
                self.assertEqual(len(temps(tmp)), 1)  # the orphan is reported, not hidden

    def test_warnings_as_errors_do_not_turn_published_create_into_failure(self):
        with tempfile.TemporaryDirectory() as tmp, warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            target = Path(tmp) / "out.txt"
            with mock.patch.object(Path, "unlink", fail_temp_unlink()):
                A.atomic_create_text(target, "published")
            self.assertEqual(target.read_text(encoding="utf-8"), "published")
            self.assertEqual(len(temps(tmp)), 1)

    def test_normal_create_emits_no_warning_and_leaves_no_temp(self):
        with tempfile.TemporaryDirectory() as tmp, warnings.catch_warnings():
            warnings.simplefilter("error")
            A.atomic_create_text(Path(tmp) / "out.txt", "data")
            self.assertEqual(temps(tmp), [])


class T2OriginalExceptionWins(unittest.TestCase):
    STEPS = ("fsync", "replace", "link")

    def test_cleanup_error_never_replaces_the_original(self):
        cases = (("write", "fsync"), ("write", "replace"), ("create", "fsync"), ("create", "link"), ("copy", "link"))
        for api, step in cases:
            with self.subTest(api=api, step=step), tempfile.TemporaryDirectory() as tmp:
                target, source = Path(tmp) / "out.txt", Path(tmp) / "src.txt"
                target.write_text("old", encoding="utf-8") if api == "write" else None
                source.write_text("new", encoding="utf-8")
                original = ValueError("original %s failure" % step)
                with mock.patch.object(A.os, step, side_effect=original), \
                        mock.patch.object(Path, "unlink", fail_temp_unlink()):
                    with self.assertRaises(ValueError) as raised:
                        if api == "write":
                            A.atomic_write_text(target, "new")
                        elif api == "create":
                            A.atomic_create_text(target, "new")
                        else:
                            A.atomic_create_copy(source, target)
                self.assertIs(raised.exception, original)
                if api == "write":
                    self.assertEqual(target.read_text(encoding="utf-8"), "old")  # replace target keeps old content
                else:
                    self.assertFalse(target.exists())                          # create publishes nothing

    def test_recoverable_cleanup_still_removes_the_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(A.os, "fsync", side_effect=OSError("fsync")), self.assertRaises(OSError):
                A.atomic_write_text(Path(tmp) / "out.txt", "x")
            self.assertEqual(temps(tmp), [])


class T3CopyCloseFault(unittest.TestCase):
    def test_close_failure_removes_the_temp_and_publishes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "src.bin", Path(tmp) / "out.bin"
            source.write_bytes(b"data")
            real_close = os.close

            def fail_close(fd):
                real_close(fd)
                raise OSError("synthetic close failure")

            with mock.patch.object(A.os, "close", fail_close), self.assertRaises(OSError):
                A.atomic_create_copy(source, target)
            self.assertFalse(target.exists())
            self.assertEqual(temps(tmp), [])


class T4FdopenOwnership(unittest.TestCase):
    def test_fdopen_failure_closes_the_descriptor_and_removes_the_temp(self):
        for api in ("write", "create"):
            with self.subTest(api=api), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "out.txt"
                if api == "write":
                    target.write_text("old", encoding="utf-8")
                closed = []
                real_close = os.close
                with mock.patch.object(A.os, "fdopen", side_effect=ValueError("synthetic fdopen failure")), \
                        mock.patch.object(A.os, "close", side_effect=lambda fd: (closed.append(fd), real_close(fd))):
                    with self.assertRaises(ValueError):
                        A.atomic_write_text(target, "new") if api == "write" else A.atomic_create_text(target, "new")
                self.assertEqual(len(closed), 1, "the unwrapped descriptor must be closed exactly once")
                self.assertEqual(temps(tmp), [], "with the descriptor closed the temp can be removed (also on Windows)")
                if api == "write":
                    self.assertEqual(target.read_text(encoding="utf-8"), "old")
                else:
                    self.assertFalse(target.exists())


class SemanticsPreserved(unittest.TestCase):
    def test_replace_vs_exclusive_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            A.atomic_write_text(target, "one")
            A.atomic_write_text(target, "two")                     # replace overwrites
            self.assertEqual(target.read_text(encoding="utf-8"), "two")
            with self.assertRaises(FileExistsError):
                A.atomic_create_text(target, "three")              # create never overwrites
            self.assertEqual(target.read_text(encoding="utf-8"), "two")
            self.assertEqual(temps(tmp), [])

    def test_public_api_unchanged(self):
        for name in ("atomic_write_bytes", "atomic_write_text", "atomic_create_text", "atomic_create_copy"):
            self.assertTrue(callable(getattr(A, name)))


if __name__ == "__main__":
    unittest.main()

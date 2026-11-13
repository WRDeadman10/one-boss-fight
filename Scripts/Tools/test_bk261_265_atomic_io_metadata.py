"""BK-261..265 (C, implementer; X-2112): metadata (mode/mtime) behaviour of atomic_create_copy and
atomic_write_text/bytes, shutil.copy2 parity, symlink sources, and the M1 read-only-source fix.

Synthetic OS temp directories only; no production caller, project output, lock, pack, Unreal, build or PIE.
On Windows os.chmod only toggles the read-only attribute, so modes are 0o100444 (read-only) or 0o100666.
"""
import os
import shutil
import stat
import sys
import tempfile
import time
import unittest
import warnings
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import atomic_io as A  # noqa: E402

OLD = 1_600_000_000  # fixed source mtime (2020-09-13)


def temps(folder):
    return sorted(p.name for p in Path(folder).iterdir() if p.name.endswith(".tmp"))


def mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


def symlink_reason():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            os.symlink(os.path.join(tmp, "x"), os.path.join(tmp, "probe"))
            return None
        except (OSError, NotImplementedError) as error:
            return f"host cannot create symlinks: {error!r}"


SYMLINK_SKIP = symlink_reason()


class TempDir(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        for p in self.dir.rglob("*"):  # read-only files block TemporaryDirectory cleanup on Windows
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
        self._tmp.cleanup()

    def source(self, readonly=False, name="src.txt", data=b"payload"):
        src = self.dir / name
        src.write_bytes(data)
        os.utime(src, (OLD, OLD))
        if readonly:
            os.chmod(src, stat.S_IREAD)
        return src


class Bk261TempMetadataAtPreLinkGate(TempDir):
    def capture(self, src):
        seen = {}
        real_link = A.os.link

        def gate(tmp_path, dst):
            seen.update(mode=mode(tmp_path), mtime=os.stat(tmp_path).st_mtime, data=Path(tmp_path).read_bytes())
            return real_link(tmp_path, dst)

        with mock.patch.object(A.os, "link", gate):
            A.atomic_create_copy(src, self.dir / "out.txt")
        return seen

    def test_writable_source_mode_and_mtime_are_on_the_temp_before_publication(self):
        src = self.source()
        seen = self.capture(src)
        self.assertEqual(seen["mode"], mode(src))       # copy2 already applied the source permissions
        self.assertEqual(seen["mtime"], OLD)
        self.assertEqual(seen["data"], b"payload")

    def test_readonly_source_temp_is_kept_writable_until_publication(self):
        src = self.source(readonly=True)
        seen = self.capture(src)
        self.assertTrue(seen["mode"] & stat.S_IWRITE)  # M1: writable so fsync/unlink can work (Windows: 0o666)
        self.assertFalse(mode(src) & stat.S_IWRITE)
        self.assertEqual(seen["mtime"], OLD)                       # chmod does not touch the copied mtime


class Bk262Copy2Parity(TempDir):
    def test_final_copy_matches_shutil_copy2_and_source_is_unchanged(self):
        for readonly in (False, True):
            with self.subTest(readonly=readonly):
                src = self.source(readonly=readonly, name=f"src_{readonly}.txt")
                before = (src.read_bytes(), mode(src), os.stat(src).st_mtime)
                reference = self.dir / f"ref_{readonly}.txt"
                shutil.copy2(src, reference)
                out = self.dir / f"out_{readonly}.txt"
                with warnings.catch_warnings():
                    warnings.simplefilter("error")  # a clean copy emits no warning
                    A.atomic_create_copy(src, out)
                self.assertEqual(out.read_bytes(), reference.read_bytes())
                self.assertEqual(mode(out), mode(reference))
                self.assertEqual(os.stat(out).st_mtime, os.stat(reference).st_mtime)
                self.assertEqual((src.read_bytes(), mode(src), os.stat(src).st_mtime), before)
                self.assertEqual(temps(self.dir), [])


class M1ReadOnlySourceFix(TempDir):
    def test_readonly_source_copy_succeeds_without_orphan(self):
        """M1: formerly PermissionError at temporary.open('r+b') AND an orphan read-only temp that cleanup could
        not remove (Windows)."""
        src = self.source(readonly=True)
        A.atomic_create_copy(src, self.dir / "out.txt")
        self.assertEqual((self.dir / "out.txt").read_bytes(), b"payload")
        self.assertEqual(mode(self.dir / "out.txt"), mode(src))
        self.assertEqual(temps(self.dir), [])

    def test_mode_restore_failure_after_publication_is_a_warning(self):
        src = self.source(readonly=True)
        real_chmod = os.chmod
        calls = []

        def chmod(path, m, *a, **k):
            calls.append(Path(path).name)
            if not Path(path).name.endswith(".tmp"):
                raise PermissionError("synthetic post-publish chmod failure")
            return real_chmod(path, m, *a, **k)

        with mock.patch.object(A.os, "chmod", chmod), self.assertWarns(RuntimeWarning) as caught:
            A.atomic_create_copy(src, self.dir / "out.txt")
        self.assertIn("could not apply source mode", str(caught.warning))
        self.assertEqual((self.dir / "out.txt").read_bytes(), b"payload")  # published copy stands
        self.assertEqual(temps(self.dir), [])

    def test_mode_restore_warning_cannot_turn_published_copy_into_failure(self):
        src = self.source(readonly=True)
        real_chmod = os.chmod

        def chmod(path, m, *a, **k):
            if not Path(path).name.endswith(".tmp"):
                raise PermissionError("synthetic post-publish chmod failure")
            return real_chmod(path, m, *a, **k)

        with mock.patch.object(A.os, "chmod", chmod), warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)
            A.atomic_create_copy(src, self.dir / "out.txt")  # T1: warnings-as-errors cannot reverse publication
        self.assertEqual((self.dir / "out.txt").read_bytes(), b"payload")
        self.assertEqual(temps(self.dir), [])

    def test_failure_before_link_with_readonly_source_leaves_no_temp(self):
        src = self.source(readonly=True)
        with mock.patch.object(A.os, "link", side_effect=OSError("synthetic link failure")), self.assertRaises(OSError):
            A.atomic_create_copy(src, self.dir / "out.txt")
        self.assertFalse((self.dir / "out.txt").exists())
        self.assertEqual(temps(self.dir), [])


@unittest.skipIf(SYMLINK_SKIP, SYMLINK_SKIP or "")
class Bk263SymlinkSource(TempDir):
    def test_copy_follows_the_link(self):
        referent = self.source(name="referent.txt")
        link = self.dir / "link.txt"
        os.symlink(referent, link)
        A.atomic_create_copy(link, self.dir / "out.txt")
        out = self.dir / "out.txt"
        self.assertFalse(out.is_symlink())                     # copy2 default follow_symlinks=True
        self.assertEqual(out.read_bytes(), b"payload")
        self.assertTrue(link.is_symlink())
        self.assertEqual(referent.read_bytes(), b"payload")
        self.assertEqual(temps(self.dir), [])


class Bk264ReplaceMetadata(TempDir):
    def test_absent_target_gets_a_fresh_owner_writable_file(self):
        start = time.time() - 2
        target = self.dir / "new.txt"
        A.atomic_write_text(target, "x")
        self.assertTrue(mode(target) & stat.S_IWRITE)
        self.assertGreaterEqual(os.stat(target).st_mtime, start)
        if os.name != "nt":
            self.assertEqual(mode(target), 0o600)  # temp is created 0o600; no umask-based default

    def test_existing_writable_target_metadata_is_not_preserved(self):
        target = self.source(name="out.txt", data=b"old")
        start = time.time() - 2
        A.atomic_write_bytes(target, b"new")
        self.assertEqual(target.read_bytes(), b"new")
        self.assertGreaterEqual(os.stat(target).st_mtime, start)   # mtime is the new file's, not OLD
        self.assertNotEqual(os.stat(target).st_mtime, OLD)
        self.assertTrue(mode(target) & stat.S_IWRITE)

    @unittest.skipUnless(os.name == "nt", "Windows-specific: os.replace onto a read-only file is refused")
    def test_existing_readonly_target_is_refused_on_windows(self):
        target = self.source(readonly=True, name="out.txt", data=b"old")
        with self.assertRaises(PermissionError):
            A.atomic_write_bytes(target, b"new")
        self.assertEqual(target.read_bytes(), b"old")
        self.assertEqual(mode(target), stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        self.assertEqual(temps(self.dir), [])


if __name__ == "__main__":
    unittest.main()

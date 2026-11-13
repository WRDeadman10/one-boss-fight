"""BK-266..270 (C, implementer; X-2116): atomic_create_copy refusal paths - same path, existing different
destination, destination hard-linked to the source, and read-only-source failures with an existing destination or an
injected pre-publication fault. Synthetic OS temp directories only; no production caller, project output, lock,
pack, Unreal, build or PIE.
"""
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import atomic_io as A  # noqa: E402

OLD, OTHER = 1_600_000_000, 1_500_000_000


def temps(folder):
    return sorted(p.name for p in Path(folder).iterdir() if p.name.endswith(".tmp"))


def meta(path):
    st = os.stat(path)
    return Path(path).read_bytes(), stat.S_IMODE(st.st_mode), st.st_mtime


def hardlink_reason():
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "a"
        a.write_bytes(b"x")
        try:
            os.link(a, Path(tmp) / "b")
            return None
        except (OSError, NotImplementedError, AttributeError) as error:
            return f"host cannot create hard links: {error!r}"


HARDLINK_SKIP = hardlink_reason()


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        for p in self.dir.rglob("*"):
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
        self._tmp.cleanup()

    def make(self, name, data, mtime, readonly=False):
        p = self.dir / name
        p.write_bytes(data)
        os.utime(p, (mtime, mtime))
        if readonly:
            os.chmod(p, stat.S_IREAD)
        return p


class Bk266SamePath(Base):
    def test_same_source_and_destination_is_refused(self):
        for readonly in (False, True):
            with self.subTest(readonly=readonly):
                src = self.make(f"same_{readonly}.txt", b"source", OLD, readonly)
                before = meta(src)
                with self.assertRaises(FileExistsError) as raised:
                    A.atomic_create_copy(src, src)
                self.assertEqual(type(raised.exception), FileExistsError)  # from os.link: destination exists
                self.assertEqual(meta(src), before)
                self.assertEqual(temps(self.dir), [])


class Bk267ExistingDifferentDestination(Base):
    def test_existing_destination_is_refused_and_both_unchanged(self):
        for readonly in (False, True):
            with self.subTest(readonly_source=readonly):
                src = self.make(f"src_{readonly}.txt", b"source", OLD, readonly)
                dst = self.make(f"dst_{readonly}.txt", b"destination", OTHER)
                before = (meta(src), meta(dst))
                with self.assertRaises(FileExistsError):
                    A.atomic_create_copy(src, dst)
                self.assertEqual((meta(src), meta(dst)), before)
                self.assertEqual(temps(self.dir), [])


@unittest.skipIf(HARDLINK_SKIP, HARDLINK_SKIP or "")
class Bk268HardLinkedDestination(Base):
    def test_destination_hard_linked_to_source_is_refused(self):
        for readonly in (False, True):
            with self.subTest(readonly=readonly):
                src = self.make(f"src_{readonly}.txt", b"source", OLD)
                dst = self.dir / f"dst_{readonly}.txt"
                os.link(src, dst)
                if readonly:
                    os.chmod(src, stat.S_IREAD)  # shared inode: both entries become read-only
                before = (meta(src), meta(dst))
                self.assertTrue(os.path.samefile(src, dst))
                with self.assertRaises(FileExistsError):
                    A.atomic_create_copy(src, dst)
                self.assertEqual((meta(src), meta(dst)), before)
                self.assertTrue(os.path.samefile(src, dst))  # the link relationship is not broken
                self.assertEqual(os.stat(src).st_nlink, 2)
                self.assertEqual(temps(self.dir), [])


class Bk269ReadOnlySourceFailurePaths(Base):
    def test_injected_pre_publication_faults_preserve_original_and_modes(self):
        """Faults after the M1 temp chmod at fsync and link. Neither file's mode changes, the original exception
        object propagates and the (writable) temp is removed."""
        for step in ("fsync", "link"):
            with self.subTest(step=step):
                src = self.make(f"src_{step}.txt", b"source", OLD, readonly=True)
                before = meta(src)
                original = OSError(f"synthetic {step} failure")
                with mock.patch.object(A.os, step, side_effect=original), self.assertRaises(OSError) as raised:
                    A.atomic_create_copy(src, self.dir / f"out_{step}.txt")
                self.assertIs(raised.exception, original)
                self.assertEqual(meta(src), before)
                self.assertFalse((self.dir / f"out_{step}.txt").exists())
                self.assertEqual(temps(self.dir), [])

    def test_existing_destination_with_readonly_source_keeps_both_modes(self):
        src = self.make("src.txt", b"source", OLD, readonly=True)
        for dst_readonly in (False, True):
            with self.subTest(dst_readonly=dst_readonly):
                dst = self.make(f"dst_{dst_readonly}.txt", b"destination", OTHER, dst_readonly)
                before = (meta(src), meta(dst))
                chmods = []
                real_chmod = os.chmod
                with mock.patch.object(A.os, "chmod",
                                       side_effect=lambda p, m, *a, **k: (chmods.append(Path(p).name),
                                                                          real_chmod(p, m, *a, **k))[1]):
                    with self.assertRaises(FileExistsError):
                        A.atomic_create_copy(src, dst)
                self.assertEqual((meta(src), meta(dst)), before)
                self.assertTrue(all(name.endswith(".tmp") for name in chmods), chmods)  # only the temp is chmodded
                self.assertEqual(temps(self.dir), [])

    def test_temp_chmod_failure_preserves_original(self):
        src = self.make("src.txt", b"source", OLD, readonly=True)
        before = meta(src)
        original = PermissionError("synthetic temp chmod failure")
        real_chmod = os.chmod

        def fail_write_enable(path, m, *a, **k):
            # copy2's copystat call (read-only mode) passes; only atomic_io's M1 write-enable call fails.
            if m & stat.S_IWRITE:
                raise original
            return real_chmod(path, m, *a, **k)

        with mock.patch.object(A.os, "chmod", fail_write_enable), self.assertRaises(PermissionError) as raised:
            A.atomic_create_copy(src, self.dir / "out.txt")
        self.assertIs(raised.exception, original)
        self.assertEqual(meta(src), before)
        self.assertFalse((self.dir / "out.txt").exists())
        # Observation O5: the temp is still READ-ONLY (the write-enable failed), so on Windows the best-effort
        # cleanup unlink cannot remove it and one orphan remains. The original exception still wins (T2).
        leftover = temps(self.dir)
        if os.name == "nt":
            self.assertEqual(len(leftover), 1, leftover)
            self.assertFalse(os.stat(self.dir / leftover[0]).st_mode & stat.S_IWRITE)
        else:
            self.assertEqual(leftover, [])  # POSIX unlink depends on the directory, not the file mode


if __name__ == "__main__":
    unittest.main()

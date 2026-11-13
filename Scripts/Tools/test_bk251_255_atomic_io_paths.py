"""BK-251..255 (C, implementer; X-2105): atomic_io.py path-entry (symlink/junction parent and destination),
parent/target-type failures, and concurrent replace. Synthetic OS temp directories only; no production caller,
project output, lock, pack, Unreal, build or PIE.

Host note: true symlinks need SeCreateSymbolicLinkPrivilege / Developer Mode on Windows. When unavailable those
tests SKIP with the exact reason. A directory junction (no privilege needed) covers the linked-parent case on Windows.
"""
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import atomic_io as A  # noqa: E402


def temps(folder):
    return sorted(p.name for p in Path(folder).iterdir() if p.name.endswith(".tmp"))


def symlink_reason():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            os.symlink(tmp, os.path.join(tmp, "probe"), target_is_directory=True)
            return None
        except (OSError, NotImplementedError, AttributeError) as error:
            return f"host cannot create symlinks: {error!r}"


SYMLINK_SKIP = symlink_reason()


def make_junction(link, target):
    import _winapi
    _winapi.CreateJunction(str(target), str(link))


def snapshot(folder):
    """{relative path: bytes or '<dir>'} for collateral-change checks (does not follow links)."""
    out = {}
    for root, dirs, files in os.walk(folder):
        for name in dirs:
            out[os.path.relpath(os.path.join(root, name), folder)] = "<dir>"
        for name in files:
            p = os.path.join(root, name)
            out[os.path.relpath(p, folder)] = Path(p).read_bytes()
    return out


class Bk251LinkedParent(unittest.TestCase):
    def check(self, real_dir, link_dir):
        for api in ("write", "create"):
            with self.subTest(api=api):
                target = link_dir / f"{api}.txt"
                (A.atomic_write_text if api == "write" else A.atomic_create_text)(target, api)
                # The path entry is written THROUGH the link; the bytes land in the referent directory.
                self.assertEqual((real_dir / f"{api}.txt").read_text(encoding="utf-8"), api)
                self.assertEqual(target.read_text(encoding="utf-8"), api)
                self.assertEqual(temps(real_dir), [])

    def test_temp_is_created_beside_the_target_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "link" / "out.txt"
            fd, temp = A._temporary_path(target)
            os.close(fd)
            temp.unlink()
            self.assertEqual(temp.parent, target.parent)  # lexical sibling of the entry, not of the resolved file

    @unittest.skipIf(SYMLINK_SKIP, SYMLINK_SKIP or "")
    def test_symlinked_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            real, link = Path(tmp) / "real", Path(tmp) / "link"
            real.mkdir()
            os.symlink(real, link, target_is_directory=True)
            self.check(real, link)

    @unittest.skipUnless(os.name == "nt", "directory junctions are Windows-only")
    def test_junction_parent_exclusive_open_state(self):
        """Observed host state (BK-251): through an NTFS junction, os.open(O_CREAT|O_EXCL) of a NEW name raises
        FileExistsError while a plain O_CREAT open succeeds. Reproduced with _winapi.CreateJunction and with
        PowerShell New-Item -ItemType Junction, short and long temp paths."""
        with tempfile.TemporaryDirectory() as tmp:
            real, link = Path(tmp) / "real", Path(tmp) / "link"
            real.mkdir()
            make_junction(link, real)
            try:
                flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
                try:
                    os.close(os.open(link / "probe.tmp", flags, 0o600))
                    self.skipTest("this host allows O_EXCL through junctions; hazard J1 not present")
                except FileExistsError:
                    pass
                self.assertFalse((real / "probe.tmp").exists())
            finally:
                os.rmdir(link)  # remove the junction entry only, never the referent

    @unittest.skipUnless(os.name == "nt", "directory junctions are Windows-only")
    def test_j1_junction_parent_write_create_copy_finish_and_clean(self):
        """J1 fixed (X-2109): formerly tempfile.mkstemp retried that FileExistsError up to TMP_MAX (2**31-1) and
        effectively hung. atomic_io now detects the junction signature and creates the temp in the resolved parent;
        the destination entry is still published through the lexical (junction) path."""
        with tempfile.TemporaryDirectory() as tmp:
            real, link = Path(tmp) / "real", Path(tmp) / "link"
            real.mkdir()
            make_junction(link, real)
            try:
                result = []
                worker = threading.Thread(target=lambda: result.append(self._junction_body(real, link)))
                worker.start()
                worker.join(30)
                self.assertFalse(worker.is_alive(), "atomic_io under a junction parent must not hang")
                self.assertEqual(result, ["done"])
            finally:
                os.rmdir(link)

    def _junction_body(self, real, link):
        self.check(real, link)
        source = real / "src.bin"
        source.write_bytes(b"copy")
        A.atomic_create_copy(source, link / "copy.bin")
        assert (real / "copy.bin").read_bytes() == b"copy"
        with self.assertRaises(FileExistsError):
            A.atomic_create_text(link / "create.txt", "again")  # no-overwrite still holds through the junction
        assert temps(real) == [] and temps(link) == []
        return "done"


class J1BoundedTempCreation(unittest.TestCase):
    def test_permission_error_from_temp_creation_propagates_unchanged(self):
        original = PermissionError("synthetic temporary open denied")
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(A.os, "open", side_effect=original), self.assertRaises(PermissionError) as raised:
                A.atomic_write_text(Path(tmp) / "out.txt", "x")
            self.assertIs(raised.exception, original)
            self.assertFalse((Path(tmp) / "out.txt").exists())

    def test_persistent_collisions_give_up_after_the_bound(self):
        """Every attempt collides with an EXISTING name -> a clear FileExistsError after _TEMP_ATTEMPTS, no hang."""
        calls = []

        def always_exists(path, flags, mode=0o777):
            calls.append(path)
            Path(path).write_bytes(b"")  # the name exists, so this is a genuine collision, not the junction signature
            raise FileExistsError(path)

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(A.os, "open", always_exists), self.assertRaises(FileExistsError) as raised:
                A.atomic_write_text(Path(tmp) / "out.txt", "x")
            self.assertEqual(len(calls), A._TEMP_ATTEMPTS)
            self.assertIn("after", str(raised.exception))
            self.assertFalse((Path(tmp) / "out.txt").exists())

    def test_phantom_collision_switches_to_resolved_parent_once(self):
        """FileExistsError for a name that does NOT exist (junction signature) -> retry in realpath(parent)."""
        real_open = os.open
        seen = []

        def phantom_then_real(path, flags, mode=0o777):
            seen.append(Path(path).parent)
            if len(seen) == 1:
                raise FileExistsError(path)
            return real_open(path, flags, mode)

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            with mock.patch.object(A.os, "open", phantom_then_real):
                A.atomic_write_text(target, "x")
            self.assertEqual(target.read_text(encoding="utf-8"), "x")
            self.assertEqual(seen[0], target.parent)
            self.assertEqual(seen[1], Path(os.path.realpath(target.parent)))
            self.assertEqual(temps(tmp), [])

    def test_temp_naming_and_permissions_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            fd, temp = A._temporary_path(target)
            os.close(fd)
            try:
                self.assertRegex(temp.name, r"^\.out\.txt\.[0-9a-f]{12}\.tmp$")
                self.assertEqual(temp.parent, target.parent)  # normal directories keep the lexical sibling
            finally:
                temp.unlink()


@unittest.skipIf(SYMLINK_SKIP, SYMLINK_SKIP or "")
class Bk252SymlinkDestination(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.referent = self.dir / "referent.txt"
        self.referent.write_text("referent", encoding="utf-8")
        self.link = self.dir / "dest.txt"
        os.symlink(self.referent, self.link)

    def tearDown(self):
        self._tmp.cleanup()

    def test_replace_api_replaces_the_link_entry_not_the_referent(self):
        A.atomic_write_text(self.link, "new")
        self.assertFalse(self.link.is_symlink())
        self.assertEqual(self.link.read_text(encoding="utf-8"), "new")
        self.assertEqual(self.referent.read_text(encoding="utf-8"), "referent")
        self.assertEqual(temps(self.dir), [])

    def test_create_api_refuses_and_changes_neither(self):
        with self.assertRaises(FileExistsError):
            A.atomic_create_text(self.link, "new")
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(self.referent.read_text(encoding="utf-8"), "referent")
        self.assertEqual(temps(self.dir), [])


class Bk253ParentAndTargetTypeFailures(unittest.TestCase):
    def test_parent_component_is_a_file(self):
        for api in ("write", "create", "copy"):
            with self.subTest(api=api), tempfile.TemporaryDirectory() as tmp:
                blocker = Path(tmp) / "blocker"
                blocker.write_text("keep", encoding="utf-8")
                source = Path(tmp) / "src.txt"
                source.write_text("s", encoding="utf-8")
                before = snapshot(tmp)
                target = blocker / "out.txt"
                with self.assertRaises(OSError) as raised:
                    if api == "copy":
                        A.atomic_create_copy(source, target)
                    else:
                        (A.atomic_write_text if api == "write" else A.atomic_create_text)(target, "x")
                self.assertIsInstance(raised.exception, (FileExistsError, NotADirectoryError))
                self.assertEqual(snapshot(tmp), before)  # nothing published, no collateral change, no temp

    def test_parent_creation_failure_propagates_original(self):
        original = PermissionError("synthetic mkdir failure")
        with tempfile.TemporaryDirectory() as tmp:
            before = snapshot(tmp)
            with mock.patch.object(Path, "mkdir", side_effect=original), self.assertRaises(PermissionError) as raised:
                A.atomic_write_text(Path(tmp) / "new" / "out.txt", "x")
            self.assertIs(raised.exception, original)
            self.assertEqual(snapshot(tmp), before)

    def test_target_is_a_directory(self):
        for api in ("write", "create"):
            with self.subTest(api=api), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "out.txt"
                target.mkdir()
                (target / "inner.txt").write_text("inner", encoding="utf-8")
                before = snapshot(tmp)
                with self.assertRaises(OSError):
                    (A.atomic_write_text if api == "write" else A.atomic_create_text)(target, "x")
                self.assertEqual(snapshot(tmp), before)  # directory and its contents untouched, no temp


class Bk254ConcurrentReplace(unittest.TestCase):
    WORKERS = 6
    SIZE = 4 * 1024 * 1024  # 4 MiB per payload

    def test_final_file_is_one_complete_payload(self):
        payloads = [bytes([65 + i]) * self.SIZE for i in range(self.WORKERS)]
        barrier = threading.Barrier(self.WORKERS, timeout=60)
        real_replace = A.os.replace

        def gated_replace(src, dst):
            barrier.wait()  # every worker has fully written+fsynced its temp before any replace
            return real_replace(src, dst)

        outcomes = [None] * self.WORKERS

        def worker(i):
            try:
                A.atomic_write_bytes(target, payloads[i])
                outcomes[i] = "ok"
            except PermissionError as error:  # Windows: replacing a file another replace holds open
                outcomes[i] = f"PermissionError:{getattr(error, 'winerror', None)}"
            except BaseException as error:  # pragma: no cover
                outcomes[i] = repr(error)

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.bin"
            target.write_bytes(b"old")
            with mock.patch.object(A.os, "replace", gated_replace):
                threads = [threading.Thread(target=worker, args=(i,)) for i in range(self.WORKERS)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join(120)
            final = target.read_bytes()
            self.assertIn(final, payloads, "final file must be exactly one complete payload (never mixed/truncated)")
            self.assertGreaterEqual(outcomes.count("ok"), 1, outcomes)
            self.assertTrue(all(o == "ok" or o.startswith("PermissionError") for o in outcomes), outcomes)
            self.assertEqual(temps(tmp), [], "losing writers must remove their temps too")
            self.outcomes = outcomes


if __name__ == "__main__":
    unittest.main()

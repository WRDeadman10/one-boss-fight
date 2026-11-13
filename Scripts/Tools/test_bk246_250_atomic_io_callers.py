"""BK-246..250 (C, implementer; X-2100): post-hotfix caller compatibility and exclusive-create concurrency for
Scripts/Tools/atomic_io.py.

Source scan plus synthetic tests in throwaway OS temp directories only. No production caller is executed and no
project output, lock, real evidence pack, Unreal, build or PIE is touched.
"""
import ast
import re
import sys
import tempfile
import threading
import unittest
import warnings
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import atomic_io as A  # noqa: E402

CALLERS = ["audit_editor_save_safety.py", "evidence_pack.py", "evidence_summary.py", "inventory_editor_asset_writers.py",
           "make_source_manifest.py", "new_rule_scaffold.py", "summarize_encounter_cost.py",
           "summarize_packaged_metrics.py", "token_coverage.py"]
WARNING_CONTROL = re.compile(r"simplefilter|filterwarnings|catch_warnings|PYTHONWARNINGS|-W\s*error|-Werror")


def temps(folder):
    return sorted(p.name for p in Path(folder).iterdir() if p.name.endswith(".tmp"))


def source_files():
    for path in sorted((REPO / "Scripts").rglob("*")):
        if path.suffix in {".py", ".ps1", ".bat", ".cmd"} and "__pycache__" not in path.parts \
                and not path.name.startswith("test_"):
            yield path


def direct_callers():
    found = {}
    for path in source_files():
        if path.suffix != ".py" or path.name == "atomic_io.py":
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", (DeprecationWarning, SyntaxWarning))
            tree = ast.parse(path.read_text(encoding="utf-8-sig", errors="replace"))
        if any(isinstance(n, ast.ImportFrom) and n.module == "atomic_io" for n in ast.walk(tree)):
            found[path.name] = path
    return found


def fail_temp_unlink():
    real = Path.unlink

    def unlink(self, *a, **k):
        if self.name.endswith(".tmp"):
            raise PermissionError("synthetic orphan temp")
        return real(self, *a, **k)
    return unlink


class Bk246CallerInventoryAndFilters(unittest.TestCase):
    def test_exactly_nine_direct_callers(self):
        self.assertEqual(sorted(direct_callers()), CALLERS)

    def test_no_caller_or_launcher_controls_warnings(self):
        """No non-test source (py/ps1/bat/cmd) ignores or promotes warnings, so callers run with Python defaults:
        an orphan-temp RuntimeWarning is printed to stderr once and never changes the exit code."""
        hits = [f"{p.relative_to(REPO)}:{i}" for p in source_files()
                for i, line in enumerate(p.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1)
                if WARNING_CONTROL.search(line)]
        self.assertEqual(hits, [])

    def test_no_repo_level_warning_configuration(self):
        for name in ("pytest.ini", "setup.cfg", "tox.ini", "pyproject.toml", "sitecustomize.py"):
            self.assertFalse((REPO / name).exists(), name)


class Bk248FilterModes(unittest.TestCase):
    MODES = ("default", "ignore", "error")

    def run_create(self, kind, mode):
        with tempfile.TemporaryDirectory() as tmp:
            target, source = Path(tmp) / "out.txt", Path(tmp) / "src.txt"
            source.write_text("payload", encoding="utf-8")
            with warnings.catch_warnings(record=True) as seen, mock.patch.object(Path, "unlink", fail_temp_unlink()):
                warnings.simplefilter(mode)
                A.atomic_create_text(target, "payload") if kind == "text" else A.atomic_create_copy(source, target)
            return target.read_text(encoding="utf-8"), len(temps(tmp)), [w for w in seen
                                                                         if issubclass(w.category, RuntimeWarning)]

    def test_published_create_succeeds_under_every_filter(self):
        for kind in ("text", "copy"):
            for mode in self.MODES:
                with self.subTest(kind=kind, mode=mode):
                    content, orphans, runtime = self.run_create(kind, mode)  # must not raise
                    self.assertEqual(content, "payload")
                    self.assertEqual(orphans, 1)
                    self.assertEqual(len(runtime), 1 if mode == "default" else 0)

    def test_failure_still_raises_under_every_filter(self):
        for mode in self.MODES:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "out.txt"
                target.write_text("keep", encoding="utf-8")
                with warnings.catch_warnings():
                    warnings.simplefilter(mode)
                    with self.assertRaises(FileExistsError):
                        A.atomic_create_text(target, "new")
                self.assertEqual(target.read_text(encoding="utf-8"), "keep")
                self.assertEqual(temps(tmp), [])


class Bk249ConcurrentCreate(unittest.TestCase):
    WORKERS = 8

    def race(self, publish):
        """All workers write their temp, then meet at a barrier placed just before os.link, so every link is
        attempted against the same target at the same point (deterministic contention, not timing luck)."""
        barrier = threading.Barrier(self.WORKERS, timeout=30)
        real_link = A.os.link

        def gated_link(src, dst):
            barrier.wait()
            return real_link(src, dst)

        results = [None] * self.WORKERS

        def worker(i):
            try:
                publish(i)
                results[i] = "won"
            except FileExistsError:
                results[i] = "exists"
            except BaseException as error:  # pragma: no cover - reported via assertion
                results[i] = repr(error)

        with mock.patch.object(A.os, "link", gated_link):
            threads = [threading.Thread(target=worker, args=(i,)) for i in range(self.WORKERS)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(60)
        return results

    def test_exactly_one_winner_for_create_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            results = self.race(lambda i: A.atomic_create_text(target, f"writer-{i}" * 100))
            self.assertEqual(results.count("won"), 1, results)
            self.assertEqual(results.count("exists"), self.WORKERS - 1, results)
            winner = results.index("won")
            self.assertEqual(target.read_text(encoding="utf-8"), f"writer-{winner}" * 100)
            self.assertEqual(temps(tmp), [])

    def test_exactly_one_winner_for_create_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.bin"
            sources = []
            for i in range(self.WORKERS):
                src = Path(tmp) / f"src{i}.bin"
                src.write_bytes(bytes([i]) * 4096)
                sources.append(src)
            results = self.race(lambda i: A.atomic_create_copy(sources[i], target))
            self.assertEqual(results.count("won"), 1, results)
            self.assertEqual(results.count("exists"), self.WORKERS - 1, results)
            self.assertEqual(target.read_bytes(), bytes([results.index("won")]) * 4096)
            self.assertEqual(temps(tmp), [])


if __name__ == "__main__":
    unittest.main()

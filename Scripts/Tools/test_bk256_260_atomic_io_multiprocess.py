"""BK-256..260 (C, implementer; X-2110): multi-process contention and kill-before-publish for Scripts/Tools/atomic_io.py.

Child processes (multiprocessing, spawn start method) write only into throwaway OS temp directories. Each child
installs a TEST-ONLY gate on atomic_io's own os.replace / os.link / Path.mkdir reference inside its own process, so
all children reach the contended step together (deterministic contention, not timing luck). No production caller,
project output, lock, pack, Unreal, build or PIE.
"""
import multiprocessing as mp
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import atomic_io as A  # noqa: E402

CTX = mp.get_context("spawn")
WORKERS = 6
JOIN_TIMEOUT = 120


def temps(folder):
    return sorted(str(p.relative_to(folder)) for p in Path(folder).rglob("*.tmp"))


def site(error):
    """The last atomic_io.py source line on the error's traceback (where the failure surfaced)."""
    import traceback
    frames = [f for f in traceback.extract_tb(error.__traceback__) if f.filename.endswith("atomic_io.py")]
    return f"{frames[-1].name}:{frames[-1].line}" if frames else "outside atomic_io"


def classify(error):
    if error is None:
        return "ok"
    if isinstance(error, FileExistsError):
        return f"FileExistsError@{site(error)}"
    if isinstance(error, PermissionError):
        return f"PermissionError:{getattr(error, 'winerror', None)}@{site(error)}"
    return f"other:{error!r}@{site(error)}"


# ---- child entry points (module level so spawn can import them) ----

def _gate(module_obj, name, barrier):
    real = getattr(module_obj, name)

    def gated(*args, **kwargs):
        barrier.wait()
        return real(*args, **kwargs)
    setattr(module_obj, name, gated)


def child_replace(target, payload_byte, size, barrier, results, index):
    _gate(A.os, "replace", barrier)
    try:
        A.atomic_write_bytes(Path(target), bytes([payload_byte]) * size)
        results[index] = "ok"
    except BaseException as error:  # classified, never swallowed silently
        results[index] = classify(error)


def child_create(target, index, barrier, results):
    _gate(A.os, "link", barrier)
    try:
        A.atomic_create_text(Path(target), f"writer-{index}\n" * 1000)
        results[index] = "ok"
    except BaseException as error:
        results[index] = classify(error)


def child_nested(target, index, barrier, results):
    _gate(A.Path, "mkdir", barrier)  # every writer creates the same missing parent chain at once
    try:
        A.atomic_write_bytes(Path(target), bytes([65 + index]) * 65536)
        results[index] = "ok"
    except BaseException as error:
        results[index] = classify(error)


def child_stall_before_publish(target, ready):
    """Write+flush+fsync the private temp, then stop forever at the publication step until killed."""
    def stalled_replace(src, dst):
        ready.set()
        while True:
            time.sleep(1)
    A.os.replace = stalled_replace
    A.atomic_write_bytes(Path(target), b"new-bytes" * 1000)


# ---- tests ----

def run_children(target_fn, args_for):
    manager = CTX.Manager()
    barrier = manager.Barrier(WORKERS, timeout=90)
    results = manager.list([None] * WORKERS)
    procs = [CTX.Process(target=target_fn, args=args_for(i, barrier, results)) for i in range(WORKERS)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(JOIN_TIMEOUT)
    hung = [p.pid for p in procs if p.is_alive()]
    for p in procs:
        if p.is_alive():
            p.kill()
    out = list(results)
    manager.shutdown()
    return out, hung, [p.exitcode for p in procs]


class Bk256MultiProcessReplace(unittest.TestCase):
    def test_final_bytes_are_one_full_payload(self):
        size = 2 * 1024 * 1024
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.bin"
            target.write_bytes(b"old")
            results, hung, codes = run_children(
                child_replace, lambda i, b, r: (str(target), 65 + i, size, b, r, i))
            self.assertEqual(hung, [])
            self.assertEqual(codes, [0] * WORKERS)
            self.assertTrue(all(r == "ok" or (r.startswith("PermissionError") and "os.replace" in r) for r in results), results)
            self.assertGreaterEqual(results.count("ok"), 1, results)
            final = target.read_bytes()
            self.assertEqual(len(final), size)
            self.assertEqual(len(set(final)), 1, "mixed payload")
            self.assertIn(final[0], [65 + i for i, r in enumerate(results) if r == "ok"],
                          "final bytes must come from a writer that reported success")
            self.assertEqual(temps(tmp), [])
            print(f"\nBK-256 outcomes: {results}", file=sys.stderr)


class Bk257MultiProcessCreate(unittest.TestCase):
    def test_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.txt"
            results, hung, codes = run_children(child_create, lambda i, b, r: (str(target), i, b, r))
            self.assertEqual(hung, [])
            self.assertEqual(codes, [0] * WORKERS)
            self.assertEqual(results.count("ok"), 1, results)
            self.assertEqual(sum(r.startswith("FileExistsError@") and "os.link" in r for r in results), WORKERS - 1, results)
            winner = results.index("ok")
            self.assertEqual(target.read_text(encoding="utf-8"), f"writer-{winner}\n" * 1000)
            self.assertEqual(temps(tmp), [])


class Bk258ConcurrentNestedParent(unittest.TestCase):
    def test_missing_parent_created_by_many_writers(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a" / "b" / "c" / "out.bin"
            results, hung, codes = run_children(child_nested, lambda i, b, r: (str(target), i, b, r))
            self.assertEqual(hung, [])
            self.assertEqual(codes, [0] * WORKERS)
            failures = [r for r in results if r != "ok"]
            self.assertTrue(all(r.startswith("PermissionError") and "os.replace" in r for r in failures),
                            f"only replace contention may fail; never parent creation or temp creation: {results}")
            self.assertGreaterEqual(results.count("ok"), 1, results)
            final = target.read_bytes()
            self.assertEqual(len(final), 65536)
            self.assertEqual(len(set(final)), 1)
            self.assertEqual(temps(tmp), [])
            print(f"\nBK-258 outcomes: {results}", file=sys.stderr)


class Bk259KillBeforePublish(unittest.TestCase):
    def test_killed_writer_leaves_old_bytes_and_an_orphan_temp(self):
        """atomic_io has NO crash cleanup: a writer killed after fsync but before os.replace leaves the destination
        unchanged and its private temp behind. This documents that state; it is not a cleanup guarantee."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "out.bin"
            target.write_bytes(b"old")
            ready = CTX.Event()
            proc = CTX.Process(target=child_stall_before_publish, args=(str(target), ready))
            proc.start()
            try:
                self.assertTrue(ready.wait(60), "child never reached the publication gate")
                orphan = temps(tmp)
                self.assertEqual(len(orphan), 1)
                self.assertEqual((Path(tmp) / orphan[0]).read_bytes(), b"new-bytes" * 1000)  # fully flushed temp
            finally:
                proc.kill()
                proc.join(30)
            self.assertNotEqual(proc.exitcode, 0)
            self.assertEqual(target.read_bytes(), b"old")
            self.assertEqual(len(temps(tmp)), 1, "the orphan temp survives the kill (no crash cleanup)")
            for name in temps(tmp):
                (Path(tmp) / name).unlink()  # test cleanup only


if __name__ == "__main__":
    unittest.main()

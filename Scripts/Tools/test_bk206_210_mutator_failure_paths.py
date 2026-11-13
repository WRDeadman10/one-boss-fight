"""BK-206..210 (C, implementer; X-2054): invocation routes and failure/cleanup paths of the two legacy Python lock
mutators, with exact source anchors.

Source-only: files are READ as text. Neither mutator nor the C-1003 child is imported, run or edited; no lock, log,
temp file, asset, editor or subprocess is touched. Line anchors are asserted so drift is caught. Facts vs risks are
separated in the report; nothing here claims a live event. X-1991 remains open.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETARGET = "Scripts/Editor/retarget_mixamo_backstep.py"
C1003 = "Scripts/Editor/run_c1003_under_lock.py"
CHILD = "Scripts/Editor/set_strong_attack_data_c1003.py"


def lines(rel):
    return (ROOT / rel).read_text(encoding="utf-8-sig", errors="replace").splitlines()


def at(rel, number):
    return lines(rel)[number - 1].strip()


class Bk206InvocationRoutes(unittest.TestCase):
    """Routes, by kind (the BK-201/202 inventory, re-asserted here as anchors)."""

    def test_retarget_entry_points(self):
        self.assertEqual(at(RETARGET, 421), 'if __name__ == "__main__":')        # direct `python` / -ExecutePythonScript run
        self.assertEqual(at(RETARGET, 413), "if not IN_ENGINE:")                 # outside editor -> dry_check only
        self.assertEqual(at(RETARGET, 417), "ok = execute_pipeline()")            # inside editor -> lock + asset writes

    def test_c1003_entry_point_is_module_level(self):
        """No main()/__main__ guard: the lock is taken at IMPORT time (module-level code from :13), so even an
        `import` would mutate the lock - one more reason the audit never imports it."""
        text = "\n".join(lines(C1003))
        self.assertNotIn("__main__", text)
        self.assertEqual(at(C1003, 13), "if os.path.exists(LOCK_PATH):")
        self.assertTrue(lines(C1003)[12].startswith("if "))  # column 0: module level

    def test_child_is_a_standalone_editor_script(self):
        text = "\n".join(lines(CHILD))
        self.assertIn("import unreal", text)
        self.assertNotRegex(text, r"(?i)lock")


class Bk207C1003ChildProcessTrace(unittest.TestCase):
    def test_launch_and_cleanup_ordering(self):
        self.assertEqual(at(C1003, 14), 'print("ERROR: Lock already exists at", LOCK_PATH)')
        self.assertEqual(at(C1003, 15), "sys.exit(1)")                                      # existing lock -> exit 1
        self.assertEqual(at(C1003, 18), 'with open(LOCK_PATH, "w", encoding="utf-8") as f:')  # write BEFORE try
        self.assertEqual(at(C1003, 25), "try:")
        self.assertEqual(at(C1003, 37), "res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)")
        self.assertEqual(at(C1003, 38), 'print("Return code:", res.returncode)')            # printed only
        self.assertEqual(at(C1003, 46), "finally:")
        self.assertEqual(at(C1003, 47), "if os.path.exists(LOCK_PATH):")
        self.assertEqual(at(C1003, 49), "os.remove(LOCK_PATH)")
        self.assertEqual(at(C1003, 50), 'print("[AG] Lock released.")')                     # printed even if :49 skipped

    def test_propagation_facts(self):
        """Exceptions (TimeoutExpired after subprocess.run kills the child, FileNotFoundError for a missing editor, a
        failing os.remove) are NOT caught - only `finally` - so they end the script non-zero; a child non-zero
        return code is never propagated (no sys.exit / check=True / raise on it)."""
        text = "\n".join(lines(C1003))
        self.assertNotRegex(text, r"\bexcept\b")
        self.assertNotRegex(text, r"check=True|sys\.exit\(res|raise\b|exit\(res")
        self.assertEqual(text.count("sys.exit("), 1)  # only the pre-existing-lock exit at :15


class Bk208RetargetFailurePaths(unittest.TestCase):
    def test_acquisition_anchors(self):
        self.assertEqual(at(RETARGET, 94), "if os.path.exists(full_lock):")
        self.assertEqual(at(RETARGET, 98), 'if data.get("owner") != "AG":')
        self.assertEqual(at(RETARGET, 100), "except Exception as e:")                       # re-raises as refusal
        self.assertEqual(at(RETARGET, 101), 'raise RuntimeError(f"Cannot acquire engine lock: {e}")')
        self.assertEqual(at(RETARGET, 107), "os.makedirs(os.path.dirname(full_lock), exist_ok=True)")
        self.assertEqual(at(RETARGET, 108), 'with open(full_lock, "w", encoding="utf-8") as f:')
        self.assertEqual(at(RETARGET, 109), "json.dump(lock_data, f, indent=2)")

    def test_pipeline_and_cleanup_anchors(self):
        self.assertEqual(at(RETARGET, 350), "acquire_engine_lock(proj)")                   # before the try
        self.assertEqual(at(RETARGET, 351), "try:")
        self.assertEqual(at(RETARGET, 371), 'raise RuntimeError("Combat mannequin mesh or IK rig missing.")')
        self.assertEqual(at(RETARGET, 384), 'raise RuntimeError(f"No AnimSequence found in {MIXAMO_PKG} after import.")')
        self.assertEqual(at(RETARGET, 407), "return True")
        self.assertEqual((at(RETARGET, 408), at(RETARGET, 409)), ("finally:", "release_engine_lock(proj)"))

    def test_release_failure_is_swallowed(self):
        self.assertEqual(at(RETARGET, 115), "if os.path.exists(full_lock):")
        self.assertEqual(at(RETARGET, 117), "os.remove(full_lock)")
        self.assertEqual(at(RETARGET, 119), "except Exception as e:")
        self.assertEqual(at(RETARGET, 120), 'log_error(f"Failed to release engine lock: {e}")')  # no re-raise


class Bk209InvariantComparison(unittest.TestCase):
    """Exact mismatches with the C-1155 runner invariants (each a source fact; see report for risks)."""

    def test_exact_mismatches(self):
        r = "\n".join(lines(RETARGET))
        c = "\n".join(lines(C1003))
        for label, text in (("retarget", r), ("c1003", c)):
            with self.subTest(label):
                lock_lines = [l for l in text.splitlines() if "ENGINE_LOCK.json" in l]
                self.assertTrue(lock_lines)
                self.assertTrue(all(re.search(r"Execution[\\/]+ENGINE_LOCK\.json", l) for l in lock_lines),
                                lock_lines)  # every lock path is the Execution lock: the root lock is never used
                self.assertNotRegex(text, r"O_EXCL|'x'|\"x\"|FileMode")         # no exclusive create
                self.assertNotRegex(text, r"uuid|token")                        # no run token
                self.assertNotRegex(text, r"-ceq|owner_token")                  # no ownership-checked release
        self.assertIn("import unreal", r)                                       # takes the lock inside the editor
        self.assertNotRegex(c, r"tasklist|psutil|Get-Process")                  # never checks for a running editor


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from summarize_memory_soak import analyze, parse_log


def sample(route, cycle, stage):
    return {"route": route, "cycle": cycle, "stage": stage, "gc_before_sample": True,
            "objects": {"actors": 90 + (cycle % 2), "bosses": 1, "javelins": 0, "wave_or_projectile": 0},
            "memory": {"working_set_mb": 1000.0 + cycle, "private_mb": 1200.0 + cycle}}


def log_text(route="legacy", final="PASS"):
    rows = [sample(route, 0, "baseline_after_warmup")]
    for cycle in range(1, 51):
        rows.extend((sample(route, cycle, "before_reset"), sample(route, cycle, "after_reset")))
    lines = [f"LogTemp: [MemorySoak] sample {row!r}" for row in rows]
    lines.append(f"LogTemp: [MemorySoak] RESULT route={route} resets=50/50 status={final} reason=complete")
    return "\n".join(lines)


class MemorySoakSummaryTests(unittest.TestCase):
    def test_complete_pair_arm_is_summarized_without_leak_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.log"
            path.write_text(log_text(), encoding="utf-8")
            summary = analyze(parse_log(path))
        self.assertTrue(summary["valid"])
        self.assertEqual(101, summary["samples"])
        self.assertEqual(90, summary["post_actor_min"])
        self.assertEqual(91, summary["post_actor_max"])
        self.assertEqual(49.0, summary["post_private_delta_mb"])

    def test_incomplete_arm_and_missing_gc_marker_are_inconclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "selected.log"
            text = log_text("selected", "INCOMPLETE").replace("'gc_before_sample': True", "'gc_before_sample': False", 1)
            path.write_text(text, encoding="utf-8")
            summary = analyze(parse_log(path))
        self.assertFalse(summary["valid"])
        self.assertTrue(any("PASS 50/50" in issue for issue in summary["issues"]))
        self.assertTrue(any("pre-sample GC" in issue for issue in summary["issues"]))


if __name__ == "__main__":
    unittest.main()

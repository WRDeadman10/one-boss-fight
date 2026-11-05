"""Fixture for grouped FrameworkProof timeline output and raw log-line retention."""
import tempfile
import unittest
from pathlib import Path

from plot_framework_timeline import events


class TimelineGroupingTests(unittest.TestCase):
    def test_identity_carries_across_instance_lines_and_keeps_log_line_numbers(self):
        content = """[2026.11.03-10.00.00:000][  1]LogTemp: Display: [FrameworkProof] playback_start encounter=7 generation=2 instance=41 montage=Move slot=FullBody rate=1 label=Test
not a proof line
[2026.11.03-10.00.01:000][  2]LogTemp: Display: [FrameworkProof] hit instance=41 window=Blade outcome=Accepted hpApplied=10
[2026.11.03-10.00.02:000][  3]LogTemp: Display: [FrameworkProof] encounter_reset generation=3 oldState=Dead executorRearmed=1 bossHealth=250 targetHealth=800
[2026.11.03-10.00.03:000][  4]LogTemp: Display: [FrameworkProof] playback_start encounter=7 generation=3 instance=42 montage=Move slot=FullBody rate=1 label=Test
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.log"
            path.write_text(content, encoding="utf-8")
            rows = events(path)
        self.assertEqual([row[1] for row in rows], [1, 3, 4, 5])
        self.assertEqual([row[3] for row in rows], ["e=7/g=2/i=41", "e=7/g=2/i=41", "e=7/g=3", "e=7/g=3/i=42"])
        self.assertEqual([row[4] for row in rows], ["playback_start", "hit", "encounter_reset", "playback_start"])


if __name__ == "__main__":
    unittest.main()

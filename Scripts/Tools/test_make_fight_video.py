"""Offline fixture checks for game-time concat and owner subtitles."""

import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

try:
    from Scripts.Tools.make_fight_video import parse_log, make_concat, make_ass, trim_leading_frames
except ModuleNotFoundError:
    from make_fight_video import parse_log, make_concat, make_ass, trim_leading_frames


FIXTURE = Path(__file__).with_name("fixtures") / "full_fight_sample.log"
TOOL = Path(__file__).with_name("make_fight_video.py")


class FightVideoTests(unittest.TestCase):
    def test_trim_black_capture_leadin_shifts_subtitles_with_frames(self):
        frames = [(0, 10.0), (1, 10.2), (2, 10.4), (3, 10.6)]
        events = [(0.5, "Light attack"), (0.7, "Guard")]
        kept, shifted = trim_leading_frames(frames, events, 2)
        self.assertEqual(kept, frames[2:])
        self.assertAlmostEqual(shifted[0][0], 0.1)
        self.assertAlmostEqual(shifted[1][0], 0.3)
        with self.assertRaisesRegex(ValueError, "retain at least one"):
            trim_leading_frames(frames, events, 4)

    def test_game_time_durations_and_subtitles(self):
        frames, events = parse_log(FIXTURE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            for index in range(3):
                (folder / f"f_{index:05d}.png").write_bytes(b"png")
            concat = make_concat(frames, folder)
            self.assertIn("duration 0.080000", concat)
            self.assertIn("duration 0.120000", concat)
            self.assertEqual(concat.count("duration "), 3)
            self.assertIn("Guard counter", make_ass(events, 0.32))
            self.assertIn("Boss defeated", make_ass(events, 0.32))

    def test_missing_frame_fails(self):
        frames, _ = parse_log(FIXTURE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError, "missing frame"):
                make_concat(frames, Path(root))

    def test_duplicate_or_nonmonotone_frame_fails(self):
        for tail in ("[FullFight] FRAME 0 g=10.300 action=light", "[FullFight] FRAME 3 g=9.000 action=light"):
            with self.assertRaises(ValueError):
                parse_log(FIXTURE.read_text(encoding="utf-8") + "\n" + tail)

    def test_gap_and_malformed_marker_fail(self):
        for line in ("[FullFight] FRAME 2 g=10.3 action=light", "[FullFight] FRAME 1 g=nan action=light"):
            with self.assertRaises(ValueError):
                parse_log("[FullFight] FRAME 0 g=10.0 action=None\n" + line)

    def test_spaced_frame_folder_and_single_frame_tail(self):
        frames, _ = parse_log("[FullFight] FRAME 0 g=1.0 action=None")
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root) / "frame folder"
            folder.mkdir()
            (folder / "f_00000.png").write_bytes(b"png")
            concat = make_concat(frames, folder)
            self.assertIn("frame folder/f_00000.png'", concat)
            self.assertIn("duration 0.066667", concat)
            self.assertEqual(concat.count("file '"), 2)  # repeated tail frame

    def test_long_event_time_and_out_of_bounds_event(self):
        events = [(3661.25, "air_heavy"), (3662.0, "too late")]
        ass = make_ass(events, 3661.75)
        self.assertIn("1:01:01.25", ass)
        self.assertNotIn("too late", ass)

    def test_ass_escaping(self):
        _, events = parse_log("[FullFight] FRAME 0 g=1.0 action=None\n[FullFight] ACTION foo{bar} t=0.1")
        self.assertIn("foo\\{bar\\}", make_ass(events, 1.0))

    def test_cli_with_spaced_paths_writes_inputs_without_rendering(self):
        with tempfile.TemporaryDirectory() as root:
            root_path = Path(root)
            frames = root_path / "Owner's frame folder"
            output = root_path / "video output"
            frames.mkdir()
            for index in range(3):
                (frames / f"f_{index:05d}.png").write_bytes(b"png")
            result = subprocess.run([sys.executable, "-I", str(TOOL), "--log", str(FIXTURE),
                                     "--frames", str(frames), "--out", str(output)],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("ass=actions.ass", (output / "ffmpeg_command.txt").read_text(encoding="utf-8"))
            self.assertIn("Owner'\\''s frame folder", (output / "frames.ffconcat").read_text(encoding="utf-8"))
            self.assertFalse((output / "fight_review.mp4").exists())


if __name__ == "__main__":
    unittest.main()

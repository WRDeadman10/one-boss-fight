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

    def test_trim_keeps_frame_and_ass_offsets_in_same_capture_timeline(self):
        source_frames = [(i, 10.0 + i * 0.1) for i in range(5)]
        source_events = [(0.15, "discarded early event"), (0.35, "retained event")]
        original_frames = list(source_frames)
        original_events = list(source_events)
        kept, shifted = trim_leading_frames(source_frames, source_events, 2)
        self.assertEqual(source_frames, original_frames)
        self.assertEqual(source_events, original_events)
        self.assertEqual(kept, [(2, 10.2), (3, 10.3), (4, 10.4)])
        self.assertEqual(len(shifted), 1)
        self.assertAlmostEqual(shifted[0][0], 0.15)
        self.assertEqual(shifted[0][1], "retained event")
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            for index in (2, 3, 4):
                (folder / f"f_{index:05d}.png").write_bytes(b"png")
            concat = make_concat(kept, folder)
            self.assertIn("f_00002.png", concat)
            self.assertNotIn("f_00000.png", concat)
        self.assertIn("retained event", make_ass(shifted, 0.3))
        self.assertNotIn("discarded early event", make_ass(shifted, 0.3))

    def test_review_docs_bind_build255_and_build259_findings_to_distinct_captures(self):
        root = Path(__file__).resolve().parents[2]
        build255 = (root / "Documentation/Boss/FIGHT_VIDEO_REVIEW.md").read_text(encoding="utf-8")
        build259 = (root / "Documentation/Boss/FIGHT_VIDEO_REVIEW2_AG.md").read_text(encoding="utf-8")
        self.assertIn("BUILD-255", build255)
        self.assertIn("fight_review.mp4", build255)
        self.assertIn("first six source PNGs", build255)
        self.assertIn("Absent in BUILD-255 video", build255)
        self.assertIn("BUILD-259", build259)
        self.assertIn("fight_review2.mp4", build259)
        self.assertIn("Parry Recoil** | **NOT SEEN**", build259)
        self.assertIn("BUILD-255 `fight_review.mp4` is a separate capture", build259)
        self.assertNotIn("first six source PNGs", build259)

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

    def test_new_run_and_action_ids_preserve_video_parser_frame_compatibility(self):
        source = ("[FullFight] FRAME 0 g=10.0 marker=smoke:frame:00000 action=light action_id=smoke:action:00001\n"
                  "[FullFight] ACTION light t=0.1 id=smoke:action:00001 dist=200")
        frames, events = parse_log(source)
        self.assertEqual(frames, [(0, 10.0)])
        self.assertEqual(events, [(0.1, "Light attack")])

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

    def test_real_parry_contact_is_a_caption_and_requires_an_open_attempt(self):
        valid = ("[FullFight] FRAME 0 g=1.0 action=parry_watch\n"
                 "[FullFight] PARRY_ATTEMPT instance=4 active=True position=0.720 opened=True parried_before=0\n"
                 "[FullFight] PARRY_CONTACT instance=4 t=1.1 parried_delta=1 boss_montage=AM_Boss01_ParryRecoil\n"
                 "[FullFight] PARRY_RECOIL instance=4 t=1.12 montage=AM_Boss01_ParryRecoil\n")
        frames, events = parse_log(valid)
        self.assertEqual(len(frames), 1)
        self.assertIn((1.1, "Successful parry"), events)
        self.assertIn((1.12, "Boss parry recoil"), events)
        self.assertIn("Successful parry", make_ass(events, 2.0))

        for bad in (
                "[FullFight] PARRY_CONTACT instance=4 t=1.1 parried_delta=1 boss_montage=AM_Boss01_ParryRecoil",
                "[FullFight] PARRY_ATTEMPT instance=4 active=True position=0.720 opened=False parried_before=0\n"
                "[FullFight] PARRY_CONTACT instance=4 t=1.1 parried_delta=1 boss_montage=AM_Boss01_ParryRecoil",
                "[FullFight] PARRY_ATTEMPT instance=4 active=True position=0.720 opened=True parried_before=0\n"
                "[FullFight] PARRY_CONTACT instance=4 t=1.1 parried_delta=2 boss_montage=AM_Boss01_ParryRecoil",
                "[FullFight] PARRY_RECOIL instance=4 t=1.12 montage=AM_Boss01_ParryRecoil",
                "[FullFight] PARRY_ATTEMPT instance=4 active=True position=0.720 opened=True parried_before=0\n"
                "[FullFight] PARRY_CONTACT instance=4 t=1.1 parried_delta=1 boss_montage=AnimMontage_2\n"
                "[FullFight] PARRY_RECOIL instance=4 t=1.12 montage=AnimMontage_2",
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                parse_log("[FullFight] FRAME 0 g=1.0 action=None\n" + bad)

    def test_parry_post_contact_frame_marker_references_a_real_captured_frame(self):
        source = ("[FullFight] FRAME 0 g=10.0 action=parry_watch\n"
                  "[FullFight] PARRY_ATTEMPT instance=4 active=True position=0.720 opened=True parried_before=0\n"
                  "[FullFight] PARRY_CONTACT instance=4 t=0.1 parried_delta=1 boss_montage=AM_Boss01_ParryRecoil\n"
                  "[FullFight] FRAME 1 g=10.2 action=None\n"
                  "[FullFight] PARRY_FRAME_READY label=plus_0p05 instance=4 frame=1 t=0.2 actual_offset=0.100 path=D:/frames/f_00001.png\n")
        frames, events = parse_log(source)
        self.assertEqual(frames, [(0, 10.0), (1, 10.2)])
        self.assertIn((0.1, "Successful parry"), events)
        for changed in (source.replace("frame=1", "frame=9"),
                        source.replace("actual_offset=0.100", "actual_offset=-0.100")):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                parse_log(changed)

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

"""test_contact_sheet.py - Unit test suite for contact_sheet.py.

Verifies:
- Windows font path escaping (C: -> C\\:).
- Grid layout computation (CxR).
- Canonical frame indexing formula: frame = round((t_orig - 105.0) * fps) + 1.
- Filtergraph ordering: drawtext -> select -> scale -> tile.
- Scale-relative font sizing: asserts fontsize=80 for width=960, fontsize=160 for width=480 (C-496).
- Bottom-left placement avoiding game HUD: asserts y=h-th- (C-496).
- Safety check: strictly rejects output paths inside the repository.
- Dry-run command construction.

Run: python -I test_contact_sheet.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from contact_sheet import (
    escape_filter_path,
    compute_tile_layout,
    build_ffmpeg_command,
    validate_out_path,
    DEFAULT_VIDEO,
    DEFAULT_FPS,
    DEFAULT_COMBAT_ZERO,
    DEFAULT_LABEL_PX,
    DEFAULT_SOURCE_WIDTH
)


class TestContactSheet(unittest.TestCase):
    def setUp(self):
        self.repo_root = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")
        )

    def test_escape_filter_path(self):
        """Tests that Windows drive letter colons are escaped with backslash."""
        self.assertEqual(
            escape_filter_path(r"C:\Windows\Fonts\arial.ttf"),
            r"C\:/Windows/Fonts/arial.ttf"
        )
        self.assertEqual(
            escape_filter_path("D:/media/font.ttf"),
            r"D\:/media/font.ttf"
        )
        self.assertEqual(
            escape_filter_path("/usr/share/fonts/arial.ttf"),
            "/usr/share/fonts/arial.ttf"
        )

    def test_compute_tile_layout(self):
        """Tests calculation of grid layout 'CxR'."""
        self.assertEqual(compute_tile_layout(40, 5), "5x8")
        self.assertEqual(compute_tile_layout(30, 6), "6x5")
        self.assertEqual(compute_tile_layout(1, 5), "5x1")
        self.assertEqual(compute_tile_layout(0, 5), "5x1")
        self.assertEqual(compute_tile_layout(21, 5), "5x5")

    def test_build_ffmpeg_command_structure(self):
        """Tests command arguments, start frame formula, filtergraph order, and HUD avoidance."""
        start_sec = 112.0
        duration_sec = 2.0
        out_path = "C:/temp/test.png"

        cmd = build_ffmpeg_command(
            video_path=DEFAULT_VIDEO,
            start_sec=start_sec,
            duration_sec=duration_sec,
            out_path=out_path,
            step=3,
            scale_width=960,
            columns=5,
            fps=DEFAULT_FPS,
            combat_zero=DEFAULT_COMBAT_ZERO,
            label_px=DEFAULT_LABEL_PX,
            source_width=DEFAULT_SOURCE_WIDTH
        )

        self.assertEqual(cmd[0], "ffmpeg")
        self.assertIn("-ss", cmd)
        self.assertEqual(cmd[cmd.index("-ss") + 1], "112.000")
        self.assertIn("-t", cmd)
        self.assertEqual(cmd[cmd.index("-t") + 1], "2.000")
        self.assertIn("-i", cmd)
        self.assertIn("-vf", cmd)

        vf = cmd[cmd.index("-vf") + 1]

        # Verify filter order: drawtext -> select -> scale -> tile
        pos_drawtext = vf.find("drawtext=")
        pos_select = vf.find("select=")
        pos_scale = vf.find("scale=")
        pos_tile = vf.find("tile=")

        self.assertTrue(pos_drawtext != -1, "drawtext filter must be present")
        self.assertTrue(pos_select != -1, "select filter must be present")
        self.assertTrue(pos_scale != -1, "scale filter must be present")
        self.assertTrue(pos_tile != -1, "tile filter must be present")

        self.assertTrue(
            pos_drawtext < pos_select < pos_scale < pos_tile,
            f"Filter order violation: expected drawtext < select < scale < tile"
        )

        # Verify canonical start frame formula: round((112.0 - 105.0) * 59.9401) + 1 = 421
        expected_start_frame = round((112.0 - 105.0) * DEFAULT_FPS) + 1
        self.assertEqual(expected_start_frame, 421)
        self.assertIn(f"{expected_start_frame}+n", vf)

        # Verify evidence pattern format in drawtext text
        self.assertIn("morgott_c0_", vf)
        self.assertIn("%{pts\\:hms\\:112.000}", vf)

        # Verify bottom-left placement avoiding HUD (y=h-th-) per C-496
        self.assertIn("y=h-th-", vf)

        # Verify single frame update output
        self.assertIn("-frames:v", cmd)
        self.assertEqual(cmd[cmd.index("-frames:v") + 1], "1")
        self.assertIn("-update", cmd)
        self.assertEqual(cmd[-1], out_path)

    def test_relative_font_sizing_for_960_and_480(self):
        """Tests scale-relative font size calculation per C-496: 20*3840/960=80 and 20*3840/480=160."""
        # Test width 960 -> fontsize 80
        cmd_960 = build_ffmpeg_command(
            video_path=DEFAULT_VIDEO,
            start_sec=110.95,
            duration_sec=0.5,
            out_path="C:/temp/test_960.png",
            scale_width=960,
            label_px=20,
            source_width=3840
        )
        vf_960 = cmd_960[cmd_960.index("-vf") + 1]
        self.assertIn("fontsize=80", vf_960, "Expected fontsize=80 for width=960 (20*3840/960)")

        # Test width 480 -> fontsize 160
        cmd_480 = build_ffmpeg_command(
            video_path=DEFAULT_VIDEO,
            start_sec=110.95,
            duration_sec=0.5,
            out_path="C:/temp/test_480.png",
            scale_width=480,
            label_px=20,
            source_width=3840
        )
        vf_480 = cmd_480[cmd_480.index("-vf") + 1]
        self.assertIn("fontsize=160", vf_480, "Expected fontsize=160 for width=480 (20*3840/480)")

    def test_validate_out_path_rejects_repo_paths(self):
        """Tests that any path inside repository raises ValueError."""
        in_repo_paths = [
            os.path.join(self.repo_root, "output.png"),
            os.path.join(self.repo_root, "Docs", "test.png"),
            os.path.join(self.repo_root, "Documentation", "Boss", "test.png")
        ]
        for p in in_repo_paths:
            with self.assertRaises(ValueError) as ctx:
                validate_out_path(p, self.repo_root)
            self.assertIn("SAFETY VIOLATION", str(ctx.exception))

    def test_validate_out_path_permits_outside_paths(self):
        """Tests that paths outside repository pass validation without error."""
        out_paths = [
            "C:/temp/test.png",
            "C:/Windows/Temp/test.png",
            "D:/scratch/test.png"
        ]
        for p in out_paths:
            try:
                validate_out_path(p, self.repo_root)
            except ValueError:
                self.fail(f"validate_out_path unexpectedly failed on external path '{p}'")


if __name__ == "__main__":
    unittest.main(verbosity=2)

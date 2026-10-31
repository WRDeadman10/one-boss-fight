"""Re-open tests for KI146_DODGE_ACTION_NOTES.md.
Verifies that the key claims are backed by the source files cited.
Run: python -I test_reopen_ki146_dodge_notes.py
"""
import os
import re
import sys
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
SCRIPTS = os.path.join(ROOT, "Scripts", "Editor")
SOURCE = os.path.join(ROOT, "Source", "OneBossFight", "Player")
F4_LOG = os.path.join(ROOT, "Docs", "BossCombatReview", "Execution", "Claude", "F4",
                      "dodge_run1", "editor_raw.log")
NOTES = os.path.join(os.path.dirname(__file__), "KI146_DODGE_ACTION_NOTES.md")


def read(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace")


class TestNotesFileExists(unittest.TestCase):
    def test_notes_file_exists(self):
        self.assertTrue(os.path.exists(NOTES), "KI146_DODGE_ACTION_NOTES.md not found")

    def test_notes_file_crlf(self):
        with open(NOTES, "rb") as f:
            raw = f.read()
        lines_lf = raw.replace(b"\r\n", b"\n").split(b"\n")
        crlf_lines = raw.split(b"\r\n")
        # Every \n should be preceded by \r
        lone_lf = raw.count(b"\n") - raw.count(b"\r\n")
        self.assertEqual(lone_lf, 0, "Notes file has %d bare LF (not CRLF)" % lone_lf)


class TestPieIframesScript(unittest.TestCase):
    """Claims about pie_iframes.py"""

    @classmethod
    def setUpClass(cls):
        cls.src = read(os.path.join(SCRIPTS, "pie_iframes.py"))

    def test_uses_set_key_down_not_inject_action_for_dodge(self):
        # The script calls set_key_down for the DODGE constant
        self.assertIn("set_key_down", self.src,
                      "pie_iframes.py must call set_key_down")
        # It does NOT use inject_action for the dodge
        # (inject_action may appear in imports/comments but not as the dodge trigger)
        self.assertNotIn("inject_action", self.src,
                         "pie_iframes.py must NOT use inject_action (dodge is via set_key_down)")

    def test_dodge_constant_is_face_button_right(self):
        self.assertIn('Gamepad_FaceButton_Right', self.src,
                      "DODGE key must be Gamepad_FaceButton_Right")

    def test_quick_montage_name(self):
        self.assertIn("Dodge_Small_Forward_Roll_Montage", self.src)

    def test_full_montage_name(self):
        self.assertIn("Dodge_To_Idle_Montage", self.src)

    def test_quick_window_start(self):
        self.assertIn("0.10718", self.src, "Quick i-frame window start 0.10718")

    def test_quick_window_end(self):
        self.assertIn("0.48975", self.src, "Quick i-frame window end 0.48975")

    def test_full_window_end(self):
        self.assertIn("0.69987", self.src, "Full i-frame window end 0.69987")


class TestDrivePieScript(unittest.TestCase):
    """Claims about drive_pie.py (the new -DodgeAction path)"""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "Docs", "BossCombatReview", "Execution",
                            "Claude", "F4", "drive_pie.py")
        cls.src = read(path)

    def test_inject_action_for_ia_dodge(self):
        self.assertIn("inject_action", self.src)
        self.assertIn("IA_Dodge", self.src)

    def test_hold_duration_012(self):
        self.assertIn("0.12", self.src, "hold duration 0.12 s per press")


class TestPieHitIntake(unittest.TestCase):
    """inject_action pattern is the proven approach in pie_hit_intake.py"""

    @classmethod
    def setUpClass(cls):
        cls.src = read(os.path.join(SCRIPTS, "pie_hit_intake.py"))

    def test_inject_action_present(self):
        self.assertIn("inject_action", self.src)

    def test_ia_actions_listed(self):
        for ia in ("IA_NormalAttack", "IA_StrongAttack", "IA_ChargedAttack"):
            self.assertIn(ia, self.src, "Expected action %s in pie_hit_intake" % ia)


class TestIFrameMonitorHeader(unittest.TestCase):
    """Claims about RPGIFrameMonitor.h"""

    @classmethod
    def setUpClass(cls):
        cls.src = read(os.path.join(SOURCE, "RPGIFrameMonitor.h"))

    def test_notify_state_class_name(self):
        self.assertIn("ANS_iFrames_C", self.src)

    def test_status_invulnerable_mentioned(self):
        self.assertIn("Status.Invulnerable", self.src)


class TestIFrameMonitorCpp(unittest.TestCase):
    """Claims about RPGIFrameMonitor.cpp"""

    @classmethod
    def setUpClass(cls):
        cls.src = read(os.path.join(SOURCE, "RPGIFrameMonitor.cpp"))

    def test_read_window_walks_notifies(self):
        self.assertIn("ReadWindow", self.src)
        self.assertIn("Notifies", self.src)

    def test_notify_state_class_fName_match(self):
        self.assertIn("NotifyStateClassName", self.src)
        self.assertIn("GetFName", self.src)

    def test_log_category(self):
        self.assertIn("LogRPGIFrame", self.src)

    def test_invulnerable_on_log(self):
        self.assertIn("invulnerable on", self.src)


class TestDamageResolverCpp(unittest.TestCase):
    """Claims about RPGDamageResolver.cpp"""

    @classmethod
    def setUpClass(cls):
        cls.src = read(os.path.join(SOURCE, "RPGDamageResolver.cpp"))

    def test_rejected_invulnerable_outcome(self):
        self.assertIn("RejectedInvulnerable", self.src)

    def test_status_invulnerable_reason(self):
        self.assertIn("Status.Invulnerable", self.src)

    def test_log_category(self):
        self.assertIn("LogRPGDamage", self.src)

    def test_record_ue_log_format(self):
        # The UE_LOG call references both the outcome and health values
        self.assertIn("health %.1f", self.src)

    def test_invulnerability_check(self):
        self.assertIn("IsInvulnerable", self.src)


class TestDodgeTimingHeader(unittest.TestCase):
    """Claims about RPGDodgeTiming.h"""

    @classmethod
    def setUpClass(cls):
        cls.src = read(os.path.join(SOURCE, "RPGDodgeTiming.h"))

    def test_double_tap_window_default(self):
        self.assertIn("0.30", self.src, "DoubleTapWindow default 0.30 s")

    def test_dodge_action_property(self):
        # The .h declares DodgeAction as a TSoftObjectPtr<UInputAction>; "IA_Dodge" is in the .cpp
        self.assertIn("DodgeAction", self.src,
                      "DodgeAction UPROPERTY must be in RPGDodgeTiming.h")

    def test_quick_montage_property(self):
        self.assertIn("QuickMontage", self.src)

    def test_full_montage_property(self):
        self.assertIn("FullMontage", self.src)


class TestDodgeTimingCpp(unittest.TestCase):
    """Claims about RPGDodgeTiming.cpp"""

    @classmethod
    def setUpClass(cls):
        cls.src = read(os.path.join(SOURCE, "RPGDodgeTiming.cpp"))

    def test_ia_dodge_asset_path(self):
        self.assertIn("IA_Dodge.IA_Dodge", self.src,
                      "IA_Dodge soft-object path in RPGDodgeTiming.cpp")

    def test_bound_log_line(self):
        self.assertIn("dodge timing bound to", self.src)

    def test_double_tap_window_log(self):
        self.assertIn("double tap window", self.src)


class TestCrashLog(unittest.TestCase):
    """Claims about the dodge_run1 crash log"""

    @classmethod
    def setUpClass(cls):
        cls.log = read(F4_LOG) if os.path.exists(F4_LOG) else ""

    def test_log_exists(self):
        self.assertTrue(os.path.exists(F4_LOG), "dodge_run1/editor_raw.log not found")

    def test_bp_advanced_player_controller_compile_error(self):
        self.assertIn("BP_AdvancedPlayerController", self.log)
        self.assertIn("COMPILER ERROR", self.log,
                      "Expected compiler error for BP_AdvancedPlayerController")

    def test_class_default_object_ensure(self):
        self.assertIn("ClassDefaultObject != nullptr", self.log)

    def test_access_violation(self):
        self.assertIn("EXCEPTION_ACCESS_VIOLATION", self.log)

    def test_dodge_timing_bound_log(self):
        self.assertIn("dodge timing bound to IA_Dodge", self.log)

    def test_deactivate_widget_missing(self):
        self.assertIn("DeactivateWidget", self.log,
                      "Expected broken DeactivateWidget reference in crash log")

    def test_set_key_down_was_used_not_inject(self):
        # The old driver used set_key_down; the log shows F3D prefix (old driver)
        self.assertIn("[F3D] dodge key", self.log,
                      "Old driver (F3D prefix with set_key_down) was used in dodge_run1")


if __name__ == "__main__":
    unittest.main(verbosity=2)

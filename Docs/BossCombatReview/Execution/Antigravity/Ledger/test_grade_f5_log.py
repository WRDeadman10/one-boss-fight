"""
test_grade_f5_log.py
====================
Unit tests for Antigravity F5 Multi-Attack PIE Grader (Order A-286).
Runs 100% offline with zero engine dependency.
Verifies all 8 validation checks across pass and targeted failure synthetic logs:
1. Valid 2-attack log (PASS)
2. Unhandled ERROR line (FAIL)
3. Decision missing or after playback_start (FAIL)
4. Same card repeated / no diversity (FAIL)
5. Missing cooldown refusal on second decision (FAIL)
6. Event timing deviation (FAIL)
7. Missing or incomplete cleanup lines (FAIL)
8. HP invariant mismatch (FAIL)
9. Incorrect attack count (FAIL)
"""

import unittest
from typing import List
from pathlib import Path
import sys

# Ensure current directory is on sys.path
cur_dir = str(Path(__file__).resolve().parent)
if cur_dir not in sys.path:
    sys.path.insert(0, cur_dir)

from grade_f5_log import grade_f5_log_lines, FALLBACK_CARD_SPECS


def make_valid_f5_log() -> List[str]:
    """Generates a synthetic passing 2-attack F5 log."""
    return [
        "[FrameworkProof] dependencies mesh=Sevarog resolved=1 label=F5_fixture",
        "[FrameworkProof] walk start=X=500 rangeCm=165.0 bandMin=150 bandMax=180",
        # Attack 1: SwingSlow (uses attack=<n> as emitted by live boss character)
        "[FrameworkProof] decision attack=1 chosen=Move_Sevarog_SwingSlow_F5 score=1.85 range=165.0",
        "[FrameworkProof] candidate attack=1 card=Move_Sevarog_SwingMedium_F5 score=1.20",
        "[FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=Montage_0 slot=FullBody rate=1.0",
        "[FrameworkProof] playback instance=1 position=0.10 nodeWeight=1 montageWeight=1",
        "[FrameworkProof] event encounter=1 generation=1 instance=1 kind=Open window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.35 label=F5_fixture",
        "[FrameworkProof] sweep instance=1 window=Window_SwingSlow_Primary from=0.35 to=0.40 substeps=3",
        "[FrameworkProof] hit instance=1 window=Window_SwingSlow_Primary key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=800 healthAfter=765",
        "[FrameworkProof] event encounter=1 generation=1 instance=1 kind=Close window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.4917 label=F5_fixture",
        "[FrameworkProof] event encounter=1 generation=1 instance=1 kind=Finished window=None group=None localSeconds=1.65 label=F5_fixture",
        "[FrameworkProof] cleanup instance=1 reason=Finished modelIdle=1 ownedMontageStopped=1",
        # Attack 2: SwingMedium (with cooldown refusal for SwingSlow)
        "[FrameworkProof] refusal attack=2 card=Move_Sevarog_SwingSlow_F5 reason=Selector.Cooldown",
        "[FrameworkProof] decision attack=2 chosen=Move_Sevarog_SwingMedium_F5 score=1.45 range=150.0",
        "[FrameworkProof] candidate instance=2 card=Move_Sevarog_AntiGreed_F5 score=1.10",
        "[FrameworkProof] playback_start encounter=1 generation=1 instance=2 montage=Montage_1 slot=FullBody rate=1.0",
        "[FrameworkProof] playback instance=2 position=0.05 nodeWeight=1 montageWeight=1",
        "[FrameworkProof] event encounter=1 generation=1 instance=2 kind=Open window=Window_SwingMedium_Sweep group=HitGroup_ScytheBlade localSeconds=0.1917 label=F5_fixture",
        "[FrameworkProof] sweep instance=2 window=Window_SwingMedium_Sweep from=0.19 to=0.25 substeps=3",
        "[FrameworkProof] hit instance=2 window=Window_SwingMedium_Sweep key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=25 healthBefore=765 healthAfter=740",
        "[FrameworkProof] event encounter=1 generation=1 instance=2 kind=Close window=Window_SwingMedium_Sweep group=HitGroup_ScytheBlade localSeconds=0.2667 label=F5_fixture",
        "[FrameworkProof] event encounter=1 generation=1 instance=2 kind=Finished window=None group=None localSeconds=1.10 label=F5_fixture",
        "[FrameworkProof] cleanup instance=2 reason=Finished modelIdle=1 ownedMontageStopped=1",
        # Final Invariant & Teardown
        "[FrameworkProof] invariant targetHPBefore=800 targetHPAfter=740 expectedHP=740 acceptedHits=2 appliedDamage=60",
        "[FrameworkProof] RESULT outcome=CompletedMultiAttack"
    ]


class TestGradeF5Log(unittest.TestCase):

    def test_valid_two_attack_run(self):
        """Clean valid 2-attack log passes all 8 checks."""
        lines = make_valid_f5_log()
        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertTrue(report["passed"], f"Expected pass, got errors: {report['errors']}")
        self.assertEqual(len(report["errors"]), 0)
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["parsed_data"]["accepted_hit_count"], 2)
        self.assertEqual(report["parsed_data"]["total_damage_from_hits"], 60.0)

    def test_fail_error_token(self):
        """Log containing an engine ERROR token fails check."""
        lines = make_valid_f5_log()
        lines.insert(5, "[FrameworkProof] ERROR: SkeletalMesh socket not found")
        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["no_error_tokens"])
        self.assertTrue(any("ERROR" in e for e in report["errors"]))

    def test_fail_decision_missing_or_after_playback(self):
        """Decision placed after playback_start fails ordering check."""
        lines = make_valid_f5_log()
        # Swap decision instance=1 and playback_start instance=1
        dec_idx = next(i for i, l in enumerate(lines) if "decision" in l and ("instance=1" in l or "attack=1" in l))
        pb_idx = next(i for i, l in enumerate(lines) if "playback_start" in l and "instance=1" in l)
        lines[dec_idx], lines[pb_idx] = lines[pb_idx], lines[dec_idx]

        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["decision_precedes_playback"])
        self.assertTrue(any("did not precede playback_start" in e for e in report["errors"]))

    def test_fail_same_card_repeated(self):
        """Both attacks selecting the same card fails diversity check."""
        lines = make_valid_f5_log()
        # Force second attack to also choose SwingSlow
        for i, l in enumerate(lines):
            if "decision" in l and ("instance=2" in l or "attack=2" in l):
                lines[i] = "[FrameworkProof] decision attack=2 chosen=Move_Sevarog_SwingSlow_F5 score=1.45 range=150.0"
                break

        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["distinct_moves_selected"])
        self.assertTrue(any("identical move card" in e for e in report["errors"]))

    def test_fail_missing_cooldown_refusal(self):
        """Second decision lacking cooldown refusal for first card fails check."""
        lines = [l for l in make_valid_f5_log() if not ("refusal" in l and ("instance=2" in l or "attack=2" in l))]
        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["cooldown_refusal_on_second_decision"])
        self.assertTrue(any("did not trace a Cooldown refusal" in e for e in report["errors"]))

    def test_fail_event_timing_deviation(self):
        """Event timing deviating from spec fails timeline check."""
        lines = make_valid_f5_log()
        # Corrupt Open timing for instance 1 from 0.35 to 0.10
        for i, l in enumerate(lines):
            if "kind=Open" in l and "instance=1" in l:
                lines[i] = "[FrameworkProof] event encounter=1 generation=1 instance=1 kind=Open window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.10 label=F5_fixture"
                break

        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["event_timings_match_specs"])
        self.assertTrue(any("Open timing" in e for e in report["errors"]))

    def test_fail_missing_cleanup(self):
        """Missing second cleanup line fails cleanup check."""
        lines = [l for l in make_valid_f5_log() if not (l.startswith("[FrameworkProof] cleanup") and "instance=2" in l)]
        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["cleanups_exact_two"])
        self.assertTrue(any("Expected exactly 2 clean finish cleanups" in e for e in report["errors"]))

    def test_fail_hp_mismatch(self):
        """HP after not matching applied damage fails invariant check."""
        lines = make_valid_f5_log()
        for i, l in enumerate(lines):
            if l.startswith("[FrameworkProof] invariant"):
                lines[i] = "[FrameworkProof] invariant targetHPBefore=800 targetHPAfter=700 expectedHP=700 acceptedHits=2 appliedDamage=60"
                break

        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["target_hp_invariant"])
        self.assertTrue(any("Invariant mismatch" in e for e in report["errors"]))

    def test_fail_wrong_attack_count(self):
        """Only one attack executed fails attack count check."""
        # Truncate log right after attack 1 cleanup
        idx = next(i for i, l in enumerate(make_valid_f5_log()) if "cleanup instance=1" in l)
        lines = make_valid_f5_log()[:idx+1]
        lines.append("[FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35")
        lines.append("[FrameworkProof] RESULT outcome=CompletedSingleAttack")

        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertFalse(report["passed"])
        self.assertFalse(report["checks"]["two_attacks_executed"])
        self.assertTrue(any("Expected exactly 2 sequential attacks" in e for e in report["errors"]))

    def test_valid_legacy_instance_tokens(self):
        """Valid 2-attack log with legacy instance= tokens passes."""
        lines = [
            "[FrameworkProof] dependencies mesh=Sevarog resolved=1 label=F5_fixture",
            "[FrameworkProof] decision instance=1 chosen=Move_Sevarog_SwingSlow_F5 score=1.85 range=165.0",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=Montage_0 slot=FullBody rate=1.0",
            "[FrameworkProof] event encounter=1 generation=1 instance=1 kind=Open window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.35 label=F5_fixture",
            "[FrameworkProof] hit instance=1 window=Window_SwingSlow_Primary key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=800 healthAfter=765",
            "[FrameworkProof] event encounter=1 generation=1 instance=1 kind=Close window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.4917 label=F5_fixture",
            "[FrameworkProof] event encounter=1 generation=1 instance=1 kind=Finished window=None group=None localSeconds=1.65 label=F5_fixture",
            "[FrameworkProof] cleanup instance=1 reason=Finished modelIdle=1 ownedMontageStopped=1",
            "[FrameworkProof] refusal instance=2 card=Move_Sevarog_SwingSlow_F5 reason=Selector.Cooldown",
            "[FrameworkProof] decision instance=2 chosen=Move_Sevarog_SwingMedium_F5 score=1.45 range=150.0",
            "[FrameworkProof] playback_start encounter=1 generation=1 instance=2 montage=Montage_1 slot=FullBody rate=1.0",
            "[FrameworkProof] event encounter=1 generation=1 instance=2 kind=Open window=Window_SwingMedium_Sweep group=HitGroup_ScytheBlade localSeconds=0.1917 label=F5_fixture",
            "[FrameworkProof] hit instance=2 window=Window_SwingMedium_Sweep key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=25 healthBefore=765 healthAfter=740",
            "[FrameworkProof] event encounter=1 generation=1 instance=2 kind=Close window=Window_SwingMedium_Sweep group=HitGroup_ScytheBlade localSeconds=0.2667 label=F5_fixture",
            "[FrameworkProof] event encounter=1 generation=1 instance=2 kind=Finished window=None group=None localSeconds=1.10 label=F5_fixture",
            "[FrameworkProof] cleanup instance=2 reason=Finished modelIdle=1 ownedMontageStopped=1",
            "[FrameworkProof] invariant targetHPBefore=800 targetHPAfter=740 expectedHP=740 acceptedHits=2 appliedDamage=60",
            "[FrameworkProof] RESULT outcome=CompletedMultiAttack"
        ]
        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertTrue(report["passed"], f"Expected pass, got errors: {report['errors']}")


    def test_attack_miss_warning_invariant_pass(self):
        """When an attack misses (KI-147, e.g. AntiGreed at far range), invariant holds and passes with WARNING."""
        lines = make_valid_f5_log()
        # Remove hit for attack 2 (simulating a miss)
        lines = [l for l in lines if not (l.startswith("[FrameworkProof] hit") and "instance=2" in l)]
        # Update invariant to reflect only 1 hit accepted (damage=35, targetHPAfter=765, expectedHP=765)
        for i, l in enumerate(lines):
            if l.startswith("[FrameworkProof] invariant"):
                lines[i] = "[FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35"
                break

        report = grade_f5_log_lines(lines, card_specs=FALLBACK_CARD_SPECS)
        self.assertTrue(report["passed"], f"Expected PASS for valid invariant with miss, got: {report['errors']}")
        self.assertTrue(report["checks"]["target_hp_invariant"])
        self.assertEqual(len(report["warnings"]), 1)
        self.assertIn("KI-147", report["warnings"][0])
        self.assertIn("hits=1 < attacks=2", report["warnings"][0])


if __name__ == "__main__":
    unittest.main()

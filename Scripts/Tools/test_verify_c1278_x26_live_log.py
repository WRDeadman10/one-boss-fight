#!/usr/bin/env python3
"""Offline tests for the C-1278 live-log verifier."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("verify_c1278_x26_live_log.py")
SPEC = importlib.util.spec_from_file_location("verify_c1278_x26_live_log", SCRIPT)
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def good_log():
    lines = [
        "[FrameworkProof] refusal attack=1 card=%s reason=MoveModel.Phase seq=1" % VERIFY.S6,
        "[FrameworkProof] refusal attack=1 card=%s reason=MoveModel.Phase seq=1" % VERIFY.S8,
        "[FrameworkProof] phase_transition attack=2 from=Phase_1 to=Phase_2 health=150 max=250 fraction=0.6",
        # S6 and S8 have disjoint range bands, so positive P2 evidence needs
        # separate selector decisions after the phase transition.
        "[FrameworkProof] candidate attack=3 card=%s score=1 seq=4" % VERIFY.S6,
        "[FrameworkProof] candidate attack=4 card=%s score=1 seq=5" % VERIFY.S8,
        "[FrameworkProof] candidate attack=4 card=Move_Sevarog_Swing1_Medium score=1 seq=5",
        "[FrameworkProof] hit instance=1 window=W key=HitGroup_ScytheBlade outcome=Accepted hpApplied=65 healthBefore=800 healthAfter=735",
        "[FrameworkProof] SETUP stage=before_request move=%s requestedRangeCm=120 actualDistanceCm=120 cardBandCm=90..150 inBand=1" % VERIFY.S6,
        "[FrameworkProof] area_effect state=Released instance=2 card=%s center=X=0 Y=0 Z=0 cardTime=0.8 release=0.8 delay=0.75 radius=225" % VERIFY.S7,
        "[FrameworkProof] S7_RELEASE_SAMPLE elapsedAfterStart=0.8 playerGround=(0,0,0) bossGround=(0,500,0)",
        "[FrameworkProof] area_effect state=Resolve instance=2 distanceCm=10 radiusCm=225 targetRadiusCm=60 inside=1 cardTime=1.55",
        "[FrameworkProof] area_effect_damage instance=2 outcome=Accepted hpApplied=35 healthBefore=800 healthAfter=765",
        "[FrameworkProof] area_effect_snare state=Started instance=2 scale=0.55 seconds=2.5 baseSpeed=600",
        "[FrameworkProof] area_effect_snare state=Ended restored=1",
        "[FrameworkProof] channel state=Started instance=3 card=%s start=0.267 end=1.267 tickInterval=0.2 facingYaw=0 trackFacing=0" % VERIFY.S8,
    ]
    for index, time in enumerate(VERIFY.TICKS, 1):
        lines.append("[FrameworkProof] channel_tick instance=3 tick=%d cardTime=%s rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4" % (index, time))
    lines.append("[FrameworkProof] channel state=Ended instance=3 ticks=5")
    return "\n".join(lines)


class X26LiveLogVerifierTests(unittest.TestCase):
    def test_complete_stationary_log_passes_every_table_row(self):
        rows = VERIFY.verify(good_log())
        self.assertEqual([row["status"] for row in rows], ["PASS"] * 7)
        self.assertTrue(all(row["evidence"] for row in rows))

    def test_synthetic_pass_fixtures_cover_each_c1278_row(self):
        rows = VERIFY.verify(good_log())
        self.assertEqual([row["row"] for row in rows], [
            "X26-P1", "X26-P2", "X26-S6", "X26-S7a", "X26-S7b", "X26-S8a", "X26-S8b"
        ])
        self.assertTrue(all(row["status"] == "PASS" and row["evidence"] for row in rows))

    def test_accepts_scoped_damage_outcome_enum_emitted_by_cpp(self):
        log = good_log().replace("outcome=Accepted", "outcome=ERPGDamageOutcome::Accepted")
        log = log.replace("outcome=Miss", "outcome=ERPGDamageOutcome::Miss")
        rows = VERIFY.verify(log)
        self.assertEqual([row["status"] for row in rows], ["PASS"] * 7)

    def test_phase_rows_fail_closed_for_missing_duplicate_and_out_of_order_transition(self):
        log = good_log().replace(
            "[FrameworkProof] phase_transition attack=2 from=Phase_1 to=Phase_2 health=150 max=250 fraction=0.6\n", "")
        rows = {row["row"]: row for row in VERIFY.verify(log)}
        self.assertEqual(rows["X26-P2"]["status"], "FAIL")
        duplicate = good_log().replace(
            "[FrameworkProof] candidate attack=3 card=%s score=1 seq=4" % VERIFY.S6,
            "[FrameworkProof] phase_transition attack=4 from=Phase_1 to=Phase_2 health=140 max=250 fraction=0.56\n"
            "[FrameworkProof] candidate attack=3 card=%s score=1 seq=4" % VERIFY.S6)
        rows = {row["row"]: row for row in VERIFY.verify(duplicate)}
        self.assertEqual(rows["X26-P2"]["status"], "FAIL")
        out_of_order = good_log().replace(
            "[FrameworkProof] phase_transition attack=2 from=Phase_1 to=Phase_2 health=150 max=250 fraction=0.6\n", "")
        out_of_order = out_of_order.replace(
            "[FrameworkProof] candidate attack=3 card=%s score=1 seq=4" % VERIFY.S6,
            "[FrameworkProof] candidate attack=3 card=%s score=1 seq=4\n"
            "[FrameworkProof] phase_transition attack=2 from=Phase_1 to=Phase_2 health=150 max=250 fraction=0.6" % VERIFY.S6)
        rows = {row["row"]: row for row in VERIFY.verify(out_of_order)}
        self.assertEqual(rows["X26-P1"]["status"], "FAIL")

    def test_s6_bad_range_and_wrong_hit_count_fail(self):
        bad_range = good_log().replace("actualDistanceCm=120 cardBandCm=90..150 inBand=1",
                                       "actualDistanceCm=151 cardBandCm=90..150 inBand=0")
        rows = {row["row"]: row for row in VERIFY.verify(bad_range)}
        self.assertEqual(rows["X26-S6"]["status"], "FAIL")
        duplicate_hit = good_log().replace(
            "[FrameworkProof] area_effect state=Released instance=2",
            "[FrameworkProof] hit instance=1 window=W key=HitGroup_ScytheBlade outcome=Accepted hpApplied=65 healthBefore=735 healthAfter=670\n"
            "[FrameworkProof] area_effect state=Released instance=2")
        rows = {row["row"]: row for row in VERIFY.verify(duplicate_hit)}
        self.assertEqual(rows["X26-S6"]["status"], "FAIL")

    def test_s6_first_card_accepts_initialize_and_request_setup_pair(self):
        log = good_log().replace(
            "[FrameworkProof] SETUP stage=before_request move=%s requestedRangeCm=120 actualDistanceCm=120 cardBandCm=90..150 inBand=1" % VERIFY.S6,
            "[FrameworkProof] SETUP stage=before_initialize move=%s requestedRangeCm=120 actualDistanceCm=120 cardBandCm=90..150 inBand=1\n" % VERIFY.S6
            + "[FrameworkProof] SETUP stage=before_request move=%s requestedRangeCm=120 actualDistanceCm=120 cardBandCm=90..150 inBand=1" % VERIFY.S6)
        rows = {row["row"]: row for row in VERIFY.verify(log)}
        self.assertEqual(rows["X26-S6"]["status"], "PASS")
        setup_evidence = rows["X26-S6"]["evidence"][:2]
        self.assertIn("stage=before_initialize", setup_evidence[0])
        self.assertIn("stage=before_request", setup_evidence[1])

    def test_s6_duplicate_request_setup_still_fails(self):
        line = "[FrameworkProof] SETUP stage=before_request move=%s requestedRangeCm=120 actualDistanceCm=120 cardBandCm=90..150 inBand=1" % VERIFY.S6
        log = good_log().replace(line, line + "\n" + line)
        rows = {row["row"]: row for row in VERIFY.verify(log)}
        self.assertEqual(rows["X26-S6"]["status"], "FAIL")

    def test_s7_wrong_damage_early_resolve_and_missing_restore_fail(self):
        wrong_damage = good_log().replace("hpApplied=35 healthBefore=800", "hpApplied=36 healthBefore=800")
        rows = {row["row"]: row for row in VERIFY.verify(wrong_damage)}
        self.assertEqual(rows["X26-S7b"]["status"], "FAIL")
        early = good_log().replace("distanceCm=10 radiusCm=225 targetRadiusCm=60 inside=1 cardTime=1.55",
                                   "distanceCm=10 radiusCm=225 targetRadiusCm=60 inside=1 cardTime=1.54")
        rows = {row["row"]: row for row in VERIFY.verify(early)}
        self.assertEqual(rows["X26-S7a"]["status"], "FAIL")
        no_restore = good_log().replace("area_effect_snare state=Ended restored=1", "area_effect_snare state=Ended restored=0")
        rows = {row["row"]: row for row in VERIFY.verify(no_restore)}
        self.assertEqual(rows["X26-S7b"]["status"], "FAIL")

    def test_phase_transition_duplicate_fails_phase_two(self):
        log = good_log().replace(
            "[FrameworkProof] candidate attack=4 card=%s score=1 seq=5" % VERIFY.S8,
            "[FrameworkProof] phase_transition attack=5 from=Phase_1 to=Phase_2 health=140 max=250 fraction=0.6\n"
            "[FrameworkProof] candidate attack=4 card=%s score=1 seq=5" % VERIFY.S8)
        rows = {row["row"]: row for row in VERIFY.verify(log)}
        self.assertEqual(rows["X26-P2"]["status"], "FAIL")

    def test_phase_two_requires_two_distinct_selector_decisions(self):
        same_decision = good_log().replace("seq=5", "seq=4")
        rows = {row["row"]: row for row in VERIFY.verify(same_decision)}
        self.assertEqual(rows["X26-P2"]["status"], "FAIL")

    def test_phase_two_requires_both_phase_two_only_candidates(self):
        for missing_card in (VERIFY.S6, VERIFY.S8):
            with self.subTest(missing_card=missing_card):
                log = good_log().replace(
                    "[FrameworkProof] candidate attack=%s card=%s score=1 seq=%s\n" %
                    ((3, VERIFY.S6, 4) if missing_card == VERIFY.S6 else (4, VERIFY.S8, 5)), "")
                rows = {row["row"]: row for row in VERIFY.verify(log)}
                self.assertEqual(rows["X26-P2"]["status"], "FAIL")

    def test_phase_two_empty_pool_refusal_fails(self):
        log = good_log().replace(
            "[FrameworkProof] candidate attack=3 card=%s score=1 seq=4\n" % VERIFY.S6,
            "[FrameworkProof] autonomous_test_refusal attack=5 reason=NoCandidate seq=6\n"
            "[FrameworkProof] candidate attack=3 card=%s score=1 seq=4\n" % VERIFY.S6)
        rows = {row["row"]: row for row in VERIFY.verify(log)}
        self.assertEqual(rows["X26-P2"]["status"], "FAIL")

    def test_s7_outside_damage_is_rejected_in_dodge_out_case(self):
        log = good_log().replace("inside=1", "inside=0").replace("distanceCm=10 radiusCm=225", "distanceCm=300 radiusCm=225")
        rows = {row["row"]: row for row in VERIFY.verify(log, s7_case="dodge-out")}
        self.assertEqual(rows["X26-S7a"]["status"], "PASS")
        self.assertEqual(rows["X26-S7-dodge-out"]["status"], "FAIL")

    def test_s7_dodge_out_damage_free_miss_passes(self):
        log = good_log().replace("inside=1", "inside=0").replace("distanceCm=10 radiusCm=225", "distanceCm=300 radiusCm=225")
        log = log.replace("[FrameworkProof] area_effect_damage instance=2 outcome=Accepted hpApplied=35 healthBefore=800 healthAfter=765\n", "")
        log = log.replace("[FrameworkProof] area_effect_snare state=Started instance=2 scale=0.55 seconds=2.5 baseSpeed=600\n", "")
        log = log.replace("[FrameworkProof] area_effect_snare state=Ended restored=1\n", "")
        rows = {row["row"]: row for row in VERIFY.verify(log, s7_case="dodge-out")}
        self.assertEqual(rows["X26-S7a"]["status"], "PASS")
        self.assertEqual(rows["X26-S7-dodge-out"]["status"], "PASS")

    def test_s8_wrong_tick_count_fails(self):
        log = good_log().replace("tick=5 cardTime=1.267", "tick=5 cardTime=1.267")
        log = log.replace("[FrameworkProof] channel state=Ended instance=3 ticks=5", "[FrameworkProof] channel state=Ended instance=3 ticks=4")
        rows = {row["row"]: row for row in VERIFY.verify(log)}
        self.assertEqual(rows["X26-S8a"]["status"], "FAIL")

    def test_s8_cone_escape_requires_damage_free_out_of_cone_misses(self):
        log = good_log().replace(
            "tick=2 cardTime=0.667 rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4",
            "tick=2 cardTime=0.667 rangeCm=400 dot=0.2 inCone=0 outcome=Miss hpApplied=0 bossHealed=0")
        log = log.replace(
            "tick=3 cardTime=0.867 rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4",
            "tick=3 cardTime=0.867 rangeCm=400 dot=0.2 inCone=0 outcome=Miss hpApplied=0 bossHealed=0")
        log = log.replace(
            "tick=4 cardTime=1.067 rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4",
            "tick=4 cardTime=1.067 rangeCm=400 dot=0.2 inCone=0 outcome=Miss hpApplied=0 bossHealed=0")
        log = log.replace(
            "tick=5 cardTime=1.267 rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4",
            "tick=5 cardTime=1.267 rangeCm=400 dot=0.2 inCone=0 outcome=Miss hpApplied=0 bossHealed=0")
        rows = {row["row"]: row for row in VERIFY.verify(log, s8_case="cone-escape")}
        self.assertEqual(rows["X26-S8-cone-escape"]["status"], "PASS")

    def test_s8_cone_miss_cannot_damage_or_heal_and_inside_heals_obey_cap(self):
        escaped = good_log().replace(
            "tick=2 cardTime=0.667 rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4",
            "tick=2 cardTime=0.667 rangeCm=400 dot=0.2 inCone=0 outcome=Miss hpApplied=8 bossHealed=0")
        escaped = escaped.replace(
            "tick=3 cardTime=0.867 rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4",
            "tick=3 cardTime=0.867 rangeCm=400 dot=0.2 inCone=0 outcome=Miss hpApplied=0 bossHealed=0")
        escaped = escaped.replace(
            "tick=4 cardTime=1.067 rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4",
            "tick=4 cardTime=1.067 rangeCm=400 dot=0.2 inCone=0 outcome=Miss hpApplied=0 bossHealed=0")
        escaped = escaped.replace(
            "tick=5 cardTime=1.267 rangeCm=400 dot=1 inCone=1 outcome=Accepted hpApplied=8 bossHealed=4",
            "tick=5 cardTime=1.267 rangeCm=400 dot=0.2 inCone=0 outcome=Miss hpApplied=0 bossHealed=0")
        rows = {row["row"]: row for row in VERIFY.verify(escaped, s8_case="cone-escape")}
        self.assertEqual(rows["X26-S8-cone-escape"]["status"], "FAIL")
        over_heal = good_log().replace("bossHealed=4", "bossHealed=4.1", 1)
        rows = {row["row"]: row for row in VERIFY.verify(over_heal)}
        self.assertEqual(rows["X26-S8b"]["status"], "FAIL")

    def test_cli_emits_machine_readable_row_receipt(self):
        import json
        import tempfile
        from contextlib import redirect_stdout
        from io import StringIO

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "synthetic.log"
            receipt = root / "receipt.json"
            log.write_text(good_log(), encoding="utf-8")
            with redirect_stdout(StringIO()):
                exit_code = VERIFY.main([str(log), "--receipt", str(receipt)])
            payload = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["result"], "PASS")
        self.assertEqual(len(payload["rows"]), 7)


if __name__ == "__main__":
    unittest.main()

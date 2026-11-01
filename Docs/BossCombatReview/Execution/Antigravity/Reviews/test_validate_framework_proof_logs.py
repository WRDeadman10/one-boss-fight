#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
test_validate_framework_proof_logs.py

Automated test suite verifying the FrameworkProof Log Validator:
1. Pure LF line endings (no CR).
2. Schema registration: verifies all 65 formal tokens are defined and compile.
3. Unit tests: asserts validation of synthetic valid lines across key categories.
4. 65-Token Mutation Test: extracts one real line per token from committed/candidate logs, mutates a key, and proves 65/65 fail validation.
5. Semantic checks tests: tests detection of out-of-order attacks, duplicate gates, reused instances, backward timestamps, and seq monotonicity.
6. Full repository sweep: scans all tracked log files and asserts 0 syntax failures across >60,000 lines, and verifies the 17 known duplicate attack findings.
"""

import unittest
import re
from pathlib import Path
import tempfile

import sys
REPO_ROOT = Path(__file__).resolve().parents[5]
REVIEWS_DIR = REPO_ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
sys.path.append(str(REVIEWS_DIR))

import validate_framework_proof_logs as validator

class TestValidateFrameworkProofLogs(unittest.TestCase):

    def test_file_exists_and_pure_lf(self):
        val_path = REVIEWS_DIR / "validate_framework_proof_logs.py"
        self.assertTrue(val_path.exists(), "validate_framework_proof_logs.py does not exist")
        raw = val_path.read_bytes()
        self.assertNotIn(b"\r", raw, "validate_framework_proof_logs.py contains CR! Must be pure LF.")

    def test_all_65_tokens_registered(self):
        self.assertEqual(len(validator.SCHEMAS), 94, f"Expected 94 schemas, got {len(validator.SCHEMAS)}")
        for tok, pat in validator.SCHEMAS.items():
            compiled = validator.COMPILED_SCHEMAS.get(tok)
            self.assertIsNotNone(compiled, f"Token {tok} missing in COMPILED_SCHEMAS")
            self.assertEqual(compiled.pattern, pat)

    def test_synthetic_valid_lines(self):
        valid_samples = [
            # Decision
            "[2026.10.30-13.52.25:120][352]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=Move_Sevarog_HeavySlam_F7 score=0.939261 range=129.533 phase=Phase_1",
            "[FrameworkProof] decision attack=1 chosen=Move_Sevarog_SwingSlow_F5 score=0.803979 range=169.602",
            # Walk
            "[FrameworkProof] walk start=X=500.000 Y=0.000 Z=167.150 end=X=129.533 Y=0.000 Z=167.150 distanceCm=370.467 rangeCm=129.533 bandMin=110 bandMax=140 capsule=X=129.533 Y=0.000 Z=167.150 mesh=X=129.533 Y=0.000 Z=2.150",
            # Reposition Turn End (BOSS-MOV-003)
            "[FrameworkProof] reposition_turn_end flips=0 latchDir=-1 seconds=0.716667",
            "[FrameworkProof] hyperarmor_absorbed card=Move_Sevarog_HeavySlam_F7 postureKept=100 amountSkipped=60",
            "[FrameworkProof] reposition_turn_end flips=15 latchDir=1 seconds=1.48333",
            # Sweep
            "[FrameworkProof] sweep instance=1 window=Window_HeavySlam_Terminal from=0.475 to=0.482357 tipDistanceCm=24.0699 substeps=1 clamped=0 baked=1",
            "[FrameworkProof] sweep instance=1 window=Window_SwingSlow_Primary from=0.35 to=0.350704 tipDistanceCm=0.654927 substeps=1 clamped=0",
            # Bystander & Sweep Filter (BOSS-HIT-005)
            "[FrameworkProof] bystander_spawned ok=1 name=Character_0 x=0 y=-60 z=98.15",
            "[FrameworkProof] bystander_spawned ok=0 name=None x=0 y=0 z=0",
            "[FrameworkProof] sweep_filter instance=1 window=Window_SwingSlow_Primary ignoredPawns=1 first=Character_0 targetContact=1 selfHits=0",
            "[FrameworkProof] sweep_filter instance=1 window=Window_SwingSlow_Primary ignoredPawns=1 first= targetContact=1 selfHits=0",
            # Target Faults & Validity (BOSS-AWR-001)
            "[FrameworkProof] target_fault_injected kind=Kill",
            "[FrameworkProof] target_fault_injected kind=Destroy",
            "[FrameworkProof] target_health_mismatch valid=0 actual=0 expected=800 generation=1 reason=Dead",
            "[FrameworkProof] target_health_mismatch valid=0 actual=0 expected=800 generation=1 reason=OffArena",
            "[FrameworkProof] target_health_mismatch valid=0 actual=0 expected=800 generation=1",
            # Phase Supersedes Stagger & Posture Held (BOSS-EXE-005 & F8)
            "[FrameworkProof] stagger_superseded reason=PhaseTransition health=240 max=500 fraction=0.48",
            "[FrameworkProof] posture_held reason=StaggerActive posture=0",
            # Combo gate
            "[FrameworkProof] combo_gate gate=1 node=A outcome=Hit range=128.625 yaw=0 result=Continue next=B reason=",
            "[FrameworkProof] combo_gate gate=1 node=A outcome=Whiff range=170.71 yaw=158.386 result=Recover next=None reason=Combo.DefaultRecovery",
            # Combo duplicate hook
            "[FrameworkProof] combo_gate_duplicate gate=1 result=Ignored reason=Combo.GateConsumed stateUnchanged=1",
            # Invariant
            "[FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35",
            "[FrameworkProof] invariant targetHPBefore=800 targetHPAfter=800 damageAPIInvocationsByThisExecutor=0",
            # Heading Commit (BOSS-ANM-004 & BOSS-AWR-002)
            "[FrameworkProof] heading_commit instance=1 yaw=174.456 turnedDegrees=5.54402 maxRateDegPerSec=18.4801 capDegPerSec=90",
            "[FrameworkProof] heading_commit instance=1 yaw=174.456 turnedDegrees=5.54402 maxRateDegPerSec=18.4801 capDegPerSec=90 decisionRangeCm=154.573 liveRangeCm=184.1",
            "[FrameworkProof] heading_commit instance=1 yaw=174.456 turnedDegrees=5.54402 maxRateDegPerSec=18.4801 capDegPerSec=90 decisionRangeCm=154.573 liveRangeCm=184.1 decisionYawDeg=0 liveYawDeg=-27.3566",
            # Watchdog & Montage Suppression (BOSS-EXE-007 & BOSS-ANM-007)
            "[FrameworkProof] montage_end_suppressed instance=1 position=0.306394",
            "[FrameworkProof] watchdog_timeout instance=1 elapsedSeconds=2.15051 timeoutSeconds=2.15 recoveryEndSeconds=1.65 playRate=1",
            "[FrameworkProof] watchdog_recovered attacksDone=0",
            # Result
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=2 attacks=3",
            "[FrameworkProof] RESULT outcome=CompletedWithDamage acceptedHits=1",
            "[FrameworkProof] RESULT outcome=CompletedTelemetryOnly",
            # Encounter reset
            "[FrameworkProof] encounter_reset generation=2 oldState=Dead executorRearmed=1 bossHealth=250 targetHealth=800",
            "[FrameworkProof] encounter_reset refused generation=2 reason=Framework.Fixture.RestartState",
            # Line of Sight & Memory (BOSS-AWR-007)
            "[FrameworkProof] los_lost lastKnownX=0 lastKnownY=0 blocker=StaticMeshActor_1",
            "[FrameworkProof] los_search_start x=0 y=0",
            "[FrameworkProof] los_regained lostForSeconds=0.916667",
            "[FrameworkProof] los_resume",
            "[FrameworkProof] los_search_timeout seconds=3",
            # Dodge Histogram & Adaptation (BOSS-AWR-008)
            "[FrameworkProof] player_dodges_scheduled count=2",
            "[FrameworkProof] player_dodge_started n=1 offset=0.3 direction=Back ok=1",
            "[FrameworkProof] dodge_observed n=1 direction=Back speedCm=900 back=1 depth=1",
            "[FrameworkProof] player_activity from=None to=Flask attackKind=Unknown",
            "[FrameworkProof] player_swing from=Unknown to=Strong heavy=1",
            "[FrameworkProof] greed_pattern state=Greedy source=Flask seq=2",
            "[FrameworkProof] punish_check card=Move_Sevarog_SwingSlow_F7 recoverySeconds=1.1583 lightStartupSeconds=0.350337 heavyStartupSeconds=0.502704 travelSeconds=0.0833333 lightMarginSeconds=0.72463 heavyMarginSeconds=0.572263 requiredSeconds=0.3 heavyFinisher=0 ok=1",
            "[FrameworkProof] dodge_pattern state=BackDodging back=2 depth=2 threshold=2 seq=2",
            # Grab Fail-Safe (BOSS-HIT-012)
            "[FrameworkProof] grab_catch instance=1 window=Window_HeavySlam_Terminal socket=hand_l releaseAt=1.1 modeBefore=MOVE_Walking modeHeld=MOVE_None attached=1",
            "[FrameworkProof] grab_damage instance=1 key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=55",
            "[FrameworkProof] grab_release instance=1 reason=Released interrupted=0 attached=0 mode=MOVE_Walking floorFound=1 floorZ=-2.84217e-14 feetZ=0.0348507 gapCm=0.0348507",
            # Bounded Motion Warping (BOSS-ANM-006)
            "[FrameworkProof] warp_step instance=1 from=0.4 to=0.4 distCm=128.467 neededCm=48.4667 stepCm=4.33434e-05 movedCm=4.33434e-05 budgetCm=150 neededDeg=0 stepDeg=0 turnedDeg=0 budgetDeg=45",
            "[FrameworkProof] warp_step instance=1 from=0.45 to=0.466667 distCm=475.98 neededCm=370.98 stepCm=0 actualCm=0 movedCm=150 budgetCm=150 neededDeg=-34.6418 stepDeg=-6.93114 turnedDeg=27.7246 budgetDeg=45",
            "[FrameworkProof] warp_summary instance=1 movedCm=150 maxDistanceCm=150 turnedDeg=45 maxAngleDeg=45",
        ]
        for line in valid_samples:
            ok, tok, payload, err = validator.validate_line(line)
            self.assertTrue(ok, f"Expected line to be valid, got error: {err}\nLine: {line}")
            self.assertIsNotNone(tok)

    def test_94_token_mutation_suite(self):
        """Extract one real line per token from committed/candidate logs, break one key, and prove 94/94 fail."""
        import subprocess
        res = subprocess.run(["git", "ls-files", "Docs/*.log"], cwd=REPO_ROOT, capture_output=True, text=True)
        files = [REPO_ROOT / f for f in res.stdout.splitlines() if f.strip()]
        for candidate_log in [
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_HIT005/byst60/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_AWR001/kill/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_AWR002/pie_shift/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_EXE007/pie_suppress/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_QA003B/f8_run1/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_EXE004/pie_stale/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_MOV005/pie_leash3/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_EXE005/pie_supersede/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_MOV003/pie_latch_on/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_DEF004/pie_armor/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_PAC002/pie_tempo/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_MOV002/pie_biased_v2/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_PHS005/pie_kite/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_SEL009/pie_flask/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_AWR007/pie_hide/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_AWR007/pie_hide_no_regain_target_x128/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_AWR008/pie_dodge/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_HIT011/pie_ring_hit/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_HIT012/pie_grab_release/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_ANM006/pie_warp_clamped/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_AWR006/pie_heavy/editor_raw.log",
            REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_PAC003/pie_pass/editor_raw.log",
        ]:
            if candidate_log.exists() and candidate_log not in files:
                files.append(candidate_log)

        real_lines = {}
        for fp in files:
            try:
                content = fp.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for line in content.splitlines():
                if "[FrameworkProof]" in line:
                    m = validator.LINE_RE.search(line)
                    if m:
                        tok = m.group(1)
                        if tok not in real_lines and tok in validator.SCHEMAS:
                            real_lines[tok] = line
                if len(real_lines) == 94:
                    break
            if len(real_lines) == 94:
                break

        self.assertEqual(len(real_lines), 94, f"Expected 94 real line samples, found {len(real_lines)}")

        for tok, line in real_lines.items():
            # First verify the real line passes
            ok, t, p, err = validator.validate_line(line)
            self.assertTrue(ok, f"Real line for {tok} failed prior to mutation: {line}")

            # Mutate: corrupt the first key by appending 'z'
            parts = line.split(f"[FrameworkProof] {tok}")
            prefix = parts[0] + f"[FrameworkProof] {tok}"
            payload = parts[1]
            if "=" in payload:
                mutated_payload = re.sub(r"\b([A-Za-z0-9_]+)=", r"\1z=", payload, count=1)
            else:
                mutated_payload = " corrupted_payload " + payload
            mutated_line = prefix + mutated_payload

            # Assert mutation is caught
            m_ok, m_t, m_p, m_err = validator.validate_line(mutated_line)
            self.assertFalse(m_ok, f"Token {tok} passed unexpectedly after mutation!\nMutated line: {mutated_line}")

    def test_semantic_checks(self):
        """Test detection of semantic ordering violations."""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as tf:
            tf.write("""[2026.10.30-10.00.00:000][1]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.9 range=100
[2026.10.30-09.59.59:000][2]LogTemp: Display: [FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=M1 slot=FullBody rate=1 label=F5
[2026.10.30-10.00.02:000][3]LogTemp: Display: [FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=M2 slot=FullBody rate=1 label=F5
[2026.10.30-10.00.03:000][4]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveB score=0.8 range=100
[2026.10.30-10.00.04:000][5]LogTemp: Display: [FrameworkProof] combo_gate gate=1 node=A outcome=Hit range=100 yaw=0 result=Continue next=B reason=
[2026.10.30-10.00.05:000][6]LogTemp: Display: [FrameworkProof] combo_gate gate=1 node=A outcome=Hit range=100 yaw=0 result=Continue next=B reason=
""")
            tf_path = Path(tf.name)

        try:
            res = validator.validate_log_file(tf_path)
            kinds = [v["kind"] for v in res["semantic_violations"]]
            self.assertIn("TIMESTAMP_BACKWARDS", kinds)
            self.assertIn("REUSED_INSTANCE_ID", kinds)
            self.assertIn("DUPLICATE_ATTACK_ID", kinds)
            self.assertIn("DUPLICATE_GATE_ID", kinds)
        finally:
            tf_path.unlink()

    def test_full_repository_committed_logs_sweep(self):
        """Scans all tracked logs, asserts 0 syntax errors, and asserts 17 known semantic findings."""
        import subprocess
        res = subprocess.run(["git", "ls-files", "Docs/*.log"], cwd=REPO_ROOT, capture_output=True, text=True)
        files = [REPO_ROOT / f for f in res.stdout.splitlines() if f.strip()]
        self.assertGreater(len(files), 600, f"Expected >600 tracked log files, found {len(files)}")

        total_lines = 0
        total_syntax_failures = 0
        total_semantic_violations = 0
        all_semantic = []

        for fp in files:
            res = validator.validate_log_file(fp)
            total_lines += res["framework_proof_lines"]
            total_syntax_failures += len(res["syntax_failures"])
            total_semantic_violations += len(res["semantic_violations"])
            all_semantic.extend(res["semantic_violations"])

        self.assertGreaterEqual(total_lines, 60000, f"Expected >=60,000 telemetry lines, found {total_lines}")
        self.assertEqual(total_syntax_failures, 0, f"Expected 0 syntax failures across repository, found {total_syntax_failures}")
        
        # Verify the 17 known duplicate attack findings from F8 mid-attack stagger aborts
        self.assertEqual(total_semantic_violations, 17, f"Expected 17 semantic findings, found {total_semantic_violations}")
        for v in all_semantic:
            self.assertEqual(v["kind"], "DUPLICATE_ATTACK_ID")

    def test_decision_seq_semantics(self):
        """Test seq= validation rules introduced in v3.0."""
        # 1. Valid seq matching between traces and decision, with repeated attack=1 resolved by distinct seq
        valid_log = """[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] candidate attack=1 card=MoveA score=0.7 seq=1
[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] refusal attack=1 card=MoveB reason=TooFar seq=1
[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.7 range=120 phase=Phase_1 seq=1
[2026.10.31-21.40.25:100][960]LogTemp: Display: [FrameworkProof] candidate attack=1 card=MoveC score=0.8 seq=2
[2026.10.31-21.40.25:100][960]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveC score=0.8 range=120 phase=Phase_2 seq=2
"""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as tf:
            tf.write(valid_log)
            tf_path = Path(tf.name)
        try:
            res = validator.validate_log_file(tf_path)
            self.assertEqual(len(res["syntax_failures"]), 0)
            self.assertEqual(len(res["semantic_violations"]), 0, f"Expected 0 violations, got {res['semantic_violations']}")
        finally:
            tf_path.unlink()

        # 2. Trace mismatch: candidate seq=2, decision seq=1
        mismatch_log = """[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] candidate attack=1 card=MoveA score=0.7 seq=2
[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.7 range=120 seq=1
"""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as tf:
            tf.write(mismatch_log)
            tf_path = Path(tf.name)
        try:
            res = validator.validate_log_file(tf_path)
            kinds = [v["kind"] for v in res["semantic_violations"]]
            self.assertIn("TRACE_DECISION_SEQ_MISMATCH", kinds)
        finally:
            tf_path.unlink()

        # 3. Duplicate decision seq
        dup_seq_log = """[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.7 range=120 seq=1
[2026.10.31-21.40.25:100][960]LogTemp: Display: [FrameworkProof] decision attack=2 chosen=MoveB score=0.8 range=120 seq=1
"""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as tf:
            tf.write(dup_seq_log)
            tf_path = Path(tf.name)
        try:
            res = validator.validate_log_file(tf_path)
            kinds = [v["kind"] for v in res["semantic_violations"]]
            self.assertIn("DUPLICATE_DECISION_SEQ", kinds)
        finally:
            tf_path.unlink()

        # 4. Non-increasing decision seq
        non_inc_seq_log = """[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.7 range=120 seq=5
[2026.10.31-21.40.25:100][960]LogTemp: Display: [FrameworkProof] decision attack=2 chosen=MoveB score=0.8 range=120 seq=4
"""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as tf:
            tf.write(non_inc_seq_log)
            tf_path = Path(tf.name)
        try:
            res = validator.validate_log_file(tf_path)
            kinds = [v["kind"] for v in res["semantic_violations"]]
            self.assertIn("NON_INCREASING_DECISION_SEQ", kinds)
        finally:
            tf_path.unlink()

        # 5. Intervening unselected cycle then trace mismatch: seq=1 (unselected), seq=2 candidate, seq=3 decision
        unselected_then_mismatch_log = """[2026.10.31-21.40.20:100][900]LogTemp: Display: [FrameworkProof] refusal attack=1 card=MoveA reason=MoveModel.Cone seq=1
[2026.10.31-21.40.20:100][900]LogTemp: Display: [FrameworkProof] refusal attack=1 card=MoveB reason=MoveModel.Cone seq=1
[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] candidate attack=1 card=MoveA score=0.7 seq=2
[2026.10.31-21.40.25:100][960]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.7 range=120 seq=3
"""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as tf:
            tf.write(unselected_then_mismatch_log)
            tf_path = Path(tf.name)
        try:
            res = validator.validate_log_file(tf_path)
            kinds = [v["kind"] for v in res["semantic_violations"]]
            self.assertIn("TRACE_DECISION_SEQ_MISMATCH", kinds)
        finally:
            tf_path.unlink()

        # 6. Valid unselected cycle (seq=1) followed by valid decision cycle (seq=2)
        unselected_then_valid_log = """[2026.10.31-21.40.20:100][900]LogTemp: Display: [FrameworkProof] refusal attack=1 card=MoveA reason=MoveModel.Cone seq=1
[2026.10.31-21.40.20:100][900]LogTemp: Display: [FrameworkProof] refusal attack=1 card=MoveB reason=MoveModel.Cone seq=1
[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] candidate attack=1 card=MoveA score=0.7 seq=2
[2026.10.31-21.40.23:255][950]LogTemp: Display: [FrameworkProof] decision attack=1 chosen=MoveA score=0.7 range=120 seq=2
"""
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False, suffix=".log") as tf:
            tf.write(unselected_then_valid_log)
            tf_path = Path(tf.name)
        try:
            res = validator.validate_log_file(tf_path)
            self.assertEqual(len(res["syntax_failures"]), 0)
            self.assertEqual(len(res["semantic_violations"]), 0)
        finally:
            tf_path.unlink()

    def test_b_qa002_evidence_log(self):
        """Validate Claude/B_QA002/pie_f8/editor_raw.log passes with 0 syntax and 0 semantic violations."""
        log_path = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_QA002/pie_f8/editor_raw.log"
        self.assertTrue(log_path.exists(), f"Log file not found: {log_path}")
        res = validator.validate_log_file(log_path)
        self.assertEqual(len(res["syntax_failures"]), 0, f"Expected 0 syntax failures, got {res['syntax_failures']}")
        self.assertEqual(len(res["semantic_violations"]), 0, f"Expected 0 semantic violations, got {res['semantic_violations']}")
        self.assertEqual(res["framework_proof_lines"], 367)

    def test_b_hit005_evidence_log(self):
        """Validate Claude/B_HIT005/byst60/editor_raw.log passes with 0 syntax and 0 semantic violations."""
        log_path = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_HIT005/byst60/editor_raw.log"
        self.assertTrue(log_path.exists(), f"Log file not found: {log_path}")
        res = validator.validate_log_file(log_path)
        self.assertEqual(len(res["syntax_failures"]), 0, f"Expected 0 syntax failures, got {res['syntax_failures']}")
        self.assertEqual(len(res["semantic_violations"]), 0, f"Expected 0 semantic violations, got {res['semantic_violations']}")
        self.assertEqual(res["framework_proof_lines"], 298)

    def test_b_awr001_evidence_logs(self):
        """Validate Claude/B_AWR001 logs (kill, offarena, destroy, control) pass with 0 syntax failures."""
        awr_dir = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_AWR001"
        for sub in ("kill", "offarena", "destroy", "control"):
            log_path = awr_dir / sub / "editor_raw.log"
            self.assertTrue(log_path.exists(), f"Log missing: {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")

    def test_b_exe005_evidence_log(self):
        """Validate Claude/B_EXE005/pie_supersede/editor_raw.log passes with 0 syntax and 0 semantic violations."""
        log_path = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_EXE005/pie_supersede/editor_raw.log"
        self.assertTrue(log_path.exists(), f"Log missing: {log_path}")
        res = validator.validate_log_file(log_path)
        self.assertEqual(len(res["syntax_failures"]), 0, f"Expected 0 syntax failures, got {res['syntax_failures']}")
        self.assertEqual(len(res["semantic_violations"]), 0, f"Expected 0 semantic violations, got {res['semantic_violations']}")
        self.assertEqual(res["framework_proof_lines"], 240)

    def test_b_pac002_evidence_logs(self):
        """B_PAC002 evidence logs parse with 0 syntax failures and 0 semantic violations."""
        for sub in ["content_run1", "pie_tempo"]:
            log_path = REPO_ROOT / f"Docs/BossCombatReview/Execution/Claude/B_PAC002/{sub}/editor_raw.log"
            self.assertTrue(log_path.exists(), f"Missing {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")

    def test_b_def004_evidence_logs(self):
        """B_DEF004 evidence logs parse with 0 syntax failures and 0 semantic violations."""
        for sub in ["content_run1", "pie_armor"]:
            log_path = REPO_ROOT / f"Docs/BossCombatReview/Execution/Claude/B_DEF004/{sub}/editor_raw.log"
            self.assertTrue(log_path.exists(), f"Missing {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")

    def test_b_mov003_evidence_logs(self):
        """Validate Claude/B_MOV003 logs (pie_latch_on, pie_latch_off_control) pass with 0 syntax/semantic violations."""
        mov_dir = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_MOV003"
        for sub, expected_lines in [("pie_latch_on", 494), ("pie_latch_off_control", 591)]:
            log_path = mov_dir / sub / "editor_raw.log"
            self.assertTrue(log_path.exists(), f"Log missing: {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")
            self.assertEqual(res["framework_proof_lines"], expected_lines)

    def test_b_mov002_evidence_logs(self):
        """B_MOV002 evidence logs parse with 0 syntax failures and 0 semantic violations."""
        mov_dir = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_MOV002"
        for sub, expected_lines in [("pie_biased_v2", 309), ("pie_control_bias0_v2", 254), ("pie_control_bias0", 254), ("pie_biased_NoCandidate_no_reposition", 14)]:
            log_path = mov_dir / sub / "editor_raw.log"
            self.assertTrue(log_path.exists(), f"Missing {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")
            self.assertEqual(res["framework_proof_lines"], expected_lines)

    def test_b_phs005_evidence_logs(self):
        """B_PHS005 evidence logs parse with 0 syntax failures and 0 semantic violations."""
        phs_dir = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_PHS005"
        for sub, expected_lines in [("pie_kite", 488)]:
            log_path = phs_dir / sub / "editor_raw.log"
            self.assertTrue(log_path.exists(), f"Missing {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")
            self.assertEqual(res["framework_proof_lines"], expected_lines)

    def test_b_hit012_evidence_logs(self):
        """B_HIT012 evidence logs parse with 0 syntax failures and 0 semantic violations."""
        hit_dir = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_HIT012"
        for sub, expected_lines in [("pie_grab_release", 128), ("pie_grab_release2", 128), ("pie_grab_stagger", 202), ("pie_grab_death", 86)]:
            log_path = hit_dir / sub / "editor_raw.log"
            self.assertTrue(log_path.exists(), f"Missing {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")
            self.assertEqual(res["framework_proof_lines"], expected_lines)

    def test_b_anm006_evidence_logs(self):
        """B_ANM006 evidence logs parse with 0 syntax failures and 0 semantic violations."""
        anm_dir = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_ANM006"
        for sub, expected_lines in [("pie_warp_room", 137), ("pie_warp_room2", 137), ("pie_warp_clamped", 137)]:
            log_path = anm_dir / sub / "editor_raw.log"
            self.assertTrue(log_path.exists(), f"Missing {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")
            self.assertEqual(res["framework_proof_lines"], expected_lines)

    def test_b_awr006_evidence_logs(self):
        """B_AWR006 evidence logs parse with 0 syntax failures and 0 semantic violations."""
        awr_dir = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_AWR006"
        for sub, expected_lines in [
            ("pie_base", 474),
            ("pie_flask", 490),
            ("pie_flask2", 490),
            ("pie_heavy", 492),
            ("pie_heavy2", 492),
            ("pie_light", 478),
        ]:
            log_path = awr_dir / sub / "editor_raw.log"
            self.assertTrue(log_path.exists(), f"Missing {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")
            self.assertEqual(res["framework_proof_lines"], expected_lines)

    def test_b_pac003_evidence_logs(self):
        """B_PAC003 evidence logs parse with 0 syntax failures and 0 semantic violations."""
        pac_dir = REPO_ROOT / "Docs/BossCombatReview/Execution/Claude/B_PAC003"
        for sub, expected_lines in [
            ("pie_pass", 476),
            ("pie_pass2", 476),
            ("pie_fail", 7),
        ]:
            log_path = pac_dir / sub / "editor_raw.log"
            self.assertTrue(log_path.exists(), f"Missing {log_path}")
            res = validator.validate_log_file(log_path)
            self.assertEqual(len(res["syntax_failures"]), 0, f"[{sub}] Expected 0 syntax failures, got {res['syntax_failures']}")
            self.assertEqual(len(res["semantic_violations"]), 0, f"[{sub}] Expected 0 semantic violations, got {res['semantic_violations']}")
            self.assertEqual(res["framework_proof_lines"], expected_lines)

    def test_warp_step_v1_and_v2_accepted(self):
        """Verify warp_step accepts both v1 (no actualCm) and v2 (with actualCm), but rejects missing other fields."""
        v1_line = "[FrameworkProof] warp_step instance=1 from=0.4 to=0.4 distCm=128.467 neededCm=48.4667 stepCm=4.33434e-05 movedCm=4.33434e-05 budgetCm=150 neededDeg=0 stepDeg=0 turnedDeg=0 budgetDeg=45"
        v2_line = "[FrameworkProof] warp_step instance=1 from=0.45 to=0.466667 distCm=475.98 neededCm=370.98 stepCm=0 actualCm=0 movedCm=150 budgetCm=150 neededDeg=-34.6418 stepDeg=-6.93114 turnedDeg=27.7246 budgetDeg=45"
        
        ok, tok, _, err = validator.validate_line(v1_line)
        self.assertTrue(ok, f"v1 warp_step line failed validation: {err}")
        self.assertEqual(tok, "warp_step")
        
        ok, tok, _, err = validator.validate_line(v2_line)
        self.assertTrue(ok, f"v2 warp_step line failed validation: {err}")
        self.assertEqual(tok, "warp_step")
        
        # Missing another required field (e.g. movedCm) must fail
        bad_line = "[FrameworkProof] warp_step instance=1 from=0.45 to=0.466667 distCm=475.98 neededCm=370.98 stepCm=0 actualCm=0 budgetCm=150 neededDeg=-34.6418 stepDeg=-6.93114 turnedDeg=27.7246 budgetDeg=45"
        ok, _, _, _ = validator.validate_line(bad_line)
        self.assertFalse(ok, "warp_step line missing movedCm was unexpectedly accepted!")

if __name__ == "__main__":
    unittest.main()

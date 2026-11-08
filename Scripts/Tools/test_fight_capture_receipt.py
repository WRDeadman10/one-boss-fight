"""Offline contracts for full-fight summary and provenance accounting."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from Scripts.Tools.fight_capture_receipt import parse_receipt, validate_parry_diagnostics
except ModuleNotFoundError:
    from fight_capture_receipt import parse_receipt, validate_parry_diagnostics


RUN = "smoke_01"
PROVENANCE = {"run": RUN, "build_id": "BUILD-TEST", "map": "L_SevarogArena",
              "route": "data", "tier2": True, "tool_sha256": "a" * 64}
SUMMARY = {"run": RUN, "fight_seconds": 12.0, "boss_dead": True, "reason": "boss dead",
           "action_counts": {"light": 1, "strong": 0, "backstep": 0, "air_light": 0,
                             "air_heavy": 0, "guard": 1, "parry_watch": 0,
                             "counter": 1, "parry_contact": 1},
           "player_refills": 1, "player_deaths": 0, "frames": 3,
           "boss_health_start": 1000.0, "boss_health_max_start": 2000.0, "boss_health_end": 0.0,
           "boss_ai_controller_start": "AIC_Boss", "boss_ai_controller_end": "AIC_Boss",
           "boss_driver_mutations": 0, "boss_health_writes_by_driver": 0,
           "boss_ai_writes_by_driver": 0, "successful_parries": 1}


def sample(provenance=PROVENANCE, summary=SUMMARY, extra=""):
    lines = [
        "[EncounterActivation] route=data",
        "[FullFight] RUN_PROVENANCE " + json.dumps(provenance, sort_keys=True),
        "[FullFight] ACTION light t=1.0 id=smoke_01:action:00001",
        "[FullFight] ACTION guard t=2.0 id=smoke_01:action:00002",
        "[FullFight] COUNTER t=3.0 id=smoke_01:action:00002",
        "[FullFight] PARRY_CONTACT instance=9 t=4.0 parried_delta=1 boss_montage=AM_Boss01_ParryRecoil",
        "[FullFight] PLAYER_REFILL count=1 t=5.0 hp_before=30 hp_after=100 boss_hp=900",
        "[FullFight] FRAME 0 g=1.0 marker=smoke_01:frame:00000 action=light action_id=smoke_01:action:00001",
        "[FullFight] FRAME 1 g=1.1 marker=smoke_01:frame:00001 action=guard action_id=smoke_01:action:00002",
        "[FullFight] FRAME 2 g=1.2 marker=smoke_01:frame:00002 action=guard action_id=smoke_01:action:00002",
        "[FullFight] FRAME_CONTEXT {\"run\":\"smoke_01\",\"frame_marker_id\":\"smoke_01:frame:00000\",\"action_id\":\"smoke_01:action:00001\",\"game_time_s\":1.0,\"camera_position\":[0,0,0],\"player_position\":[1,0,0],\"boss_position\":[2,0,0],\"player_in_camera_frame_estimate\":true,\"boss_in_camera_frame_estimate\":true,\"camera_inside_boss_component_bounds\":false,\"world_occlusion\":\"UNMEASURED\"}",
        "[FullFight] FRAME_CONTEXT {\"run\":\"smoke_01\",\"frame_marker_id\":\"smoke_01:frame:00001\",\"action_id\":\"smoke_01:action:00002\",\"game_time_s\":1.1,\"camera_position\":[0,0,0],\"player_position\":[1,0,0],\"boss_position\":[2,0,0],\"player_in_camera_frame_estimate\":true,\"boss_in_camera_frame_estimate\":true,\"camera_inside_boss_component_bounds\":\"UNKNOWN\",\"world_occlusion\":\"UNMEASURED\"}",
        "[FullFight] FRAME_CONTEXT {\"run\":\"smoke_01\",\"frame_marker_id\":\"smoke_01:frame:00002\",\"action_id\":\"smoke_01:action:00002\",\"game_time_s\":1.2,\"camera_position\":[0,0,0],\"player_position\":[1,0,0],\"boss_position\":[2,0,0],\"player_in_camera_frame_estimate\":true,\"boss_in_camera_frame_estimate\":false,\"camera_inside_boss_component_bounds\":true,\"world_occlusion\":\"UNMEASURED\"}",
        "[FullFight] BOSS_DEAD at 12.0 s",
        "[FullFight] RECEIPT_SUMMARY " + json.dumps(summary, sort_keys=True),
        "[FullFight] finished: boss dead",
    ]
    if extra:
        lines.insert(-2, extra)
    return "\n".join(lines)


class FightCaptureReceiptTests(unittest.TestCase):
    def test_valid_receipt_accounts_for_actions_contacts_refills_frames_and_death(self):
        receipt = parse_receipt(sample())
        self.assertEqual(receipt["run"], RUN)
        self.assertEqual(receipt["route_witness"], "data")
        self.assertEqual(receipt["player_refills"], 1)
        self.assertEqual(receipt["player_deaths"], 0)
        self.assertTrue(receipt["boss_dead"])
        self.assertEqual(len(receipt["actions"]["light"][0]["frames"]), 1)
        self.assertEqual(len(receipt["frame_context"]), 3)
        self.assertTrue(receipt["frame_context"][2]["camera_inside_boss_component_bounds"])

    def test_frame_context_must_be_unique_and_match_run_frame_action_and_time(self):
        source = sample().replace('[FullFight] FRAME_CONTEXT {"run":"smoke_01","frame_marker_id":"smoke_01:frame:00002","action_id":"smoke_01:action:00002","game_time_s":1.2,"camera_position":[0,0,0],"player_position":[1,0,0],"boss_position":[2,0,0],"player_in_camera_frame_estimate":true,"boss_in_camera_frame_estimate":false,"camera_inside_boss_component_bounds":true,"world_occlusion":"UNMEASURED"}', "")
        with self.assertRaisesRegex(ValueError, "missing FRAME_CONTEXT"):
            parse_receipt(source)
        context = '[FullFight] FRAME_CONTEXT {"run":"smoke_01","frame_marker_id":"smoke_01:frame:00002","action_id":"smoke_01:action:00002","game_time_s":1.2,"camera_position":[0,0,0],"player_position":[1,0,0],"boss_position":[2,0,0],"player_in_camera_frame_estimate":true,"boss_in_camera_frame_estimate":false,"camera_inside_boss_component_bounds":true,"world_occlusion":"UNMEASURED"}'
        with self.assertRaisesRegex(ValueError, "exactly one FRAME_CONTEXT"):
            parse_receipt(sample().replace("[FullFight] finished: boss dead", context + "\n[FullFight] finished: boss dead"))
        with self.assertRaisesRegex(ValueError, "does not match frame identity"):
            parse_receipt(sample().replace('"frame_marker_id":"smoke_01:frame:00002"', '"frame_marker_id":"other:frame:00002"'))
        with self.assertRaisesRegex(ValueError, "world_occlusion cannot claim clear"):
            parse_receipt(sample().replace('"world_occlusion":"UNMEASURED"', '"world_occlusion":"CLEAR"', 1))

    def test_parry_diag_transitions_and_timeout_slots_are_bounded(self):
        lines = [
            "[FullFight] PARRY_DIAG montage=GS_Attack04_Montage tracker_move=A1b tracker_instance=7 tracker_active=false tracker_position=0.4 sweep_active=false sweep_count=0",
            "[FullFight] PARRY_DIAG montage=Other tracker_move=A3 tracker_instance=8 tracker_active=true tracker_position=0.5 sweep_active=false sweep_count=0",
            "[FullFight] PARRY_WATCH_RESULT outcome=timeout_no_live_a4 slot=run:action:00001 seconds=3.00",
        ]
        self.assertEqual(len(validate_parry_diagnostics(lines)["transitions"]), 2)
        with self.assertRaisesRegex(ValueError, "duplicate montage transition"):
            validate_parry_diagnostics([lines[0], lines[0]] + lines[1:])
        with self.assertRaisesRegex(ValueError, "duplicate timeout slot"):
            validate_parry_diagnostics(lines + [lines[2]])

    def test_duplicate_summary_fails(self):
        with self.assertRaisesRegex(ValueError, "exactly one RECEIPT_SUMMARY"):
            parse_receipt(sample() + "\n" + "[FullFight] RECEIPT_SUMMARY " + json.dumps(SUMMARY))

    def test_missing_summary_fails(self):
        with self.assertRaisesRegex(ValueError, "exactly one RECEIPT_SUMMARY"):
            parse_receipt(sample().replace("[FullFight] RECEIPT_SUMMARY " + json.dumps(SUMMARY, sort_keys=True), ""))

    def test_action_counter_refill_frame_and_boss_death_totals_must_match(self):
        changed = dict(SUMMARY, action_counts={**SUMMARY["action_counts"], "light": 2})
        with self.assertRaisesRegex(ValueError, "action count mismatch"):
            parse_receipt(sample(summary=changed))
        changed = dict(SUMMARY, player_refills=2)
        with self.assertRaisesRegex(ValueError, "refill count mismatch"):
            parse_receipt(sample(summary=changed))
        changed = dict(SUMMARY, frames=4)
        with self.assertRaisesRegex(ValueError, "frame count mismatch"):
            parse_receipt(sample(summary=changed))
        changed = dict(SUMMARY, boss_dead=False)
        with self.assertRaisesRegex(ValueError, "boss-death summary contradicts marker"):
            parse_receipt(sample(summary=changed))

    def test_missing_action_total_and_bad_refill_readback_fail(self):
        counts = dict(SUMMARY["action_counts"])
        counts.pop("air_light")
        with self.assertRaisesRegex(ValueError, "missing action total for air_light"):
            parse_receipt(sample(summary=dict(SUMMARY, action_counts=counts)))
        with self.assertRaisesRegex(ValueError, "below-threshold increase"):
            parse_receipt(sample(extra="[FullFight] PLAYER_REFILL count=2 t=6.0 hp_before=60 hp_after=100 boss_hp=800",
                                 summary=dict(SUMMARY, player_refills=2)))

    def test_changed_or_unknown_boss_ai_controller_fails(self):
        changed = dict(SUMMARY, boss_ai_controller_end="None")
        with self.assertRaisesRegex(ValueError, "controller readback unknown"):
            parse_receipt(sample(summary=changed))
        changed = dict(SUMMARY, boss_ai_controller_end="DifferentAI")
        with self.assertRaisesRegex(ValueError, "controller changed"):
            parse_receipt(sample(summary=changed))

    def test_cli_emits_machine_readable_json(self):
        tool = Path(__file__).with_name("fight_capture_receipt.py")
        with tempfile.TemporaryDirectory() as root:
            log = Path(root) / "run.log"
            log.write_text(sample(), encoding="utf-8")
            result = subprocess.run([sys.executable, str(tool), "--log", str(log)],
                                    capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["build_id"], "BUILD-TEST")
        self.assertEqual(receipt["route_witness"], "data")

    def test_action_ids_must_link_to_same_run_frames(self):
        source = sample().replace("smoke_01:action:00001", "other_run:action:00001", 1)
        with self.assertRaisesRegex(ValueError, "action id belongs to another run"):
            parse_receipt(source)
        source = sample().replace("action_id=smoke_01:action:00001", "action_id=smoke_01:action:99999")
        with self.assertRaisesRegex(ValueError, "no matching action"):
            parse_receipt(source)

    def test_provenance_requires_build_map_tool_hash_and_matching_route_witness(self):
        with self.assertRaisesRegex(ValueError, "route witness"):
            parse_receipt(sample().replace("[EncounterActivation] route=data\n", ""))
        with self.assertRaisesRegex(ValueError, "build_id"):
            parse_receipt(sample(provenance=dict(PROVENANCE, build_id="UNKNOWN")))
        with self.assertRaisesRegex(ValueError, "route witness"):
            parse_receipt(sample(provenance=dict(PROVENANCE, route="legacy")))

    def test_absent_action_is_zero_not_inferred_from_frames(self):
        source = sample()
        summary = dict(SUMMARY, action_counts={"light": 1, "guard": 1, "counter": 1, "parry_contact": 1,
                                               "strong": 0, "backstep": 0, "air_light": 0,
                                               "air_heavy": 0, "parry_watch": 0})
        receipt = parse_receipt(source.replace("[FullFight] RECEIPT_SUMMARY " + json.dumps(SUMMARY, sort_keys=True),
                                "[FullFight] RECEIPT_SUMMARY " + json.dumps(summary, sort_keys=True)))
        self.assertEqual(receipt["action_counts"]["air_light"], 0)


if __name__ == "__main__":
    unittest.main()

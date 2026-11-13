"""Synthetic offline contracts for the BF-X05 receipt predicate checker."""
import hashlib
import unittest

from verify_bf_x05_selected_route import ReceiptError, ROWS, validate


def sample():
    sha = hashlib.sha256(b"definition bytes").hexdigest()
    evidence = {row: [{"log": "raw.log", "excerpt": "synthetic witness for " + row}] for row in ROWS}
    return {
        "schema_version": 1, "build_id": "BUILD-298", "map": "/Game/OneBossFight/Maps/L_SevarogArena",
        "evidence": evidence,
        "runs": {
            "default_off": {"build_id": "BUILD-298", "map": "/Game/OneBossFight/Maps/L_SevarogArena", "world": "PIE_0", "route_flag": False,
                "selected_route": "Pack", "pack_boss_count": 1, "framework_boss_count": 0, "framework_binding": False},
            "framework_opt_in": {"build_id": "BUILD-298", "map": "/Game/OneBossFight/Maps/L_SevarogArena", "world": "PIE_1", "route_flag": True,
                "selected_route": "Framework", "pack_boss_count": 0, "framework_boss_count": 1, "framework_binding": True,
                "definition_path": "/Game/OneBossFight/Data/DA_FrameworkDefinition", "definition_sha256": sha, "definition_hash_readback": sha,
                "deferred_selection": {"pack_isolated_before_spawn": True, "framework_spawn_before_selection": True,
                    "selector_flag": 1, "definition_path": "/Game/OneBossFight/Data/DA_FrameworkDefinition", "activation_result": "Activated"},
                "participants": {"boss": {"object_id": "Boss_17", "slot": "Boss", "generation": 7}, "player": {"object_id": "Player_02", "slot": "Player", "generation": 7}},
                "health_current": 500, "health_max": 1000, "hud_health_fraction": 0.5, "active": True, "phase": "Phase1", "hud_owner_object_id": "Boss_17",
                "terminal_callback_actor": "Boss_17", "terminal_callback_generation": 7, "completed": True, "victory_count": 1,
                "retry_configured_delay_seconds": 1.5, "retry_measured_delay_seconds": 1.52, "retry_visible": True,
                "reset": {"count": 1, "generation": 8, "prior_generation_callback_refused": True, "prior_generation_refusal": "GenerationMismatch"},
                "replacement_actor": {"object_id": "Boss_18", "callback_refused": True, "refusal": "ActorMismatch"}}
        }
    }


class BF05VerifierTests(unittest.TestCase):
    def test_complete_receipt_passes_but_does_not_claim_live_validation(self):
        result = validate(sample())
        self.assertEqual(result["result"], "PASS")
        self.assertFalse(result["live_run_verified"])
        self.assertEqual(len(result["rows"]), 9)

    def test_missing_source_excerpt_fails(self):
        value = sample()
        value["evidence"]["HUD-01"] = []
        with self.assertRaisesRegex(ReceiptError, "HUD-01 missing evidence"):
            validate(value)

    def test_cross_build_or_map_drift_fails(self):
        value = sample()
        value["runs"]["framework_opt_in"]["build_id"] = "BUILD-299"
        with self.assertRaisesRegex(ReceiptError, "build_id mismatch"):
            validate(value)

    def test_framework_route_requires_exclusive_framework_candidate(self):
        value = sample()
        value["runs"]["framework_opt_in"]["pack_boss_count"] = 1
        with self.assertRaisesRegex(ReceiptError, "exactly one framework boss"):
            validate(value)

    def test_boolean_is_not_accepted_as_numeric_candidate_count(self):
        value = sample()
        value["runs"]["framework_opt_in"]["framework_boss_count"] = True
        with self.assertRaisesRegex(ReceiptError, "exactly one framework boss"):
            validate(value)

    def test_definition_hash_must_match_readback(self):
        value = sample()
        value["runs"]["framework_opt_in"]["definition_hash_readback"] = "0" * 64
        with self.assertRaisesRegex(ReceiptError, "hash readback mismatch"):
            validate(value)

    def test_deferred_route_requires_pack_isolation_then_spawn_then_selection(self):
        value = sample()
        value["runs"]["framework_opt_in"]["deferred_selection"]["framework_spawn_before_selection"] = False
        with self.assertRaisesRegex(ReceiptError, "spawn before selection"):
            validate(value)

    def test_deferred_definition_must_match_selected_definition(self):
        value = sample()
        value["runs"]["framework_opt_in"]["deferred_selection"]["definition_path"] = "/Game/Other"
        with self.assertRaisesRegex(ReceiptError, "flag/definition mismatch"):
            validate(value)

    def test_hud_health_and_owner_are_bound_to_native_boss(self):
        value = sample()
        value["runs"]["framework_opt_in"]["hud_health_fraction"] = 0.8
        with self.assertRaisesRegex(ReceiptError, "disagrees with native health"):
            validate(value)

    def test_terminal_generation_must_match_selected_binding(self):
        value = sample()
        value["runs"]["framework_opt_in"]["terminal_callback_generation"] = 6
        with self.assertRaisesRegex(ReceiptError, "terminal callback actor/generation mismatch"):
            validate(value)

    def test_retry_timing_has_bounded_match(self):
        value = sample()
        value["runs"]["framework_opt_in"]["retry_measured_delay_seconds"] = 2.0
        with self.assertRaisesRegex(ReceiptError, "differs by more than 0.05s"):
            validate(value)

    def test_reset_must_advance_and_reject_old_generation(self):
        value = sample()
        value["runs"]["framework_opt_in"]["reset"]["generation"] = 7
        with self.assertRaisesRegex(ReceiptError, "generation advancement"):
            validate(value)

    def test_replacement_actor_callback_must_be_refused(self):
        value = sample()
        value["runs"]["framework_opt_in"]["replacement_actor"]["callback_refused"] = False
        with self.assertRaisesRegex(ReceiptError, "replacement callback refusal missing"):
            validate(value)


if __name__ == "__main__":
    unittest.main()

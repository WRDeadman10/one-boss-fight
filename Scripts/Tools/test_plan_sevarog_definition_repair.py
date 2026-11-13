"""BK-94 (C, implementer; X-2002): synthetic tests for the proposal-only repair planner.

No Unreal, no asset reads or writes, no locks: every input is an in-memory dictionary. Values are synthetic test values,
not project values (no owner answer to X-1991 exists).
"""
import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("plan_sevarog_definition_repair", HERE / "plan_sevarog_definition_repair.py")
P = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)

BEFORE = "a" * 64
AFTER = "b" * 64
SYNTHETIC = {"Stats.MaxHealth": 1234.0, "Stats.MaxPosture": 77.0, "Stats.PostureRegenDelay": 2.5, "Stats.PostureRegenRate": 9.0,
             "Phases[Phase_1].PhaseId": "Phase_1", "Phases[Phase_1].EntryHealthFraction": 0.45,
             "Phases[Phase_1].SpeedMultiplier": 1.2, "Phases[Phase_1].RateMultiplier": 0.9, "Phases[Phase_1].AttackMultiplier": 1.3}
SOURCE = {"sender": "Owner", "message_id": "O-77", "path": "Documentation/TEAM_MAILBOX.md", "reply_sha256": "c" * 64}


def envelope_result(values=None, **change):
    values = SYNTHETIC if values is None else values
    result = {"valid": True, "errors": [], "rejected": [], "unresolved": [],
              "approved_for_review": [{"field_path": f, "value": v, "decision": "APPROVE_VALUE"} for f, v in values.items()]}
    result.update(change)
    return result


def snapshot(**change):
    snap = {"asset_path": P.ASSET_PATH, "exists": True, "file_sha256": BEFORE,
            "stats": {"max_health": 0.0, "max_posture": 0.0, "posture_regen_delay": 0.0, "posture_regen_rate": 0.0},
            "phases": [{"phase_id": "Phase_2", "entry_health_fraction": 0.5, "speed_multiplier": 1.0, "rate_multiplier": 1.0, "attack_multiplier": 1.0},
                       {"phase_id": "Phase_1", "entry_health_fraction": 0.0, "speed_multiplier": 1.0, "rate_multiplier": 1.0, "attack_multiplier": 1.0}],
            "fields": []}
    snap.update(change)
    return snap


def context(**change):
    ctx = {"operation": "in_place_update", "mode": "write", "explicit_write": True,
           "locks": {"root_held": True, "execution_held": True, "owner_token": "0123456789abcdef0123456789abcdef"},
           "backup": {"path": "Docs/BossCombatReview/Execution/Claude/backup/DA_Boss_Sevarog_Draft.before.uasset", "sha256": BEFORE}}
    ctx.update(change)
    return ctx


def saved_after(plan, **change):
    after = snapshot(file_sha256=AFTER)
    for write in plan["writes"]:
        group, prop = write["target"].split(".", 1)
        if group == "stats":
            after["stats"][prop] = write["to"]
        else:
            phase = next((p for p in after["phases"] if p.get("phase_id") == P.PHASE_ID), None)
            if phase is None:
                phase = {"phase_id": P.PHASE_ID}
                after["phases"].append(phase)
            phase[prop] = write["to"]
    after["fields"] = copy.deepcopy(plan["field_records"])
    after.update(change)
    return after


class PlannerTests(unittest.TestCase):
    def refused(self, needle, env=None, snap=None, ctx=None, owner_source=SOURCE):
        plan = P.plan_repair(envelope_result() if env is None else env, snapshot() if snap is None else snap,
                             context() if ctx is None else ctx, owner_source)
        self.assertFalse(plan["accepted"])
        self.assertEqual((plan["steps"], plan["writes"]), ([], []), "a refused plan carries no steps or writes")
        self.assertTrue(any(needle in e for e in plan["errors"]), (needle, plan["errors"]))

    # --- accepted plans ---
    def test_complete_approval_gives_an_in_place_write_plan(self):
        plan = P.plan_repair(envelope_result(), snapshot(), context(), SOURCE)
        self.assertTrue(plan["accepted"], plan["errors"])
        self.assertEqual(plan["steps"], list(P.STEPS_WRITE))
        self.assertEqual(plan["steps"][-1], "release_locks")
        self.assertEqual(len(plan["writes"]), 9)
        phase_id_write = next(w for w in plan["writes"] if w["field_path"] == "Phases[Phase_1].PhaseId")
        self.assertEqual((phase_id_write["target"], phase_id_write["to"]), ("phases[Phase_1].phase_id", "Phase_1"))
        phase_id_record = next(r for r in plan["field_records"] if r["field_path"] == "Phases[Phase_1].PhaseId")
        self.assertEqual((phase_id_record["type"], phase_id_record["value"]), ("name", "Phase_1"))
        self.assertTrue(all(w.get("row_action", "update_existing_row") == "update_existing_row" for w in plan["writes"]))
        self.assertEqual(plan["untouched_phase_rows"], ["Phase_2"])
        self.assertEqual({r["source_site"] for r in plan["field_records"]}, {"O-77"})

    def test_missing_phase_row_is_appended_not_recreated(self):
        snap = snapshot(phases=[snapshot()["phases"][0]])
        plan = P.plan_repair(envelope_result(), snap, context(), SOURCE)
        self.assertTrue(plan["accepted"], plan["errors"])
        self.assertTrue(all(w["row_action"] == "append_row" for w in plan["writes"] if "row_action" in w))
        result = P.verify_readback(plan, saved_after(plan))
        self.assertTrue(result["ok"], result["errors"])

    def test_dry_run_needs_no_locks_or_backup_and_never_saves(self):
        plan = P.plan_repair(envelope_result(), snapshot(), {"operation": "in_place_update", "mode": "dry_run"}, SOURCE)
        self.assertTrue(plan["accepted"], plan["errors"])
        self.assertNotIn("save_in_place", plan["steps"])

    # --- approval gate ---
    def test_absent_invalid_partial_unresolved_or_rejected_approval_is_refused(self):
        self.refused("absent or invalid", env={"valid": False})
        self.refused("absent or invalid", env={})
        partial = dict(SYNTHETIC); del partial["Stats.PostureRegenRate"]
        self.refused("partial approval refused", env=envelope_result(partial))
        self.refused("unresolved fields", env=envelope_result(unresolved=["Phases[Phase_1].RateMultiplier"]))
        self.refused("without an approved alternative", env=envelope_result(rejected=["Stats.MaxHealth"]))
        extra = dict(SYNTHETIC, **{"Stats.Unknown": 1.0})
        self.refused("unknown or malformed field path", env=envelope_result(extra))
        malformed = envelope_result(); malformed["approved_for_review"][0]["field_path"] = ["Stats", "MaxHealth"]
        self.refused("unknown or malformed field path", env=malformed)
        malformed_lists = envelope_result(); malformed_lists["unresolved"] = 3
        self.refused("envelope result lists are malformed", env=malformed_lists)

    def test_bad_values_are_refused_even_if_the_envelope_said_valid(self):
        for field, bad in (("Stats.MaxHealth", 1.0), ("Stats.MaxHealth", float("nan")), ("Stats.PostureRegenDelay", -1.0),
                           ("Phases[Phase_1].EntryHealthFraction", 0.0), ("Phases[Phase_1].EntryHealthFraction", 1.5),
                           ("Phases[Phase_1].SpeedMultiplier", 0.0), ("Stats.MaxPosture", True), ("Stats.MaxPosture", "77")):
            with self.subTest(field=field, value=bad):
                self.refused("outside the native range", env=envelope_result(dict(SYNTHETIC, **{field: bad})))
        self.refused("must be Phase_1", env=envelope_result(dict(SYNTHETIC, **{"Phases[Phase_1].PhaseId": "PhaseTwo"})))

    # --- asset preservation ---
    def test_existing_asset_replacement_or_creation_is_refused(self):
        for operation in ("replace", "delete_and_recreate", "create", None):
            with self.subTest(operation):
                self.refused("only in_place_update", ctx=context(operation=operation))
        self.refused("must already exist", snap=snapshot(exists=False))
        self.refused("target must be", snap=snapshot(asset_path="/Game/OneBossFight/Data/Sevarog/DA_Boss_Sevarog_Draft_Copy"))
        twin = snapshot()["phases"][1]
        self.refused("ambiguous in-place target", snap=snapshot(phases=snapshot()["phases"] + [copy.deepcopy(twin)]))

    # --- write prerequisites ---
    def test_missing_backup_locks_or_explicit_write_is_refused(self):
        self.refused("needs a file backup", ctx=context(backup={}))
        self.refused("must equal the asset file's before-hash", ctx=context(backup={"path": "x.uasset", "sha256": "d" * 64}))
        self.refused("both C-1155 locks", ctx=context(locks={"root_held": True, "execution_held": False, "owner_token": "t"}))
        self.refused("both C-1155 locks", ctx=context(locks={"root_held": True, "execution_held": True, "owner_token": ""}))
        self.refused("explicit write flag", ctx=context(explicit_write=None))
        self.refused("before-hash", snap=snapshot(file_sha256="nothex"))
        self.refused("mode must be", ctx=context(mode="apply"))
        self.refused("owner source must be", owner_source=None)
        self.refused("owner source must be", owner_source={"sender": "Owner", "message_id": "X-99", "reply_sha256": "a" * 64,
                                                            "path": "Documentation/TEAM_MAILBOX.md"})

    # --- readback ---
    def test_successful_readback_releases_locks(self):
        plan = P.plan_repair(envelope_result(), snapshot(), context(), SOURCE)
        result = P.verify_readback(plan, saved_after(plan))
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["next"], "release_locks")

    def test_failed_readback_restores_backup_then_releases_locks(self):
        plan = P.plan_repair(envelope_result(), snapshot(), context(), SOURCE)
        cases = {
            "value not saved": saved_after(plan, stats=dict(saved_after(plan)["stats"], max_health=0.0)),
            "hash unchanged": saved_after(plan, file_sha256=BEFORE),
            "asset moved": saved_after(plan, asset_path=P.ASSET_PATH + "_New"),
            "provenance missing": saved_after(plan, fields=[]),
            "provenance source mismatch": saved_after(plan, fields=[dict(r, source_sha256="d" * 64) if r["field_path"] == "Stats.MaxHealth" else r for r in plan["field_records"]]),
            "other phase removed": saved_after(plan, phases=[saved_after(plan)["phases"][1]]),
            "duplicate Phase_1": saved_after(plan, phases=saved_after(plan)["phases"] + [saved_after(plan)["phases"][1]]),
        }
        for label, after in cases.items():
            with self.subTest(label):
                result = P.verify_readback(plan, after)
                self.assertFalse(result["ok"])
                self.assertEqual(result["next"], "restore_backup_then_release_locks")

    def test_readback_tolerates_float32_rounding_only(self):
        plan = P.plan_repair(envelope_result(), snapshot(), context(), SOURCE)
        after = saved_after(plan)
        after["phases"][1]["entry_health_fraction"] = 0.45000001788139343  # float32(0.45)
        self.assertTrue(P.verify_readback(plan, after)["ok"])
        after["phases"][1]["entry_health_fraction"] = 0.46
        self.assertFalse(P.verify_readback(plan, after)["ok"])

    def test_readback_requires_an_accepted_write_plan(self):
        dry = P.plan_repair(envelope_result(), snapshot(), {"operation": "in_place_update", "mode": "dry_run"}, SOURCE)
        self.assertFalse(P.verify_readback(dry, {})["ok"])
        plan = P.plan_repair(envelope_result(), snapshot(), context(), SOURCE)
        malformed = {"asset_path": P.ASSET_PATH, "stats": [], "phases": {}, "fields": []}
        self.assertEqual(P.verify_readback(plan, malformed)["next"], "restore_backup_then_release_locks")

    # --- proposal-only contract ---
    def test_planner_never_touches_unreal_files_or_locks(self):
        source = (HERE / "plan_sevarog_definition_repair.py").read_text(encoding="utf-8")
        for forbidden in ("import unreal", "open(", "write_text", "write_bytes", "subprocess", "os.remove", "unlink", "ENGINE_LOCK", "Path("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()

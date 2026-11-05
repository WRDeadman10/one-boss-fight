from __future__ import annotations

import tempfile
import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import compare_manifest_to_legacy_defaults as audit_tool


GROUPS = (
    "attack_tracker", "bleed", "close_clip_swap", "death", "dormant_wake",
    "encounter_policy", "fireball", "heal_punish", "look", "low_sweep",
    "phase_dependencies", "phase_flow", "phases", "shockwave",
    "stagger_policy", "stagger_profile", "stats",
)


def write_runtime_evidence(root: Path) -> None:
    by_file: dict[str, dict[int, str]] = {}
    for cite in audit_tool.PLAYER_RUNTIME_EVIDENCE:
        by_file.setdefault(cite["file"], {})[cite["line"]] = cite["excerpt"]
    for filename, citations in by_file.items():
        path = root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["// fixture"] * max(citations)
        for line, excerpt in citations.items():
            lines[line - 1] = excerpt
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def manifest() -> dict[str, object]:
    return {"definitions": {
        role: {group: ([] if group == "phases" else {}) for group in GROUPS}
        | {"stats": {"max_health": 2000.0}}
        for role in ("boss", "player")
    }}


class CompareManifestLegacyDefaultsTests(unittest.TestCase):
    def test_g044_boss_tracker_is_constructor_backed_but_player_tracker_is_not(self) -> None:
        root = Path(__file__).resolve().parents[2]
        data = json.loads((root / "Saved/G044/encounter_manifest.json").read_text(encoding="utf-8"))
        table = json.loads((root / "Scripts/Tools/legacy_defaults_g044.json").read_text(encoding="utf-8"))
        rows = audit_tool.audit(data, table, root)
        boss = [row for row in rows if row["path"].startswith("definitions.boss.attack_tracker.")]
        player = [row for row in rows if row["path"].startswith("definitions.player.attack_tracker.")]
        self.assertEqual(len(boss), 100)
        self.assertTrue(all(row["status"] == "MATCH" for row in boss))
        self.assertEqual(len(player), 100)
        self.assertTrue(all(row["status"] == "NOT-COMPARABLE" for row in player))
        self.assertFalse(any(row["status"] == "NOT-COMPARABLE"
                             and row["path"].startswith("definitions.boss.") for row in rows))
        player_unknown = [row for row in rows if row["status"] == "NOT-COMPARABLE"
                          and row["path"].startswith("definitions.player.")]
        self.assertEqual(len(player_unknown), 210)
        self.assertTrue(all(row["runtime_classification"] == "INERT"
                            and len(row["runtime_evidence"]) == 4 for row in player_unknown))
        self.assertTrue(all(row["runtime_classification"] == "NOT_PLAYER"
                            and not row["runtime_evidence"] for row in rows
                            if row["path"].startswith("definitions.boss.")))
        cooldown = {row["path"]: row for row in rows
                    if row["path"].startswith("definitions.boss.fireball.fireball_cooldown.")}
        self.assertEqual(set(cooldown), {
            "definitions.boss.fireball.fireball_cooldown.x",
            "definitions.boss.fireball.fireball_cooldown.y",
        })
        self.assertTrue(all(row["status"] == "MATCH" for row in cooldown.values()))

    def test_emits_full_legacy_boss_baseline_with_zero_mismatch(self) -> None:
        root = Path(__file__).resolve().parents[2]
        data = json.loads((root / "Saved/G044/encounter_manifest.json").read_text(encoding="utf-8"))
        table = json.loads((root / "Scripts/Tools/legacy_defaults_g044.json").read_text(encoding="utf-8"))
        emitted = audit_tool.emit_legacy_baseline(data, table, root)
        rows = audit_tool.audit(emitted, table, root)
        boss = [row for row in rows if row["path"].startswith("definitions.boss.")]
        self.assertGreater(len(boss), 0)
        self.assertTrue(all(row["status"] == "MATCH" for row in boss))
        self.assertEqual(len(emitted["definitions"]["boss"]["attack_tracker"]["attacks"]), 8)

    def test_unlisted_legacy_mismatch_is_rejected_and_explicit_field_is_accepted(self) -> None:
        rows = [{"path": "definitions.boss.stats.max_health", "status": "MISMATCH"}]
        self.assertEqual(audit_tool.validate_tuning_allowlist(rows, set()),
                         ["definitions.boss.stats.max_health"])
        self.assertEqual(audit_tool.validate_tuning_allowlist(
            rows, {"definitions.boss.stats.max_health"}), [])

    def test_s26_approval_record_binds_field_value_reason_and_owner_id(self) -> None:
        rows = [{"path": "definitions.boss.stats.max_health", "status": "MISMATCH",
                 "manifest_value": 1999.0}]
        valid = [{"field": "definitions.boss.stats.max_health", "value": 1999.0,
                  "reason": "Approved encounter tuning", "owner_approval_id": "OWNER-DECISION-42"}]
        self.assertEqual(audit_tool.parse_intentional_tuning(rows, valid),
                         {"definitions.boss.stats.max_health"})
        for bad in (
            [{"field": "definitions.boss.stats.max_health", "value": 2000.0,
              "reason": "Approved", "owner_approval_id": "OWNER-DECISION-42"}],
            [{"field": "definitions.boss.stats.max_health", "value": 1999.0,
              "reason": "", "owner_approval_id": "OWNER-DECISION-42"}],
            [{"field": "definitions.boss.stats.max_health", "value": 1999.0,
              "reason": "Approved", "owner_approval_id": ""}],
        ):
            with self.assertRaises(audit_tool.AuditError):
                audit_tool.parse_intentional_tuning(rows, bad)

    def test_s26_rejects_unknown_and_duplicate_approval_fields(self) -> None:
        rows = [{"path": "definitions.boss.stats.max_health", "status": "MISMATCH",
                 "manifest_value": 1999.0}]
        record = {"field": "definitions.boss.stats.max_health", "value": 1999.0,
                  "reason": "Approved", "owner_approval_id": "OWNER-DECISION-42"}
        with self.assertRaisesRegex(audit_tool.AuditError, "not a current MISMATCH"):
            audit_tool.parse_intentional_tuning(rows, [dict(record, field="definitions.boss.stats.other")])
        with self.assertRaisesRegex(audit_tool.AuditError, "duplicate"):
            audit_tool.parse_intentional_tuning(rows, [record, record])

    def test_reports_match_mismatch_and_not_comparable_with_source_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_runtime_evidence(root)
            (root / "source.h").write_text("float MaxHealth = 2000.f;\n", encoding="utf-8")
            table = {"rules": [
                {"pattern": "definitions.boss.stats.max_health", "status": "comparable",
                 "legacy_value": 2000.0,
                 "source": {"file": "source.h", "line": 1, "excerpt": "float MaxHealth = 2000.f;"}},
                {"pattern": "definitions.player.stats.max_health", "status": "not_comparable",
                 "reason": "No legacy player CDO value is available.",
                 "source": {"file": "source.h", "line": 1, "excerpt": "float MaxHealth = 2000.f;"}},
            ]}
            data = manifest()
            data["definitions"]["boss"]["stats"]["max_health"] = 1500.0  # type: ignore[index]
            rows = audit_tool.audit(data, table, root)
            by_path = {row["path"]: row for row in rows}
            self.assertEqual(by_path["definitions.boss.stats.max_health"]["status"], "MISMATCH")
            self.assertEqual(by_path["definitions.player.stats.max_health"]["status"], "NOT-COMPARABLE")
            self.assertEqual(by_path["definitions.player.stats.max_health"]["runtime_classification"], "INERT")
            self.assertEqual(len(by_path["definitions.player.stats.max_health"]["runtime_evidence"]), 4)

    def test_refuses_uncited_or_uncovered_manifest_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source.h").write_text("float MaxHealth = 2000.f;\n", encoding="utf-8")
            data = manifest()
            with self.assertRaisesRegex(audit_tool.AuditError, "no cited default rule"):
                audit_tool.audit(data, {"rules": []}, root)
            table = {"rules": [{"pattern": "definitions.*.stats.*", "status": "not_comparable",
                                 "reason": "unverified", "source": {"file": "source.h", "line": 1,
                                                                          "excerpt": "wrong line"}}]}
            with self.assertRaisesRegex(audit_tool.AuditError, "stale source citation"):
                audit_tool.audit(data, table, root)

    def test_text_output_includes_runtime_classification_and_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_runtime_evidence(root)
            (root / "source.h").write_text("float MaxHealth = 2000.f;\n", encoding="utf-8")
            data_path = root / "manifest.json"
            table_path = root / "defaults.json"
            data = manifest()
            data_path.write_text(json.dumps(data), encoding="utf-8")
            table = {"rules": [
                {"pattern": "definitions.boss.stats.max_health", "status": "comparable",
                 "legacy_value": 2000.0,
                 "source": {"file": "source.h", "line": 1, "excerpt": "float MaxHealth = 2000.f;"}},
                {"pattern": "definitions.player.stats.max_health", "status": "not_comparable",
                 "reason": "No legacy player CDO value is available.",
                 "source": {"file": "source.h", "line": 1, "excerpt": "float MaxHealth = 2000.f;"}},
            ]}
            table_path.write_text(json.dumps(table), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                result = audit_tool.main(["--manifest", str(data_path), "--defaults", str(table_path),
                                          "--project-root", str(root)])
            self.assertEqual(result, 0)
            self.assertIn("runtime=INERT [", output.getvalue())
        self.assertIn("RPGBossHydrationPreflight.cpp:566", output.getvalue())


if __name__ == "__main__":
    unittest.main()

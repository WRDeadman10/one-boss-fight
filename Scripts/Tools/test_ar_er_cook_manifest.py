"""Offline contracts for the read-only ER/Tier 2 package-manifest checker."""
import importlib.util
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest


MODULE = Path(__file__).with_name("ar_er_cook_manifest.py")
SPEC = importlib.util.spec_from_file_location("ar_er_cook_manifest_test", MODULE)
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class ERCookManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.required = self.root / "required.txt"
        canonical = CHECK.DEFAULT_REQUIRED.read_text(encoding="utf-8").splitlines()
        self.required.write_text("\n".join(canonical) + "\n", encoding="utf-8")
        self.manifest = self.root / "normalized.json"
        self.packages = [
            "/Game/OneBossFight/Data/SelectionRoot",
            "/Game/OneBossFight/Data/BossRoot",
            "/Game/OneBossFight/Data/PlayerRoot",
            *[line for line in canonical if line and not line.startswith("#")],
        ]
        self.value = {
            "schema": "onebossfight.g044-cook-manifest/v1",
            "build_id": "OBF-SHIPPING-20261108T000000Z-01234567",
            "configuration": "Shipping",
            "root_packages": {
                "selection": "/Game/OneBossFight/Data/SelectionRoot",
                "boss": "/Game/OneBossFight/Data/BossRoot",
                "player": "/Game/OneBossFight/Data/PlayerRoot",
            },
            "packages": self.packages,
            "source_manifest_sha256": "a" * 64,
        }

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.manifest.write_text(json.dumps(self.value, sort_keys=True), encoding="utf-8")

    def test_all_eight_required_packages_pass_and_are_hash_bound(self):
        self.save()
        result = CHECK.compare(self.required, self.manifest, self.value["build_id"], "Shipping")
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["required_package_count"], 8)
        self.assertEqual(result["normalized_manifest_sha256"], __import__("hashlib").sha256(self.manifest.read_bytes()).hexdigest())
        self.assertTrue(result["route_independent_cook_check"])
        self.assertIn("no staged identity", result["claim_scope"])

    def test_missing_required_path_is_a_cook_failure_not_invalid_input(self):
        self.value["packages"].remove(self.packages[-1])
        self.save()
        result = CHECK.compare(self.required, self.manifest, self.value["build_id"], "Shipping")
        self.assertEqual(result["verdict"], "FAIL")
        self.assertEqual(len(result["missing_packages"]), 1)

    def test_duplicate_manifest_path_is_rejected(self):
        self.value["packages"].append(self.packages[-1])
        self.save()
        with self.assertRaisesRegex(ValueError, "duplicate path"):
            CHECK.compare(self.required, self.manifest, self.value["build_id"], "Shipping")

    def test_duplicate_required_package_path_is_rejected(self):
        rows = self.required.read_text(encoding="utf-8").splitlines()
        rows[-1] = rows[-2]
        self.required.write_text("\n".join(rows) + "\n", encoding="utf-8")
        self.save()
        with self.assertRaisesRegex(ValueError, "duplicate package paths"):
            CHECK.compare(self.required, self.manifest, self.value["build_id"], "Shipping")

    def test_wrong_root_does_not_match_required_path(self):
        self.value["packages"][-1] = "/Game/Other/NS_Boss_PhaseTwoAura"
        self.save()
        result = CHECK.compare(self.required, self.manifest, self.value["build_id"], "Shipping")
        self.assertEqual(result["verdict"], "FAIL")
        self.assertIn("/game/onebossfight/data/mpc_combatfeedback", result["missing_packages"])

    def test_empty_manifest_fails_closed(self):
        self.value["packages"] = []
        self.save()
        with self.assertRaisesRegex(ValueError, "packages must be a nonempty array"):
            CHECK.compare(self.required, self.manifest, self.value["build_id"], "Shipping")

    def test_missing_build_or_configuration_identity_is_rejected(self):
        self.save()
        with self.assertRaisesRegex(ValueError, "build-id"):
            CHECK.compare(self.required, self.manifest, "", "Shipping")
        with self.assertRaisesRegex(ValueError, "configuration"):
            CHECK.compare(self.required, self.manifest, self.value["build_id"], "")

    def test_explicit_build_and_configuration_must_match_manifest(self):
        self.save()
        with self.assertRaisesRegex(ValueError, "build ID does not match"):
            CHECK.compare(self.required, self.manifest, "OTHER-BUILD", "Shipping")
        with self.assertRaisesRegex(ValueError, "configuration does not match"):
            CHECK.compare(self.required, self.manifest, self.value["build_id"], "Development")

    def test_required_list_must_have_exactly_eight_unique_packages(self):
        self.required.write_text("/Game/OneBossFight/Player/Animations/OnlyOne\n", encoding="utf-8")
        self.save()
        with self.assertRaisesRegex(ValueError, "exactly eight"):
            CHECK.compare(self.required, self.manifest, self.value["build_id"], "Shipping")

    def test_checker_contains_no_file_write_or_delete_calls(self):
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        forbidden = {"write_text", "write_bytes", "unlink", "remove", "rmdir", "mkdir", "replace"}
        calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        self.assertFalse(forbidden & calls, sorted(forbidden & calls))


if __name__ == "__main__":
    unittest.main(verbosity=2)

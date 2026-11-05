from __future__ import annotations

import unittest

import verify_encounter_package_graph as graph_tool


class EncounterPackageGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = {
            "schema": graph_tool.GRAPH_SCHEMA,
            "roots": ["/Game/Data/DA_Encounter"],
            "packages": {
                "/Game/Data/DA_Encounter": {"references": ["/Game/Data/DA_Boss", "/Game/Data/DA_Player"]},
                "/Game/Data/DA_Boss": {"references": ["/Game/Boss/SK_Boss"]},
                "/Game/Data/DA_Player": {"references": []},
                "/Game/Boss/SK_Boss": {"references": []},
                "/Game/Unused/DA_Other": {"references": []},
            },
        }
        self.manifest = {
            "schema": graph_tool.MANIFEST_SCHEMA,
            "packages": [
                "/Game/Data/DA_Encounter", "/Game/Data/DA_Boss",
                "/Game/Data/DA_Player", "/Game/Boss/SK_Boss",
                "/Game/Unrelated/Asset",
            ],
        }

    def test_transitive_reachable_packages_pass_and_unused_assets_are_ignored(self) -> None:
        self.assertEqual(graph_tool.verify(self.graph, self.manifest), [])
        included, _, errors = graph_tool.reachable(self.graph)
        self.assertNotIn("/Game/Unused/DA_Other", included)
        self.assertEqual(errors, [])

    def test_missing_transitive_package_reports_reference_chain(self) -> None:
        self.manifest["packages"].remove("/Game/Boss/SK_Boss")  # type: ignore[union-attr]
        issues = graph_tool.verify(self.graph, self.manifest)
        self.assertTrue(any("/Game/Data/DA_Encounter -> /Game/Data/DA_Boss -> /Game/Boss/SK_Boss" in issue for issue in issues))

    def test_missing_graph_node_is_not_hidden_by_manifest_membership(self) -> None:
        del self.graph["packages"]["/Game/Data/DA_Player"]  # type: ignore[index]
        issues = graph_tool.verify(self.graph, self.manifest)
        self.assertTrue(any("reachable package missing from graph" in issue and "DA_Player" in issue for issue in issues))

    def test_object_paths_and_invalid_schema_are_rejected(self) -> None:
        self.graph["roots"] = ["/Game/Data/DA_Encounter.DA_Encounter"]  # type: ignore[index]
        self.assertTrue(graph_tool.verify(self.graph, self.manifest))
        self.assertTrue(graph_tool.verify({"schema": "wrong"}, self.manifest))


if __name__ == "__main__":
    unittest.main()

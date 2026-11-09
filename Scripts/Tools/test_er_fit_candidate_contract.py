import ast
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "Editor" / "retarget_er_fit_candidate.py"
SCORECARD = ROOT / "Documentation" / "Boss" / "C1174_PLAYER_FIT_TEST_SCORECARD.md"


class ERFitCandidateContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_three_candidates_and_six_unique_clip_slots(self):
        ns = {"__name__": "er_fit_contract"}
        exec(compile(self.tree, str(SCRIPT), "exec"), ns)
        self.assertEqual(set(ns["CANDIDATES"]), {"Steel", "Greystone", "Grux"})
        clips = ns["CLIPS"]
        self.assertEqual(ns["BLIND_IDS"], {"Candidate_A", "Candidate_B", "Candidate_C"})
        self.assertEqual(len(clips), 6)
        self.assertEqual(len({clip["id"] for clip in clips}), 6)
        self.assertEqual(sum("owner-approved ER" in clip["kind"] for clip in clips), 4)
        self.assertEqual(sum("pack control" in clip["kind"] for clip in clips), 2)

    def test_script_refuses_overwrite_and_never_deletes(self):
        self.assertIn("refusing to overwrite existing fit-test asset", self.source)
        self.assertNotIn("delete_asset", self.source)
        self.assertNotIn("save_loaded_asset(source", self.source)

    def test_candidate_argument_is_explicit_and_allowlisted(self):
        ns = {"__name__": "er_fit_contract"}
        exec(compile(self.tree, str(SCRIPT), "exec"), ns)
        parse = ns["candidate_from_command_line"]
        self.assertEqual(parse("Editor -ERFitCandidate=Steel -nosound"), "Steel")
        for value in ("Editor", "Editor -ERFitCandidate=Other", "Editor -ERFitCandidate=Steelx"):
            with self.assertRaises(ValueError):
                parse(value)
        blind_parse = ns["blind_id_from_command_line"]
        self.assertEqual(blind_parse("Editor -ERFitBlindId=Candidate_B"), "Candidate_B")
        with self.assertRaises(ValueError):
            blind_parse("Editor -ERFitBlindId=Steel")

    def test_root_distance_uses_ten_percent_and_in_place_floor(self):
        ns = {"__name__": "er_fit_contract"}
        exec(compile(self.tree, str(SCRIPT), "exec"), ns)
        compare = ns["root_distance_match"]
        self.assertEqual(compare(100.0, 110.0), (True, 10.0))
        self.assertEqual(compare(100.0, 111.0), (False, 11.0))
        self.assertEqual(compare(0.0, 0.1), (True, None))
        self.assertEqual(compare(None, 0.1), (None, None))

    def test_batch_outputs_are_source_named_and_confined_to_candidate_root(self):
        ns = {"__name__": "er_fit_contract"}
        exec(compile(self.tree, str(SCRIPT), "exec"), ns)
        output_name = ns["expected_output_name"]
        self.assertEqual(output_name("AN_ER_Attack_Air_Heavy_Plunge", "Greystone"),
                         "AN_ER_Attack_Air_Heavy_Plunge_Fit_Greystone")
        confined = ns["require_package_under"]
        confined("/Game/OneBossFight/Player/FitTest/Steel/AN_ER_Fit.AN_ER_Fit",
                 "/Game/OneBossFight/Player/FitTest/Steel")
        with self.assertRaises(RuntimeError):
            confined("/Game/AN_ER_Attack_Fit_Steel",
                     "/Game/OneBossFight/Player/FitTest/Steel")

    def test_batch_paths_are_renamed_and_validated_before_output_save(self):
        rename_at = self.source.index("EditorAssetLibrary.rename_asset(result_source_path, output_path)")
        assert_at = self.source.index("require_package_under(output.get_path_name(), root)")
        save_at = self.source.index("save_loaded_asset(output)")
        self.assertLess(rename_at, assert_at)
        self.assertLess(assert_at, save_at)
        self.assertNotIn("duplicate_asset(", self.source)
        self.assertNotIn("RetargetInputs", self.source)
        self.assertNotIn("save_directory(root)", self.source)

    def test_rerun_reuses_only_complete_asset_pair(self):
        ns = {"__name__": "er_fit_contract"}
        exec(compile(self.tree, str(SCRIPT), "exec"), ns)
        self.assertFalse(ns["existing_asset_pair_state"](False, False))
        self.assertTrue(ns["existing_asset_pair_state"](True, True))
        with self.assertRaises(RuntimeError):
            ns["existing_asset_pair_state"](True, False)

    def test_all_referenced_sources_exist_as_project_packages(self):
        ns = {"__name__": "er_fit_contract"}
        exec(compile(self.tree, str(SCRIPT), "exec"), ns)
        package_paths = [entry["mesh"] for entry in ns["CANDIDATES"].values()]
        package_paths += [entry["path"] for entry in ns["CLIPS"]]
        package_paths += [ns["SOURCE_MESH"], ns["SOURCE_IK_RIG"]]
        for package in package_paths:
            relative = package.removeprefix("/Game/").replace("/", "/") + ".uasset"
            self.assertTrue((ROOT / "Content" / relative).is_file(), package)

    def test_scorecard_covers_each_candidate_and_limitations(self):
        text = SCORECARD.read_text(encoding="utf-8")
        for blind_id in ("Candidate_A", "Candidate_B", "Candidate_C"):
            self.assertIn("| %s |" % blind_id, text)
        for term in ("Weapon in hand", "No foot sliding", "clipping", "±10%", "0 to 2", "Candidate_A", "D:/FightVideo/fit_test"):
            self.assertIn(term.lower(), text.lower())


if __name__ == "__main__":
    unittest.main()

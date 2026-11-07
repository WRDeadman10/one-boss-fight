"""Offline tests for Scripts/Editor/import_er_clips.py configuration and asset availability."""

import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys_path = os.fspath(REPO_ROOT / "Scripts" / "Editor")
if sys_path not in os.sys.path:
    os.sys.path.insert(0, sys_path)

import import_er_clips


def registry_row(clip_id, status, name="Clip"):
    """Build a structurally complete eight-column GATE-07 data row."""
    return f"| **{clip_id}** | {name} | 0.5 s | 160 | motion | video.mp4 | strip.png | {status} |"


class TestImportERClips(unittest.TestCase):
    def test_clips_configuration(self):
        self.assertEqual(len(import_er_clips.CLIPS), 4)
        expected_names = {
            "AN_ER_Backstep_Back",
            "AN_ER_Attack_GuardCounter",
            "AN_ER_Attack_Air_Heavy_Plunge",
            "AN_ER_Attack_Air_Light",
        }
        actual_names = {c["name"] for c in import_er_clips.CLIPS}
        self.assertEqual(actual_names, expected_names)

    def test_destination_directory(self):
        self.assertEqual(import_er_clips.DEST_DIR, "/Game/OneBossFight/Player/Animations")
        self.assertEqual(
            import_er_clips.SKELETON_PATH,
            "/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin",
        )

    def test_import_duration_metadata_tracks_source_sequences_not_montage_slices(self):
        durations = {clip["gate_id"]: (clip["duration"], clip["frames"]) for clip in import_er_clips.CLIPS}
        self.assertEqual(durations, {
            "ER-A1": (0.4667, 15),
            "ER-A4": (1.6667, 50),
            "ER-A3": (1.4000, 42),
            "ER-A2": (1.4000, 42),
        })

    def test_explicit_clip_list_is_required(self):
        with self.assertRaisesRegex(ValueError, "IMPORT_CLIPS is required"):
            import_er_clips.parse_requested_clips(None)
        with self.assertRaisesRegex(ValueError, "implicit/all-clips"):
            import_er_clips.parse_requested_clips(" ")

    def test_unknown_and_duplicate_clip_names_refuse(self):
        with self.assertRaisesRegex(ValueError, "unknown clip"):
            import_er_clips.parse_requested_clips("AN_ER_NotAClip")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            import_er_clips.parse_requested_clips("AN_ER_Attack_GuardCounter,AN_ER_Attack_GuardCounter")
        with self.assertRaisesRegex(ValueError, "empty list entry"):
            import_er_clips.parse_requested_clips("AN_ER_Attack_GuardCounter,")

    def test_registry_acceptance_gates_requested_clips(self):
        registry = (REPO_ROOT / import_er_clips.ACCEPTANCE_REGISTRY).read_text(encoding="utf-8-sig")
        selected = import_er_clips.select_accepted_clips("AN_ER_Attack_GuardCounter,AN_ER_Attack_Air_Heavy_Plunge,AN_ER_Attack_Air_Light,AN_ER_Backstep_Back", registry)
        self.assertEqual([clip["gate_id"] for clip in selected], ["ER-A4", "ER-A3", "ER-A2", "ER-A1"])
        unaccepted_registry = registry_row("ER-A1", "**DELIVERED (R7)**", "Backstep") + "\n"
        with self.assertRaisesRegex(ValueError, "does not mark accepted"):
            import_er_clips.select_accepted_clips("AN_ER_Backstep_Back", unaccepted_registry)

    def test_registry_parser_does_not_accept_delivered_only_rows(self):
        registry = "\n".join([
            registry_row("ER-A1", "**DELIVERED (R4)**", "Backstep"),
            registry_row("ER-A4", "**ACCEPTED (C-968)**", "Counter"),
        ])
        self.assertEqual(import_er_clips.accepted_clip_ids_from_registry(registry), {"ER-A4"})

    def test_registry_parser_accepts_only_affirmative_status_prefixes(self):
        registry = "\n".join([
            registry_row("ER-A1", "**ACCEPTED FOR OWNER REVIEW (C-977)**", "Backstep"),
            registry_row("ER-A2", "**DELIVERY ACCEPTED (C-972)**", "Air Light"),
            registry_row("ER-A3", "**NOT ACCEPTED**", "Air Heavy"),
            registry_row("ER-A4", "**PENDING ACCEPTANCE**", "Counter"),
        ])
        self.assertEqual(import_er_clips.accepted_clip_ids_from_registry(registry), {"ER-A1", "ER-A2"})

    def test_registry_parser_rejects_unaccepted_prefix_forms(self):
        for status in ("UN-ACCEPTED", "UN ACCEPTED", "NOT ACCEPTED (C-979)", "PENDING ACCEPTANCE (C-979)"):
            with self.subTest(status=status):
                registry = registry_row("ER-A1", f"**{status}**", "Backstep") + "\n"
                self.assertEqual(import_er_clips.accepted_clip_ids_from_registry(registry), set())

    def test_registry_parser_rejects_duplicate_malformed_and_missing_status_rows(self):
        accepted = registry_row("ER-A1", "**ACCEPTED (C-977)**", "Backstep")
        pending_duplicate = registry_row("ER-A1", "**PENDING ACCEPTANCE**", "Backstep duplicate")
        malformed_pipe_row = "| **ER-A2** | Air Light | **ACCEPTED (C-972)** |"
        missing_status = registry_row("ER-A3", "", "Air Heavy")
        valid_other = registry_row("ER-A4", "**DELIVERY ACCEPTED (C-968)**", "Counter")
        registry = "\n".join([accepted, pending_duplicate, malformed_pipe_row, missing_status, valid_other])
        self.assertEqual(import_er_clips.accepted_clip_ids_from_registry(registry), {"ER-A4"})

    def test_fbx_files_exist_and_non_empty(self):
        project_dir = os.fspath(REPO_ROOT)
        for clip in import_er_clips.CLIPS:
            fbx_path = import_er_clips.get_fbx_source_path(clip, project_dir)
            self.assertIsNotNone(fbx_path, f"FBX path for {clip['name']} could not be resolved")
            self.assertTrue(os.path.isfile(fbx_path), f"FBX file does not exist: {fbx_path}")
            size = os.path.getsize(fbx_path)
            self.assertGreater(size, 500_000, f"FBX file suspiciously small ({size} bytes): {fbx_path}")


if __name__ == "__main__":
    unittest.main()

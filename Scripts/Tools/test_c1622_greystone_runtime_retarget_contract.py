"""Static safety contract for C-1622 authoring sources (no Unreal invocation)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CPP = (ROOT / "Source/OneBossFightEditor/Private/RPGGreystoneRuntimeRetargetLibrary.cpp").read_text(encoding="utf-8")
HEADER = (ROOT / "Source/OneBossFightEditor/Public/RPGGreystoneRuntimeRetargetLibrary.h").read_text(encoding="utf-8")
SCRIPT = (ROOT / "Scripts/Editor/author_greystone_runtime_retarget.py").read_text(encoding="utf-8")
ADAPTER = (ROOT / "Scripts/Editor/greystone_runtime_retarget_stage.py").read_text(encoding="utf-8")
RUNNER = (ROOT / "Scripts/Editor/run_greystone_runtime_retarget_locked.ps1").read_text(encoding="utf-8")


class GreystoneRetargetContract(unittest.TestCase):
    def test_editor_only_surface_and_single_retarget_node(self):
        build = (ROOT / "Source/OneBossFightEditor/OneBossFightEditor.Build.cs").read_text(encoding="utf-8")
        self.assertIn('"IKRigDeveloper"', build)
        self.assertIn('"AnimGraph"', build)
        self.assertEqual(CPP.count("NewObject<UAnimGraphNode_RetargetPoseFromMesh>"), 1)
        self.assertIn("IKRetargeterAsset = Retargeter", CPP)
        self.assertIn("bUseAttachedParent = true", CPP)

    def test_source_mesh_is_hidden_and_keeps_canonical_anim_bp(self):
        self.assertIn('TEXT("ABP_CombatCharacter_C")', CPP)
        self.assertIn('TEXT("SKM_CombatMannequin")', CPP)
        self.assertIn("GetCanonicalPackMeshAndAnim", CPP)
        self.assertIn("SetSkeletalMesh(PackMesh)", CPP)
        self.assertIn("SetAnimInstanceClass(PackAnimClass)", CPP)
        self.assertIn("SetHiddenInGame(true, false)", CPP)
        self.assertIn("AlwaysTickPoseAndRefreshBones", CPP)
        self.assertIn("GetSourceOverride", CPP)

    def test_visible_mesh_setup_is_allowlisted_and_non_destructive(self):
        self.assertIn("VisibleComponentName", CPP)
        self.assertIn("SetParent(SourceTemplate)", CPP)
        self.assertIn("SetSkeletalMesh(GreystoneMesh)", CPP)
        self.assertIn("SetAnimInstanceClass(AnimBlueprint->GeneratedClass)", CPP)
        self.assertNotIn("DeleteAsset", CPP)
        self.assertNotIn("delete_asset", SCRIPT.lower())

    def test_python_dry_run_is_default_and_audits_attachments(self):
        self.assertIn('WRITE = "--write" in sys.argv', SCRIPT)
        self.assertIn('RESULT=DRY_RUN assets_saved=0', SCRIPT)
        self.assertIn("ATTACH_AUDIT", SCRIPT)
        self.assertIn("get_greystone_player_component_inventory", SCRIPT)
        self.assertNotIn('get_editor_property("simple_construction_script")', SCRIPT)
        self.assertIn('source_mesh.get_name().startswith("SKM_CombatMannequin")', SCRIPT)
        self.assertIn('source_anim.get_name() == "ABP_CombatCharacter_C"', SCRIPT)
        self.assertIn('if not WRITE:', SCRIPT)
        self.assertIn("save_loaded_asset(anim_bp)", SCRIPT)
        self.assertIn("save_loaded_asset(bp)", SCRIPT)
        self.assertIn('RUN_RESULT = "PASS"', SCRIPT)
        self.assertIn('namespace.get("RUN_RESULT") != "PASS"', ADAPTER)

    def test_component_inventory_is_read_only_and_includes_local_and_inherited_templates(self):
        self.assertIn("GetGreystonePlayerComponentInventory", HEADER)
        self.assertIn("SCS->GetAllNodes()", CPP)
        self.assertIn("GetInheritableComponentHandler(false)", CPP)
        self.assertIn("CreateRecordIterator()", CPP)
        self.assertIn("FindSCSNode()", CPP)
        self.assertIn('TEXT("%s|%s|%s|%s|%s|%s")', CPP)
        self.assertIn('split("|", 5)', SCRIPT)

    def test_runner_builds_then_authors_under_c1155_and_requires_lead_receipt(self):
        self.assertIn("CreateNew", RUNNER)
        self.assertIn("[IO.File]::Move", RUNNER)
        self.assertIn("C-1155", RUNNER)
        self.assertIn("LeadApprovalReceipt", RUNNER)
        self.assertIn("OneBossFightEditor", RUNNER)
        self.assertLess(RUNNER.index("& $build OneBossFightEditor"), RUNNER.index("Invoke-Child $stageName $editor"))
        self.assertIn("-nosound", RUNNER)
        self.assertIn("-BGreystoneRetargetWrite=1", RUNNER)
        self.assertIn("UnrealEditor*", RUNNER)

    def test_author_adapter_is_explicit_and_never_saves_assets(self):
        self.assertIn("-BGreystoneRetargetWrite=", ADAPTER)
        self.assertIn('["--write"]', ADAPTER)
        self.assertNotIn("save_loaded_asset", ADAPTER)

    def test_c1633_lead_hotfix_history(self):
        self.assertIn("SKM_CombatMannequin_Simple", CPP)
        self.assertIn('TEXT("ABP_CombatCharacter_C")', CPP)
        self.assertIn("RowMeshPath", CPP)
        self.assertIn("AnimClass.Get()", CPP)
        self.assertIn("GetOutermost()->GetName()", CPP)
        self.assertIn("FLogErrorOnExit", CPP)
        self.assertIn("CharacterMesh0", CPP)
        self.assertIn("unpack_result", SCRIPT)
        self.assertIn("ExitCode", RUNNER)


if __name__ == "__main__":
    unittest.main()

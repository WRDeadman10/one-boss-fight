"""Contract tests for BT-63 production framework profile and encounter rebind runner."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "Scripts/Editor/run_author_production_framework_profile_locked.ps1"
DRIVER_PATH = ROOT / "Scripts/Editor/author_production_framework_profile.py"


class AuthorProductionProfileRunnerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner_text = RUNNER_PATH.read_text(encoding="utf-8")
        cls.driver_text = DRIVER_PATH.read_text(encoding="utf-8")

    def test_runner_exists_and_is_non_empty(self):
        self.assertTrue(RUNNER_PATH.is_file(), "Runner script must exist at " + str(RUNNER_PATH))
        self.assertGreater(len(self.runner_text), 500)

    def test_runner_parameters_and_target_health_pin(self):
        self.assertIn("[string]$Mode = 'Full'", self.runner_text)
        self.assertIn("[double]$TargetHealth = 800.0", self.runner_text)
        self.assertIn("[switch]$SkipBuildGate", self.runner_text)
        self.assertIn("if ($TargetHealth -ne 800.0)", self.runner_text)
        self.assertIn("owner-approved production value 800.0 HP", self.runner_text)

    def test_c1155_dual_lock_protocol(self):
        self.assertIn("ENGINE_LOCK.json", self.runner_text)
        self.assertIn("Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json", self.runner_text)
        self.assertIn("function Write-AtomicLock", self.runner_text)
        self.assertIn("policy = 'C-1155'", self.runner_text)
        self.assertIn("agent = 'Antigravity'", self.runner_text)
        self.assertIn("command_id = 'BT63.author-production-framework-profile'", self.runner_text)
        self.assertIn("ABORT: existing C-1155 lock:", self.runner_text)

    def test_preflight_process_and_file_checks(self):
        self.assertIn("function Test-UnrealRunning", self.runner_text)
        self.assertIn("ABORT: close UnrealEditor / UnrealEditor-Cmd before C-1155 BT-63 operation", self.runner_text)
        self.assertIn("$driver = Join-Path $root 'Scripts\\Editor\\author_production_framework_profile.py'", self.runner_text)
        self.assertIn("$profileAsset = Join-Path $root 'Content\\OneBossFight\\Data\\Sevarog\\DA_Boss_Sevarog_FrameworkProfile_Production.uasset'", self.runner_text)
        self.assertIn("$encounterAsset = Join-Path $root 'Content\\OneBossFight\\Data\\Sevarog\\DA_Sevarog_Framework_Encounter.uasset'", self.runner_text)
        self.assertIn("$frameworkProfileCpp = Join-Path $root 'Source\\OneBossFight\\Player\\RPGBossFrameworkProfile.cpp'", self.runner_text)
        self.assertIn("$frameworkRuntimeTestsCpp = Join-Path $root 'Source\\OneBossFight\\Tests\\RPGFrameworkRuntimeTests.cpp'", self.runner_text)
        self.assertIn("$acceptanceRunner = Join-Path $root 'Scripts\\Editor\\run_sevarog_arena_route_acceptance.ps1'", self.runner_text)
        self.assertIn("$acceptanceDriver = Join-Path $root 'Scripts\\Editor\\pie_sevarog_arena_route_acceptance.py'", self.runner_text)

    def test_lock_acquisition_precedes_backups_and_post_lock_drift_check(self):
        lock_idx = self.runner_text.index("Write-AtomicLock $lock")
        backup_idx = self.runner_text.index("Copy-Item -LiteralPath $encounterAsset -Destination $encounterBackup")
        self.assertLess(lock_idx, backup_idx, "Dual C-1155 locks must be acquired BEFORE any backup or disk mutation")

        self.assertIn("Source files drifted during C-1155 lock acquisition", self.runner_text)
        self.assertIn("$preLockCppHash", self.runner_text)
        self.assertIn("$cppHash -cne $preLockCppHash", self.runner_text)

    def test_build_gate_assertions_and_schema_binding(self):
        self.assertIn("route_lead_approval.json", self.runner_text)
        self.assertIn("Saved\\C1619RouteBuild", self.runner_text)
        self.assertIn("source_build_exit -eq 0", self.runner_text)
        self.assertIn("suite_result -ceq 'PASS'", self.runner_text)
        self.assertIn("suite_complete -eq $true", self.runner_text)
        self.assertIn("failed -eq 0", self.runner_text)
        self.assertIn("cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec", self.runner_text)
        self.assertIn("framework_profile_cpp_sha256", self.runner_text)
        self.assertIn("framework_runtime_tests_cpp_sha256", self.runner_text)
        self.assertIn("acceptance_runner_sha256", self.runner_text)
        self.assertIn("acceptance_driver_sha256", self.runner_text)
        self.assertIn("locks_released -eq 2", self.runner_text)
        self.assertIn("suiteRunMatches", self.runner_text)
        self.assertIn("verified_build_token", self.runner_text)

    def test_skip_build_gate_restricted_to_dry_run(self):
        self.assertIn("if ($SkipBuildGate)", self.runner_text)
        self.assertIn("if ($Mode -ne 'DryRun')", self.runner_text)
        self.assertIn("-SkipBuildGate is only permitted when -Mode DryRun is specified", self.runner_text)

    def test_backup_and_rollback_mechanisms(self):
        self.assertIn("$encounterBackup = Join-Path $backupDir (Split-Path $encounterAsset -Leaf)", self.runner_text)
        self.assertIn("Copy-Item -LiteralPath $encounterAsset -Destination $encounterBackup", self.runner_text)
        self.assertIn("ABORT: encounter backup hash mismatch", self.runner_text)
        self.assertIn("Copy-Item -LiteralPath $encounterBackup -Destination $encounterAsset -Force", self.runner_text)
        self.assertIn("$encounterRestored = $true", self.runner_text)

    def test_profile_rollback_hash_verification(self):
        self.assertIn("$restoredProfHash = (Get-FileHash -LiteralPath $profileAsset -Algorithm SHA256).Hash", self.runner_text)
        self.assertIn("if ($restoredProfHash -cne $initialProfileHash)", self.runner_text)
        self.assertIn("$profileRestored = $true", self.runner_text)
        self.assertIn("profile_restored", self.runner_text)
        self.assertIn("$profileCleanedUp = $true", self.runner_text)

    def test_lock_retention_when_unreal_running_and_preflight_mask_prevention(self):
        self.assertIn("unrealRunningAtExit = Test-UnrealRunning", self.runner_text)
        self.assertIn("if (-not $unrealRunningAtExit)", self.runner_text)
        self.assertIn("locksRetained.Add($lock)", self.runner_text)
        self.assertIn("locks_retained", self.runner_text)
        self.assertIn("if (Test-Path -LiteralPath $run -PathType Container)", self.runner_text)

    def test_three_stage_authoring_lifecycle(self):
        self.assertIn("Invoke-AuthorStage 'dry_run'", self.runner_text)
        self.assertIn("Invoke-AuthorStage 'write'", self.runner_text)
        self.assertIn("Invoke-AuthorStage 'readback'", self.runner_text)
        self.assertIn("dry_run modified DA_Sevarog_Framework_Encounter package", self.runner_text)
        self.assertIn("write stage did not update DA_Sevarog_Framework_Encounter package", self.runner_text)
        self.assertIn("62ecc592e0c2ad57ec0b5d70afd56ba7ea1dc7f9d0fd1dc7a3fc1b625ac6d305", self.runner_text)
        self.assertIn("receipt player_posture_hit_amount mismatch", self.runner_text)
        self.assertIn("receipt stagger_seconds mismatch", self.runner_text)

    def test_driver_encounter_rebind_and_dry_run_safety(self):
        self.assertIn("ENCOUNTER_NAME = \"DA_Sevarog_Framework_Encounter\"", self.driver_text)
        self.assertIn("def build_encounter_payload(", self.driver_text)
        self.assertIn("def compute_encounter_manifest_hash(", self.driver_text)
        self.assertIn("def verify_encounter_readback(", self.driver_text)
        self.assertIn("rebind_encounter=False", self.driver_text)
        self.assertIn("--rebind-encounter", self.driver_text)
        self.assertIn("PRODUCTION_PROFILE_REBIND_ENCOUNTER", self.driver_text)
        self.assertIn("SEVAROG_AUTHOR_RECEIPT_PATH", self.driver_text)
        self.assertIn("if dry_run:", self.driver_text)
        self.assertIn("write = False", self.driver_text)

    def test_invoke_author_stage_rejects_log_python_errors(self):
        self.assertIn("LogPython:\\s*Error:|LogEditorPythonExecuter:\\s*Error:", self.runner_text)
        self.assertIn("FAIL: Editor stage '$StageName' reported Python error in log", self.runner_text)


if __name__ == "__main__":
    unittest.main()

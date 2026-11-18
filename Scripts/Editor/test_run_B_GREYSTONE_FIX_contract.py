"""C-1618 static contract: Greystone runner is prepared but never launched by this test."""
import ast
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
RUNNER = HERE / "run_B_GREYSTONE_FIX_locked.ps1"
ADAPTER = HERE / "greystone_fix_stage.py"
AUTHOR = HERE / "author_greystone_player.py"
REPOINT = HERE / "repoint_greystone_rolls_rm.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_assign(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return node.value
    raise AssertionError(name + " not found")


class GreystoneFixRunnerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = RUNNER.read_text(encoding="utf-8")
        cls.adapter = ADAPTER.read_text(encoding="utf-8")
        cls.code = "\n".join(line for line in cls.runner.splitlines() if not line.lstrip().startswith("#"))

    def test_c1155_atomic_locks_token_readback_and_editor_abort(self):
        s = self.code
        self.assertIn("ENGINE_LOCK.json", s)
        self.assertIn("Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json", s)
        self.assertIn("[System.IO.FileMode]::CreateNew", s)
        self.assertIn("[System.IO.FileShare]::None", s)
        self.assertIn("[System.IO.File]::Move($temp,$lock)", s)
        self.assertIn("$readBack.owner_token -ne $token", s)
        self.assertIn("Get-Process UnrealEditor*", s)
        self.assertIn("ABORT: UnrealEditor process is running (preflight)", s)
        self.assertIn("ABORT: UnrealEditor process appeared after lock acquisition", s)
        self.assertIn("ABORT: UnrealEditor process appeared before $Name launch", s)

    def test_lead_approval_receipt_required_before_evidence_or_engine(self):
        s = self.code
        approval = s.index("$approval = Get-Content -Raw -LiteralPath $LeadApprovalReceipt")
        evidence = s.index("New-Item -ItemType Directory -Path $backupRoot")
        self.assertLess(approval, evidence)
        self.assertIn("$approval.task -ne 'C-1618'", s)
        self.assertIn("$approval.lead -ne 'Claude'", s)
        self.assertIn("$approval.approved -ne $true", s)
        self.assertIn("lead_approval_sha256", s)

    def test_six_stages_are_ordered_and_fail_fast(self):
        calls = [
            "Invoke-EditorPython '01_layer_dry'", "Invoke-EditorPython '02_layer_write'",
            "Invoke-EditorPython '03_rolls_dry'", "Invoke-EditorPython '04_rolls_write'",
            "Invoke-EditorPython '05_repoint_dry'", "Invoke-EditorPython '06_repoint_write'",
        ]
        positions = [self.code.index(call) for call in calls]
        self.assertEqual(positions, sorted(positions))
        for token in ("-GreyLayerRepairWrite", "--write", "-RMRepointWrite"):
            self.assertIn(token, self.code)
        self.assertIn("RESULT=", self.code)
        self.assertIn("step_results.json", self.code)
        self.assertIn("$ExpectedResult", self.code)
        self.assertIn("$processHandle = $proc.Handle", self.code)
        self.assertIn("-Pattern '\\] RESULT=' -CaseSensitive", self.code)
        self.assertIn("-cmatch", self.code)

    def test_full_editor_only_and_narrow_scope(self):
        s = self.code
        self.assertIn("UnrealEditor.exe", s)
        self.assertNotIn("UnrealEditor-Cmd.exe", s)
        self.assertIn("-ExecutePythonScript=$stageAdapter", s)
        self.assertIn("'-nosound'", s)
        for forbidden in ("-NullRHI", "Build.bat", "BuildCookRun", "RunUAT", "-run=cook", "PlayInEditor", "RunDrivers"):
            self.assertNotIn(forbidden, s)
        self.assertIn("NO_BUILD=1", s)
        self.assertIn("NO_PIE=1", s)
        self.assertIn("NO_MAP_SAVE=1", s)

    def test_rollback_manifest_covers_existing_and_generated_packages(self):
        s = self.code
        self.assertIn("rollback_manifest.json", s)
        self.assertIn("Get-FileHash", s)
        self.assertIn("existing_package_file_backups", s)
        self.assertIn("possible_run_created_packages", s)
        self.assertIn("ABP_UnarmedLayer_Grey", s)
        self.assertIn("BP_GreystoneERPlayer", s)
        self.assertIn("Sequences/quick/Dodge_Small_Forward_Roll_RM", s)
        self.assertIn("Montages/full/Dodge_To_Idle_Montage_Grey_RM", s)
        self.assertIn("restore_policy", s)

    def test_finally_writes_status_and_releases_only_owned_locks(self):
        s = self.code
        fin = s.index("} finally {")
        tail = s[fin:]
        self.assertIn("status.txt", tail)
        self.assertIn("foreach ($lock in $created)", tail)
        self.assertIn("$current.owner_token -eq $token", tail)
        self.assertIn("C-1155 locks retained", tail)

    def test_stage_adapter_is_allowlisted_and_closes_editor(self):
        s = self.adapter
        for stage in ("layer", "rolls", "repoint"):
            self.assertIn('"%s":' % stage, s)
        self.assertIn("repair_grey_layer_parents.py", s)
        self.assertIn("retarget_greystone_pack_rolls_rm.py", s)
        self.assertIn("repoint_greystone_rolls_rm.py", s)
        self.assertIn("exec(compile(source, target, \"exec\")", s)
        self.assertIn('execute_console_command(None, "Quit")', s)
        self.assertIn("RESULT=FAIL", s)

    def test_reauthor_defaults_match_verified_rm_repoint_targets(self):
        module = load(REPOINT, "greystone_repoint_for_runner_contract")
        author_tree = ast.parse(AUTHOR.read_text(encoding="utf-8"))
        fields = ast.literal_eval(literal_assign(author_tree, "CHILD_FIELDS"))
        for field in ("QuickMontage", "FullMontage"):
            self.assertEqual(module.REPOINTS[field][1], fields[field])


if __name__ == "__main__":
    unittest.main()

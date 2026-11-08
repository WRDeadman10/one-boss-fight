"""Offline contracts for fail-closed Lead PIE route attribution."""
from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LeadRouteProvenanceContractTests(unittest.TestCase):
    def test_runner_splits_comma_delimited_env_entries_and_logs_applied_values(self):
        source = (ROOT / "Scripts" / "RunLeadPie.ps1").read_text(encoding="utf-8")
        self.assertIn("foreach ($rawEntry in ($entry -split ','))", source)
        self.assertIn("DRY RUN env $name=$($extraEnv[$name])", source)
        self.assertIn("Applying -Env $name=$($extraEnv[$name])", source)
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell unavailable for dry-run env contract")
        runner = ROOT / "Scripts" / "RunLeadPie.ps1"
        probe = ROOT / "Scripts" / "Editor" / "pie_full_fight.py"
        output = subprocess.run(
            [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(runner),
             "-Script", str(probe), "-Routes", "data", "-Env", "FIGHT_MAX=30,FIGHT_RUN=test",
             "-OutputDir", "AU_ENV_DRYRUN", "-DryRun"],
            cwd=ROOT, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(output.returncode, 0, output.stdout + output.stderr)
        self.assertIn("DRY RUN env FIGHT_MAX=30", output.stdout)
        self.assertIn("DRY RUN env FIGHT_RUN=test", output.stdout)
        self.assertNotIn("FIGHT_MAX=30,FIGHT_RUN=test", output.stdout)

    def test_generic_runner_exec_cmds_has_lowercase_py_path_without_spaces(self):
        source = (ROOT / "Scripts" / "RunLeadPie.ps1").read_text(encoding="utf-8")
        self.assertIn(".ToLowerInvariant()", source)
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell unavailable for dry-run ExecCmds contract")
        runner = ROOT / "Scripts" / "RunLeadPie.ps1"
        probe = ROOT / "Scripts" / "Editor" / "pie_full_fight.py"
        output = subprocess.run(
            [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(runner),
             "-Script", str(probe), "-Routes", "data", "-OutputDir", "AU_C1116_DRYRUN", "-DryRun"],
            cwd=ROOT, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(output.returncode, 0, output.stdout + output.stderr)
        match = re.search(r'-ExecCmds="py ([^"]+)"', output.stdout)
        self.assertIsNotNone(match, output.stdout)
        python_path = match.group(1)
        self.assertTrue(python_path.endswith(".py"), python_path)
        self.assertEqual(python_path, python_path.lower(), python_path)
        self.assertNotIn(" ", python_path)
    def test_generic_lead_runner_sets_and_restores_explicit_legacy_flag(self):
        source = (ROOT / "Scripts" / "RunLeadPie.ps1").read_text(encoding="utf-8")
        self.assertIn("'RPG_LEGACY_STARTUP'", source)
        self.assertIn("if ($route -eq 'legacy') { '1' } else { '' }", source)
        self.assertIn("$savedEnv[$name]", source)

    def test_generic_lead_runner_requires_actual_activation_route(self):
        source = (ROOT / "Scripts" / "RunLeadPie.ps1").read_text(encoding="utf-8")
        self.assertIn("\\[EncounterActivation\\] route=(legacy|data)", source)
        self.assertIn("$activationRoutes[0] -eq $route", source)
        self.assertIn("-or -not $routeVerified", source)
        self.assertIn("$_.Contains('[EncounterActivation]')", source)

    def test_a5_pair_runner_keeps_explicit_legacy_and_checks_witness(self):
        source = (ROOT / "Scripts" / "RunA5ParityPair.ps1").read_text(encoding="utf-8")
        self.assertIn("$env:RPG_LEGACY_STARTUP = '1'", source)
        self.assertIn("$activationRoutes[0] -ne $Route", source)
        self.assertIn("EncounterActivation route witness missing or mismatched", source)

    def test_receipt_ignores_default_startup_route_and_reads_probe_route(self):
        source = (ROOT / "Scripts" / "Tools" / "ar_charge_receipt.py").read_text(encoding="utf-8")
        self.assertIn("(?:ERControlLatency|Showcase)", source)
        self.assertIn("ACTIVATION_ROUTE_RE", source)
        self.assertIn("disagrees with probe route", source)
        self.assertIn("route_witness_file", source)

    def test_runner_handoff_documents_explicit_legacy_and_log_witness(self):
        doc = (ROOT / "Documentation" / "Boss" / "AR_C06_C10_KI192_RECEIPT_TOOL.md").read_text(encoding="utf-8")
        self.assertIn("RPG_LEGACY_STARTUP=1", doc)
        self.assertIn("[EncounterActivation] route=legacy", doc)
        self.assertIn("fails closed", doc)


if __name__ == "__main__":
    unittest.main()

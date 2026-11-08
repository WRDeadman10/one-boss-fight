"""Offline contracts for fail-closed Lead PIE route attribution."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LeadRouteProvenanceContractTests(unittest.TestCase):
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
        self.assertNotIn("ROUTE_RE = re.compile(r\"\\broute=", source)

    def test_runner_handoff_documents_explicit_legacy_and_log_witness(self):
        doc = (ROOT / "Documentation" / "Boss" / "AR_C06_C10_KI192_RECEIPT_TOOL.md").read_text(encoding="utf-8")
        self.assertIn("RPG_LEGACY_STARTUP=1", doc)
        self.assertIn("[EncounterActivation] route=legacy", doc)
        self.assertIn("fails closed", doc)


if __name__ == "__main__":
    unittest.main()

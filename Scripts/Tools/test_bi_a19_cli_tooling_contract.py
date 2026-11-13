import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_DIR = REPO_ROOT / "Scripts" / "Tools"
SCRIPTS_DIR = REPO_ROOT / "Scripts"

KI_TOOL_FILES = (
    TOOLS_DIR / "make_source_manifest.py",
    TOOLS_DIR / "profile_dump.py",
    TOOLS_DIR / "card_table.py",
    TOOLS_DIR / "validate_baked_cards.py",
    TOOLS_DIR / "plugin_dependencies.py",
    TOOLS_DIR / "proof_report.py",
    TOOLS_DIR / "asset_provenance.py",
    TOOLS_DIR / "evidence_summary.py",
    TOOLS_DIR / "token_coverage.py",
    TOOLS_DIR / "suite_log_report.py",
    TOOLS_DIR / "summarize_framework_log.py",
    TOOLS_DIR / "plot_framework_timeline.py",
)

ACTIVE_ROOT_CLIS = (
    SCRIPTS_DIR / "CheckDocs.py",
    SCRIPTS_DIR / "CheckShippingBinary.py",
    SCRIPTS_DIR / "CheckShippingFeatureSymbols.py",
    SCRIPTS_DIR / "CheckStagedContent.py",
    SCRIPTS_DIR / "ImportAssetClosure.py",
    SCRIPTS_DIR / "MailboxViewer.py",
    SCRIPTS_DIR / "SummarizeBenchmark.py",
)


class BiA19CliToolingContractTest(unittest.TestCase):
    def test_ki165_to_167_tools_and_active_root_clis_parse_cleanly(self) -> None:
        root_pys = sorted(SCRIPTS_DIR.glob("*.py"))
        self.assertGreaterEqual(len(root_pys), 119)
        for path in (*KI_TOOL_FILES, *ACTIVE_ROOT_CLIS):
            self.assertTrue(path.is_file(), f"Missing CLI tool: {path}")
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


if __name__ == "__main__":
    unittest.main()

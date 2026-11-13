import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "Scripts"


class BiA14Ps1SyntaxContractTest(unittest.TestCase):
    def test_all_powershell_scripts_parse_cleanly(self) -> None:
        ps_files = sorted(SCRIPTS_DIR.rglob("*.ps1"))
        self.assertGreaterEqual(len(ps_files), 90)
        cmd = (
            "Set-Location '"
            + str(REPO_ROOT)
            + "'; $errs = @(); foreach ($f in Get-ChildItem 'Scripts' -Recurse -Filter '*.ps1') { "
            "$t = $null; $e = $null; "
            "[void][System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$t, [ref]$e); "
            "if ($e.Count -gt 0) { $errs += ($f.Name + ': ' + $e[0].Message) } }; "
            "if ($errs.Count -gt 0) { Write-Error ($errs -join '; '); exit 1 }"
        )
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"PS1 parse error(s): {res.stderr or res.stdout}")

    def test_editor_runners_and_mailbox_post_retain_finally_and_mutex_guards(self) -> None:
        runners = sorted((SCRIPTS_DIR / "Editor").glob("run_*.ps1"))
        self.assertGreaterEqual(len(runners), 55)
        for runner in runners:
            text = runner.read_text(encoding="utf-8", errors="ignore").lower()
            self.assertIn("finally", text, f"Missing finally cleanup block in {runner.name}")

        post_text = (SCRIPTS_DIR / "MailboxPost.ps1").read_text(encoding="utf-8")
        self.assertIn("Global\\OneBossFightMailbox", post_text)
        self.assertIn("UTF8Encoding($false)", post_text)


if __name__ == "__main__":
    unittest.main()

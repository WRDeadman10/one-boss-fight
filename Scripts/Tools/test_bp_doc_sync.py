"""BP-36..39 (C, implementer; Queue BP batch 8): keep the tool documentation in sync with the tool files (static only).

  1. Every classified Scripts/Tools file (ALLOWLIST, NO_RUN and LIBRARIES from test_bp_cli_smoke) has a row in the
     Scripts/Tools/README.md table, and the table has no row for a file that does not exist.
  2. Every such tool is mentioned in Documentation/Boss/TOOLS.md (usage section or the BP-37 index).
  3. Each README row's purpose is non-empty.
No tool is imported or executed; the two Markdown files are read as text (read-only).
"""
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import test_bp_cli_smoke as smoke  # noqa: E402

TOOLS = sorted(set(smoke.ALLOWLIST) | set(smoke.NO_RUN) | set(smoke.LIBRARIES))
README = (HERE / "README.md").read_text(encoding="utf-8")
TOOLS_MD = (REPO / "Documentation" / "Boss" / "TOOLS.md").read_text(encoding="utf-8")
ROWS = dict(re.findall(r"^\|\s*`([a-z0-9_]+)\.py`\s*\|\s*(.*?)\s*\|\s*$", README, re.M))


class DocSync(unittest.TestCase):
    def test_every_tool_has_a_readme_row(self):
        self.assertEqual([t for t in TOOLS if t not in ROWS], [])

    def test_no_stale_readme_rows(self):
        self.assertEqual(sorted(r for r in ROWS if not (HERE / f"{r}.py").is_file()), [])

    def test_readme_purposes_are_non_empty(self):
        self.assertEqual(sorted(r for r, purpose in ROWS.items() if not purpose.strip()), [])

    def test_every_tool_is_mentioned_in_tools_md(self):
        missing = [t for t in TOOLS if not re.search(r"\b%s(\.py)?\b" % re.escape(t), TOOLS_MD)]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()

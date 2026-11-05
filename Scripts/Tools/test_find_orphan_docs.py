#!/usr/bin/env python3
"""Tests for find_orphan_docs.py."""

import datetime
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from find_orphan_docs import find_orphans, is_recovery_or_backup, classify_category


class TestFindOrphanDocs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

        # Create basic directory structure
        (self.root / "Documentation").mkdir(parents=True)
        (self.root / "Documentation" / "Boss").mkdir(parents=True)
        (self.root / "Docs" / "BossCombatReview" / "Execution" / "EvidenceRun").mkdir(parents=True)
        (self.root / "Scripts").mkdir(parents=True)
        (self.root / "Source").mkdir(parents=True)

        # Create active core doc
        (self.root / "Documentation" / "PROJECT_STATE.md").write_text(
            "References ActiveFile.md and sub/referenced.patch\n", encoding="utf-8"
        )
        (self.root / "CLAUDE.md").write_text("Root guide\n", encoding="utf-8")

        # Set fixed past mtime
        self.past_time = datetime.datetime(2026, 11, 2, 12, 0, 0).timestamp()
        self.cutoff = datetime.datetime(2026, 11, 4, 23, 59, 59).timestamp()
        self.future_time = datetime.datetime(2026, 11, 5, 12, 0, 0).timestamp()

    def tearDown(self):
        self.tmp.cleanup()

    def _create_file(self, rel: str, content: str = "Test content", mtime: float | None = None):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        if mtime is None:
            mtime = self.past_time
        os.utime(p, (mtime, mtime))
        return p

    def test_finds_unreferenced_old_document(self):
        self._create_file("Documentation/Boss/TrulyOrphan.md", "Lonely doc")
        orphans = find_orphans(self.root, self.cutoff)
        paths = [o["path"] for o in orphans]
        self.assertIn("Documentation/Boss/TrulyOrphan.md", paths)

    def test_excludes_referenced_by_path_or_filename(self):
        self._create_file("Documentation/ActiveFile.md", "Active doc")
        self._create_file("Documentation/sub/referenced.patch", "Active patch")
        orphans = find_orphans(self.root, self.cutoff)
        paths = [o["path"] for o in orphans]
        self.assertNotIn("Documentation/ActiveFile.md", paths)
        self.assertNotIn("Documentation/sub/referenced.patch", paths)

    def test_excludes_referenced_by_scripts_or_source(self):
        self._create_file("Scripts/some_script.py", "import doc: CustomAudit.md")
        self._create_file("Documentation/CustomAudit.md", "Custom audit")
        orphans = find_orphans(self.root, self.cutoff)
        paths = [o["path"] for o in orphans]
        self.assertNotIn("Documentation/CustomAudit.md", paths)

    def test_excludes_raw_evidence_directories(self):
        # A directory with a .log or evidence_sha256.txt
        evidence_dir = "Docs/BossCombatReview/Execution/EvidenceRun"
        self._create_file(f"{evidence_dir}/run.log", "log data")
        self._create_file(f"{evidence_dir}/unreferenced_notes.txt", "notes")
        orphans = find_orphans(self.root, self.cutoff)
        paths = [o["path"] for o in orphans]
        self.assertNotIn(f"{evidence_dir}/unreferenced_notes.txt", paths)

    def test_excludes_recovery_and_backup_files(self):
        self._create_file("Documentation/TASKS_backup_2026.md", "backup")
        self._create_file("Docs/pre_state.txt", "state")
        self._create_file("Docs/recovery_notes.md", "recovery")
        orphans = find_orphans(self.root, self.cutoff)
        paths = [o["path"] for o in orphans]
        self.assertNotIn("Documentation/TASKS_backup_2026.md", paths)
        self.assertNotIn("Docs/pre_state.txt", paths)
        self.assertNotIn("Docs/recovery_notes.md", paths)

    def test_excludes_files_newer_than_cutoff(self):
        self._create_file("Documentation/Boss/FreshDoc.md", "fresh", mtime=self.future_time)
        orphans = find_orphans(self.root, self.cutoff)
        paths = [o["path"] for o in orphans]
        self.assertNotIn("Documentation/Boss/FreshDoc.md", paths)

    def test_excludes_core_active_docs_themselves(self):
        orphans = find_orphans(self.root, self.cutoff)
        paths = [o["path"] for o in orphans]
        self.assertNotIn("CLAUDE.md", paths)
        self.assertNotIn("Documentation/PROJECT_STATE.md", paths)

    def test_helper_recovery_check_and_category_classification(self):
        self.assertTrue(is_recovery_or_backup("Docs/current_log.txt"))
        self.assertTrue(is_recovery_or_backup("Docs/backup_file.md"))
        self.assertFalse(is_recovery_or_backup("Documentation/Boss/OldAudit.md"))
        self.assertEqual(classify_category("Docs/BossCombatReview/ExistingBossAudit/01.md"), "Legacy ExistingBossAudit")
        self.assertEqual(classify_category("Docs/BossCombatReview/Reference/01.md"), "Legacy Combat Reference")
        self.assertEqual(classify_category("Documentation/AG/REPORT_12.md"), "Archived Briefs & Reports")


if __name__ == "__main__":
    unittest.main()

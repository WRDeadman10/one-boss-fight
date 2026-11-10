"""Synthetic duplicate and gap checks for append-only mailbox headers."""
from pathlib import Path
import tempfile
import unittest

from Scripts.Tools.check_mailbox_ids import audit


class MailboxIdAuditTests(unittest.TestCase):
    def test_contiguous_party_ids_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            mailbox = Path(temporary) / "mail.md"
            mailbox.write_text("### [C-1] x\n### [C-2] y\n### [X-1] x\n### [A-1] a\n", encoding="utf-8")
            self.assertEqual(audit(mailbox), [])

    def test_duplicate_and_skipped_ids_are_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            mailbox = Path(temporary) / "mail.md"
            mailbox.write_text("### [X-1] x\n### [X-1] duplicate\n### [X-3] skipped\n", encoding="utf-8")
            issues = audit(mailbox)
        self.assertEqual(len(issues), 2)
        self.assertTrue(any("duplicate headers" in issue for issue in issues))
        self.assertTrue(any("skipped IDs 2..2" in issue for issue in issues))

    def test_missing_initial_id_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            mailbox = Path(temporary) / "mail.md"
            mailbox.write_text("### [A-3] a\n", encoding="utf-8")
            issues = audit(mailbox)
        self.assertTrue(any("A: skipped IDs 1..2" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main(verbosity=2)

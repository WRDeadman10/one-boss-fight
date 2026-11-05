from __future__ import annotations

import unittest

from mailbox_decision_digest import digest


class MailboxDecisionDigestTests(unittest.TestCase):
    def test_inclusive_range_selects_only_c_messages_and_keeps_complete_bodies(self) -> None:
        source = ("### [C-10] Claude -> Codex, 2026-11-01\nTASK: one\n"
                  "### [X-11] Codex -> Claude, 2026-11-01\nnot a decision\n"
                  "### [C-12] Claude -> Codex, 2026-11-02\nTASK: two\n"
                  "### [C-13] Claude -> Codex, 2026-11-03\noutside\n")
        result = digest(source, "C-10", "C-12")
        self.assertEqual(result["count"], 2)
        self.assertEqual([row["id"] for row in result["messages"]], ["C-10", "C-12"])
        self.assertEqual(result["messages"][0]["body"], "TASK: one")

    def test_rejects_reversed_or_non_c_ranges(self) -> None:
        with self.assertRaises(ValueError):
            digest("", "C-12", "C-10")
        with self.assertRaises(ValueError):
            digest("", "X-10", "C-12")


if __name__ == "__main__":
    unittest.main(verbosity=2)

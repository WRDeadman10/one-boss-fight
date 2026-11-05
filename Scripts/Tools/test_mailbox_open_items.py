from __future__ import annotations

import unittest

from mailbox_open_items import digest


class MailboxOpenItemsTests(unittest.TestCase):
    def test_last_n_window_and_explicit_signals_only(self):
        source = "".join(
            f"### [C-{i}] Claude -> Codex, today\n"
            + ("STATUS: ACCEPTED\n" if i < 3 else "STATUS: PARTIAL; WAITING ON OWNER\n")
            for i in range(1, 5)
        )
        result = digest(source, 2)
        self.assertEqual(result["window_messages"], 2)
        self.assertEqual([item["id"] for item in result["items"]], ["C-3", "C-4"])
        self.assertEqual(result["items"][0]["signals"], ["PARTIAL", "WAITING"])

    def test_no_status_signals_yields_empty_item_list(self):
        self.assertEqual(digest("### [X-1] Codex -> Claude\nCompleted.\n", 1)["items"], [])


if __name__ == "__main__":
    unittest.main()

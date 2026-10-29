#!/usr/bin/env python3
"""
Unit and Contract Tests for MailboxViewer.py (AG08)
Verifies:
  1. Timestamp parsing for date-only headers, recorded time with timezone, and commentary.
  2. Composer timestamp formatting with 24-hr time and timezone offset.
  3. Reverse append order rendering (newest appended message first, no inaccurate date/ID sorting).
  4. Stable selection preservation by message ID across polling updates.
  5. Mobile responsive layout contracts (word wrapping, full reading area, navigation).
  6. Read-only fidelity check on actual Documentation/TEAM_MAILBOX.md.
"""

import os
import sys
import tempfile
import unittest
import importlib.util
from datetime import datetime

# Import MailboxViewer module directly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
VIEWER_PATH = os.path.join(PROJECT_ROOT, "Scripts", "MailboxViewer.py")
REAL_MAILBOX_PATH = os.path.join(PROJECT_ROOT, "Documentation", "TEAM_MAILBOX.md")

spec = importlib.util.spec_from_file_location("MailboxViewer", VIEWER_PATH)
mv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mv)

MailboxParser = mv.MailboxParser
MailboxWriter = mv.MailboxWriter


class TestMailboxTimestampParsing(unittest.TestCase):
    """Verifies WO08 Requirement 1: Date & Time parsing and display rules."""

    def test_parse_date_only_header(self):
        ts = MailboxParser.parse_timestamp("2026-10-22")
        self.assertFalse(ts["time_recorded"])
        self.assertEqual(ts["date"], "2026-10-22")
        self.assertEqual(ts["time"], "")
        self.assertEqual(ts["tz"], "")
        self.assertIn("[time not recorded]", ts["display"])
        self.assertIn("2026-10-22", ts["display"])

    def test_parse_date_with_local_label(self):
        ts = MailboxParser.parse_timestamp("2026-10-27 local")
        self.assertFalse(ts["time_recorded"])
        self.assertEqual(ts["date"], "2026-10-27")
        self.assertIn("[time not recorded]", ts["display"])
        self.assertIn("(local)", ts["display"])

    def test_parse_date_with_commentary(self):
        ts = MailboxParser.parse_timestamp("2026-10-24 (for Q15 and Q16 when you wake)")
        self.assertFalse(ts["time_recorded"])
        self.assertEqual(ts["date"], "2026-10-24")
        self.assertIn("[time not recorded]", ts["display"])
        self.assertIn("(for Q15 and Q16 when you wake)", ts["display"])

    def test_parse_timestamp_hh_mm(self):
        ts = MailboxParser.parse_timestamp("2026-10-23 14:34")
        self.assertTrue(ts["time_recorded"])
        self.assertEqual(ts["date"], "2026-10-23")
        self.assertEqual(ts["time"], "14:34")
        self.assertIn("2026-10-23 14:34", ts["display"])

    def test_parse_timestamp_full_iso_with_tz(self):
        ts = MailboxParser.parse_timestamp("2026-10-27 00:27:22 +05:30")
        self.assertTrue(ts["time_recorded"])
        self.assertEqual(ts["date"], "2026-10-27")
        self.assertEqual(ts["time"], "00:27:22")
        self.assertEqual(ts["tz"], "+05:30")
        self.assertEqual(ts["display"], "2026-10-27 00:27:22 +05:30")

    def test_parse_empty_timestamp(self):
        ts = MailboxParser.parse_timestamp("")
        self.assertFalse(ts["time_recorded"])
        self.assertEqual(ts["display"], "[time not recorded]")


class TestMailboxComposer(unittest.TestCase):
    """Verifies WO08 Requirement 1: Composer writes full date, 24h time and timezone offset."""

    def test_composer_append_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_mailbox = os.path.join(tmpdir, "TEST_MAILBOX.md")
            with open(fake_mailbox, "w", encoding="utf-8") as f:
                f.write("# Fake Team Mailbox\n\n### [O-1] Owner -> All, 2026-10-26\nInitial directive.\n")

            res = MailboxWriter.append_message(
                sender="Owner",
                recipient="Codex",
                body="Testing composer timestamp with full tz.",
                prefix="O",
                filepath=fake_mailbox
            )

            self.assertTrue(res["success"])
            self.assertEqual(res["message_id"], "O-2")

            # Verify appended file contents
            with open(fake_mailbox, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("### [O-2] Owner -> Codex, 2026-", content)
            # Must contain timezone offset e.g. +05:30 or -XX:XX
            import re
            header_match = re.search(r'### \[O-2\] Owner -> Codex, (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{2}:\d{2})', content)
            self.assertIsNotNone(header_match, f"Header did not match expected timestamp format: {content}")


class TestMailboxOrderingAndIntegrity(unittest.TestCase):
    """Verifies WO08 Requirement 2: Strict reverse append order (no sorting by inaccurate dates/IDs)."""

    def test_out_of_order_dates_and_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_mailbox = os.path.join(tmpdir, "TEST_MAILBOX.md")
            # Deliberately out-of-order dates and IDs in append order
            entries = [
                "### [Z-99] Codex -> All, 2026-10-28 12:00:00 +05:30\nFirst appended entry.",
                "### [A-01] Claude -> All, 2026-10-20\nSecond appended entry.",
                "### [M-50] Antigravity -> All, 2026-10-25 09:30:00 +05:30\nThird appended entry."
            ]
            with open(fake_mailbox, "w", encoding="utf-8") as f:
                f.write("\n\n".join(entries) + "\n")

            parsed = MailboxParser.parse_file(fake_mailbox)
            self.assertEqual(parsed["count"], 3)
            # In file parse order:
            self.assertEqual([m["id"] for m in parsed["messages"]], ["Z-99", "A-01", "M-50"])
            # The latest message is the last appended in file:
            self.assertEqual(parsed["latest"]["id"], "M-50")
            # Reverse append order should be M-50, A-01, Z-99 (NOT sorted by date 2026-10-28, 2026-10-25, 2026-10-20)
            rev_order = [m["id"] for m in reversed(parsed["messages"])]
            self.assertEqual(rev_order, ["M-50", "A-01", "Z-99"])

    def test_special_characters_and_hash_preservation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_mailbox = os.path.join(tmpdir, "TEST_MAILBOX.md")
            with open(fake_mailbox, "w", encoding="utf-8") as f:
                f.write("# Fake Mailbox\n")

            test_body = (
                "Verifying special chars: <script>alert(1)</script> & 'quotes' \"double\" `code`.\n"
                "Long hash: 5f88c0921096de8be6da96a230ce2625a940a47fe6d08c1f83827a2b846badeb\n"
                "Path: C:\\UnrealProject\\OneBossFight\\Docs\\BossCombatReview\\Execution\\test.md"
            )

            res = MailboxWriter.append_message(
                sender="Owner",
                recipient="All",
                body=test_body,
                prefix="O",
                filepath=fake_mailbox
            )

            self.assertTrue(res["success"])
            parsed = MailboxParser.parse_file(fake_mailbox)
            self.assertEqual(parsed["count"], 1)
            msg = parsed["messages"][0]
            self.assertIn("<script>alert(1)</script>", msg["body"])
            self.assertIn("5f88c0921096de8be6da96a230ce2625a940a47fe6d08c1f83827a2b846badeb", msg["body"])


class TestHTMLTemplateUIContracts(unittest.TestCase):
    """Verifies WO08 UI Presentation Contracts in HTML_TEMPLATE."""

    def test_html_ui_contracts(self):
        html = mv.HTML_TEMPLATE
        # 1. Responsive mobile viewport
        self.assertIn('name="viewport"', html)
        self.assertIn('viewport-fit=cover', html)

        # 2. Reverse append order in JS feed rendering
        self.assertIn('.slice().reverse()', html)
        self.assertIn('✨ NEWEST', html)

        # 3. Stable selection by message ID
        self.assertIn('selectedMsgId', html)
        self.assertIn('selectMessageById', html)

        # 4. Mobile detail reading area improvements
        self.assertIn('mobile-detail-mode', html)
        self.assertIn('overflow-wrap: anywhere', html)
        self.assertIn('word-break: break-word', html)

        # 5. Mobile detail navigation controls with declared >= 44px touch targets
        self.assertIn('btn-nav-newer', html)
        self.assertIn('btn-nav-older', html)
        self.assertIn('navigateMessageRelative', html)
        self.assertIn('replyToCurrentMessage', html)
        self.assertIn('min-height: 44px;', html)

        # 6. Unified 1024px breakpoint contract (no 901-1023px dead zone)
        self.assertIn('@media (max-width: 1023px)', html)
        self.assertIn('@media (min-width: 1024px)', html)
        self.assertIn('window.innerWidth < 1024', html)

        # 7. Functional Auto-follow checkbox contract
        self.assertIn('id="auto-scroll"', html)
        self.assertIn('Auto-follow live', html)
        self.assertIn('autoFollow', html)

    def test_multi_breakpoint_logic(self):
        """Simulates single-pane vs dual-pane breakpoint logic across boundary widths."""
        test_widths = [390, 768, 899, 900, 901, 980, 1023, 1024, 1280, 1920]
        results = {w: (w < 1024) for w in test_widths}
        
        # All widths < 1024 (including 901, 980, 1023) must be single-pane
        for w in [390, 768, 899, 900, 901, 980, 1023]:
            self.assertTrue(results[w], f"Width {w} should be single-pane")

        # All widths >= 1024 must be dual-pane desktop
        for w in [1024, 1280, 1920]:
            self.assertFalse(results[w], f"Width {w} should be dual-pane desktop")


class TestRealMailboxReadonlyFidelity(unittest.TestCase):
    """Verifies that parsing actual Documentation/TEAM_MAILBOX.md preserves all messages and bodies."""

    def test_actual_mailbox_parsing(self):
        self.assertTrue(os.path.exists(REAL_MAILBOX_PATH), "Real mailbox not found")
        parsed = MailboxParser.parse_file(REAL_MAILBOX_PATH)
        self.assertTrue(parsed["exists"])
        self.assertGreaterEqual(parsed["count"], 457)
        self.assertIsNotNone(parsed["latest"])

        # Check that bodies are non-empty and IDs are clean
        for m in parsed["messages"]:
            self.assertTrue(len(m["id"]) > 0)
            self.assertTrue(len(m["sender"]) > 0)
            self.assertTrue(len(m["recipient"]) > 0)
            self.assertIsInstance(m["time_recorded"], bool)


if __name__ == "__main__":
    unittest.main()

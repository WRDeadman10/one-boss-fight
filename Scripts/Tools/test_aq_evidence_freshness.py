"""Fixtures for AQ evidence freshness and identity boundaries."""

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from Scripts.Tools.aq_evidence_freshness import classify_record


CUTOFF = datetime(2026, 11, 1, tzinfo=timezone.utc)
EXPECTED = {"expected_build": "BUILD-269", "expected_route": "legacy", "cutoff_utc": CUTOFF}


class AqEvidenceFreshnessContract(unittest.TestCase):
    def test_current_identity(self):
        row = {"build": "BUILD-269", "route": "legacy", "timestamp_utc": "2026-11-08T15:00:00Z"}
        self.assertEqual(classify_record(row, **EXPECTED), "CURRENT")

    def test_stale_identity(self):
        row = {"build": "BUILD-269", "route": "legacy", "timestamp_utc": "2026-10-31T23:59:59Z"}
        self.assertEqual(classify_record(row, **EXPECTED), "STALE")

    def test_missing_or_unqualified_identity(self):
        fixtures = (
            {},
            {"build": "BUILD-269", "timestamp_utc": "2026-11-08T15:00:00Z"},
            {"build": "BUILD-269", "route": "legacy", "timestamp_utc": "2026-11-08T15:00:00"},
            {"build": "BUILD-269", "route": "legacy", "timestamp_utc": "not-a-time"},
        )
        for row in fixtures:
            with self.subTest(row=row):
                self.assertEqual(classify_record(row, **EXPECTED), "MISSING_IDENTITY")

    def test_mismatched_build_or_route(self):
        for row in (
            {"build": "BUILD-268", "route": "legacy", "timestamp_utc": "2026-11-08T15:00:00Z"},
            {"build": "BUILD-269", "route": "data", "timestamp_utc": "2026-11-08T15:00:00Z"},
        ):
            with self.subTest(row=row):
                self.assertEqual(classify_record(row, **EXPECTED), "MISMATCH")

    def test_invalid_cutoff_is_rejected(self):
        row = {"build": "BUILD-269", "route": "legacy", "timestamp_utc": "2026-11-08T15:00:00Z"}
        with self.assertRaisesRegex(ValueError, "timezone"):
            classify_record(row, expected_build="BUILD-269", expected_route="legacy", cutoff_utc=datetime(2026, 11, 1))


if __name__ == "__main__":
    unittest.main()

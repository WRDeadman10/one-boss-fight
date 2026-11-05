# Queue V C076–C079 — comparator, receipt, registration, mailbox digest

Status: C076–C079 implemented and focused checks pass. Offline only; no Editor, build, or PIE run.

## C076 — bracketed state comparator regressions

The U-A04 false-PASS concern is already fixed in `Scripts/Tools/compare_encounter_parity.py` (C-897): bracketed values with health/posture/poise/damage/stamina/hp keywords remain numeric comparison tokens; sampled arrays remain WARN-only. Extended `test_compare_encounter_parity.py` to exercise all six state keywords, assert the 2000-to-1500 divergence is a mismatch, and assert those state values are not classified as volatile samples. The suite passes 28/28. Existing U-A04 source analysis: `Documentation/Boss/U_A01_U_A04_AUDIT.md`; current tests also retain a live shaped sample-list warning fixture.

## C077 — typed observable labels against a real log

The existing explicit alias maps `L8 perfect parry slow motion duration` to the check beginning `L8 real perfect parry contact starts` in `write_a4_parity_receipt.py`. Added a second test that parses the current BUILD-220 `pie_legend_t1/legacy/editor_raw.log`, checks that exact live label/status, and verifies the typed value lies inside its declared fixed range. This is an offline reader test against the retained live log, not a new PIE measurement. `test_a5_parity_driver_registration.py` passes 21/21.

## C078 — A5 registration refresh

`audit_a5_driver_registration.py` reports 31 receipt definitions, 41 scheduled RunDrivers rows, 32 A5 runner allowlist entries, and 31 checked receipt drivers with zero registration/minimum discrepancies. The 31 include Legend and its L8 typed-observable check. The refusal route is independently present in RunDrivers and the A5 runner. `pie_memory_soak` is an explicit A5 runner entry and has its own source driver, not a RunDrivers regression row. Added regression assertions for these special registrations. Audit tests pass 6/6. The full 31-row MATCH table is reproducible by running `python Scripts/Tools/audit_a5_driver_registration.py`.

## C079 — C-id mailbox decision digest

Added `Scripts/Tools/mailbox_decision_digest.py`: read-only CLI emits JSON for Claude C-messages in an inclusive C-id range, preserving each complete body and ignoring interleaved X/A messages as entries. Example: `python Scripts/Tools/mailbox_decision_digest.py C-900 C-928`. It defaults to `Documentation/TEAM_MAILBOX.md`, writes stdout unless `--output` is supplied, and refuses malformed or reversed bounds. Synthetic tests pass 2/2. No mailbox content is written or reordered.

## Focused validation

- `python Scripts/Tools/test_compare_encounter_parity.py`: 28 passed.
- `python Scripts/Tools/test_a5_parity_driver_registration.py`: 21 passed.
- `python Scripts/Tools/test_audit_a5_driver_registration.py`: 6 passed.
- `python Scripts/Tools/test_mailbox_decision_digest.py`: 2 passed.
- `python Scripts/Tools/audit_a5_driver_registration.py`: 31 receipt rows checked, zero issues.

# Queue_50 Batch 8: offline tool audit

Date: 2026-11-10. Scope: Queue_50 tasks 36–40. These tools operate on existing logs, evidence manifests, Markdown, and the append-only mailbox; no source assets or evidence files were modified.

## Implemented and checked

- Task 36, `Scripts/Tools/summarize_framework_log.py`: parsed real PIE logs from `B_LIVE_20261104b/com004_parried_phase080` and `com004_parried_phase200`; output per-token totals, decisions, accepted/parried/guarded outcomes, reported accepted hits, and per-card summaries.
- Task 37, `Scripts/Tools/check_evidence_sha256.py`: fixed UTF-8 BOM handling, which previously marked PowerShell-generated manifests malformed. Added a BOM fixture and changed `entries_checked` to count parsed hash rows.
- Task 38, `Scripts/Tools/compare_parry_runs.py`: added explicit total-hit counts while retaining timestamp-independent RESULT and outcome comparison. Compared the two real phase logs: run 080 reports 5 accepted / 2 parried / 39 hit rows; run 200 reports 3 accepted / 3 parried / 37 hit rows. Their RESULT and hit/outcome totals correctly differ.
- Task 39, `Scripts/Tools/check_doc_links.py`: existing fixtures pass; whole `Documentation` scan reports `broken_links=0`.
- Task 40, `Scripts/Tools/check_mailbox_ids.py`: added reporting for missing initial IDs as well as internal gaps and duplicates; synthetic fixtures cover contiguous, duplicate, internal-gap, and initial-gap cases.

## Current repository findings

- Evidence scan: 144 Claude `B_*` manifests, 2,255 parsed hash entries, and 10 hash mismatches. These are reported for review and were not rewritten:
  - `B_C1003_X1410/status.txt`
  - `B_C1030_TIER2/status.txt`
  - `B_C1072_AURASOCKET/status.txt`
  - `B_C1079_BOSSBLOCKS/status.txt`
  - `B_C1147_PARRYDIAG/status.txt`
  - `B_C1233_EMBERANNOT2/status.txt`
  - `B_C1235_EMBERA2/status.txt`
  - `B_C835_PARITY/run_parity.ps1`
  - `B_C970_X1370/status.txt`
  - `B_C978_X1380/status.txt`
- Mailbox ID scan: 3 historical gaps and no duplicate headers: X-21..X-50, A-215, and A-236..A-237. The append-only mailbox was not changed.
- Offline tool contracts: 12/12 pass across summary, compare, evidence-hash, mailbox-ID, and documentation-link fixtures. All five scripts pass `py_compile`.

The hash and mailbox reports are findings for Lead review; historical evidence and mailbox entries remain untouched.

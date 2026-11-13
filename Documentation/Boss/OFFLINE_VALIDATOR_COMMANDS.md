# Offline Validator Command Index

Local Python checks only. These commands do not launch Unreal, build, cook, run PIE, or establish packaged-game acceptance. Run from the repository root.

| Purpose | Command | Scope / limit |
|---|---|---|
| Check relative links under Documentation | `python Scripts/Tools/check_doc_links.py` | Inline Markdown links; does not resolve reference-style links or links outside Documentation. |
| Validate supported AA/AB/AT queue IDs and grouping | `python Scripts/Tools/validate_queue_batches.py` | Checks IDs 01–50, uniqueness/order, and batch grouping for AB/AT. It does not validate acceptance-column completeness or Queue BD. |
| Verify an evidence manifest's listed files and hashes | `python Scripts/Tools/verify_evidence_manifest.py <manifest>` | Offline read-only; optionally add `--require-bytes --verify-source-references --strict-membership`. Does not alter or certify evidence provenance. |
| Validate A5 paired receipt directory | `python Scripts/Tools/validate_a5_receipt_directory.py <receipt-root> --expected <ids.json>` | Offline read-only; expected file must be a unique JSON array of IDs. Checks receipt object/route and pair identity. |
| Run focused evidence-manifest contract tests | `python -m unittest Scripts.Tools.test_verify_evidence_manifest -v` | Temporary fixtures only; does not touch captured evidence. |
| Run focused A5 receipt contract tests | `python -m unittest Scripts.Tools.test_validate_a5_receipt_directory -v` | Temporary fixtures only. |
| Run focused queue validator tests | `python -m unittest Scripts.Tools.test_validate_queue_batches -v` | Current supported queues plus synthetic malformed fixtures. |

## Protected engine boundary

No command in this index performs a UHT/build/native suite/Shipping/Editor/PIE/cook/package run. Those remain Lead-owned and must follow the current mailbox order and C-1155 exactly: task-specific runner, both required locks, matching owner token, pinned DD27j suite hash where applicable, and ownership-safe release. Do not substitute generic `Rebuild.ps1`.

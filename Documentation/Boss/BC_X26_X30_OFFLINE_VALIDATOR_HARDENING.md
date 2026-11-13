# Queue BC Batch 6: X26–X30 offline validator and status audit

## X26 — validator inventory

Read-only inventory of representative project validators:

| Tool | Input / contract | Executes Unreal or writes evidence? |
|---|---|---|
| `Scripts/Tools/validate_a5_receipt_directory.py` | Receipt pair presence, driver identity, legacy/data route | No |
| `Scripts/Tools/verify_evidence_manifest.py` | Evidence pack bytes/hashes and optional source-log references | No |
| `Scripts/Tools/check_evidence_sha256.py` | Claude evidence hash lists | No |
| `Scripts/Tools/validate_queue_batches.py` | 50 ordered task IDs and five-row groups | No |
| `Scripts/Tools/validate_encounter_manifest.py` | G044 manifest schema/field contract | No |
| `Scripts/Tools/check_g044_cook_manifest.py` | Package manifest consistency | No |

This is a source inventory; no validator was run against Lead-owned raw evidence.

## X27 — malformed receipt input hotfix

`validate_a5_receipt_directory.validate` assumed decoded receipt JSON and `identity` were objects. A JSON array, scalar, or non-object `identity` could raise `AttributeError` instead of returning a validation issue. Added explicit top-level object and identity-object handling; malformed shapes now fail closed with bounded diagnostics. Added fixtures for non-object receipt and identity values.

## X28 — evidence reader path and identity tests

Added `Scripts/Tools/test_verify_evidence_manifest.py` for parent traversal and absolute paths in listed members, traversal in `source_log`, requirement that cited source logs are listed in the same manifest, and source SHA-256 identity mismatch. The verifier implementation already rejected these cases; this adds regression coverage without changing evidence files.

## X29/X30 — link and progress reconciliation

`python Scripts/Tools/check_doc_links.py .` reports `broken_links=0` across Documentation. TASKS, TEST_PLAN, and PROJECT_STATE now each record BC batches X01–X30 with separate gates: BC-X01 native tests authored but not run; X06–X25 static source/proof audits; X27–X28 offline validator hardening with focused tests run; X29 link scan; X30 status synchronization. No Lead-owned build, native suite, runtime, asset, or package gate is marked closed by this batch.

## Verification and limits

Focused command: `python -m unittest Scripts.Tools.test_validate_a5_receipt_directory Scripts.Tools.test_verify_evidence_manifest -v` — **9/9 passed**. `py_compile` passed for the changed validator and focused tests. Documentation links: **0 broken**. No full suite, Unreal, build, PIE, cook, evidence mutation, commit, or push.

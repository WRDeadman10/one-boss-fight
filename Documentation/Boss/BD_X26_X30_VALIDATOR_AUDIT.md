# Queue BD X26–X30 — Offline Validator Audit

**Scope:** source, test and documentation review plus a narrow invalid-UTF-8 regression fix. No captured evidence was edited. No Unreal, build, UHT, native suite, PIE, cook, asset, lock, commit, or push operation was performed.

## Findings by task

### BD-X26 — receipt validators and malformed shapes

`validate_a5_receipt_directory.py` catches I/O, Unicode and JSON decode failures and rejects non-object receipt roots, malformed `identity`, missing/contradictory IDs, duplicate pair IDs, and mismatched route arms. Its tests already include top-level array and malformed identity cases. The expected-ID CLI path rejects non-list, non-string/empty and duplicate IDs. No additional malformed top-level gap was found there.

`verify_evidence_manifest.py` already rejects a non-object or wrong-schema manifest and validates its `files` array entries. The manifest read path did not catch `UnicodeDecodeError`, so invalid UTF-8 escaped `verify()` as an exception. It now reports that input as a normal `cannot read manifest` issue; a focused temporary-fixture regression test covers the case.

### BD-X27 — traversal and identity

The manifest validator rejects absolute and parent-traversal entries, resolves symlinks before checking evidence-root containment, detects duplicate file entries, verifies listed payload sizes/hashes when supplied, and checks source references for containment, manifest membership, and hash identity when `--verify-source-references` is enabled. `--strict-membership` rejects unlisted files and symlinks. These are lexical and resolved-path checks on the current filesystem snapshot; they do not establish who captured a file or when.

### BD-X28 — queue IDs and acceptance fields

`validate_queue_batches.py` checks supported queue IDs for duplicates, missing/extra IDs and order; AB/AT additionally require ten numbered headings and five rows per batch. Its tests include duplicate, missing and grouping failures. It does not validate the acceptance column or support Queue BD's `BD-X` identifier pattern. This is a documented validator coverage boundary, not a claim that a queue currently fails acceptance.

### BD-X29 — Markdown link forms

`check_doc_links.py` scans `Documentation/**/*.md`, strips fenced and inline code, and resolves inline Markdown link targets (including angle-wrapped URLs). It skips external schemes, protocol-relative and fragment-only targets. It does not parse reference-style links, escaped brackets/parentheses comprehensively, or scan Markdown outside `Documentation`; zero reported broken links is therefore scoped to the forms and tree it parses.

### BD-X30 — command index

Added `OFFLINE_VALIDATOR_COMMANDS.md` with exact offline invocations and their scope, plus a clear boundary for Lead-owned engine verification.

## Verification

- `python -m unittest Scripts.Tools.test_verify_evidence_manifest Scripts.Tools.test_validate_a5_receipt_directory Scripts.Tools.test_validate_queue_batches -v` — 13 passed.
- `python Scripts/Tools/check_doc_links.py` — `broken_links=0`.
- Scoped `git diff --check` — clean; only line-ending normalization notices.

## Files

- `Scripts/Tools/verify_evidence_manifest.py`
- `Scripts/Tools/test_verify_evidence_manifest.py`
- `Documentation/Boss/OFFLINE_VALIDATOR_COMMANDS.md`
- `Documentation/Boss/BD_X26_X30_VALIDATOR_AUDIT.md`

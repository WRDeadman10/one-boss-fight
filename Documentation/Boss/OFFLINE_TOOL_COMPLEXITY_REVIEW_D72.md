# Offline tool large-input complexity review (D72)

Date: 2026-11-03. Static source review only; no benchmark or stress run was performed.

## Complexity observations

- Most scanners are linear in visited bytes/lines, with a final sort for deterministic output. `check_mailbox_ids.py` performs two mailbox reads and sorts unique IDs by party; the current mailbox has about 2,000 recognized headers, so this is a small bounded state set in the observed workspace, though there is no hard file-size limit.
- `check_shipping_guards.py`, `list_cvars.py`, `check_ki_references.py`, and related repository scans walk configured source/config trees and process each file's lines. Cost scales with tree size; no visited-file cap is applied.
- `audit_framework_schemas.py` intentionally performs several source/schema/log passes and uses repeated token/field lookups. This multiplies a handful of full scans rather than introducing a nested all-lines-by-all-lines comparison; its current validator inventory is 138 tokens and source tree is project-bounded.
- `asset_provenance.py` checks each supplied log line against each extracted asset-path literal (`O(log_lines × asset_literals × line_length)` worst case). The literal set is script-derived and normally small, but neither side is capped.
- JSON/log parsers such as `validate_baked_cards.py`, `evidence_summary.py`, `proof_report.py`, and `suite_log_report.py` hold decoded/parsed content or row lists in memory. `evidence_pack.py` copies files but then hashes each destination with `read_bytes()`, so peak memory can approach the largest copied file. There is no streaming/size cap.
- Diff tools build maps/sets and sort output (`O(n)` memory, usually `O(n log n)` comparisons). Duplicate checks are map-based; no obvious pairwise comparison over all test rows was found.

## Bounded-input assumptions and limits

Inputs are expected to be project documentation/source trees, retained editor logs, small evidence bundles, and baked-card JSON. The tools do not enforce those assumptions with maximum file sizes or row counts. Recursive scans can include unexpectedly large caller-supplied roots, and large raw logs/manifests may use substantial memory. No correctness or runtime threshold is claimed here; the report identifies scale-sensitive paths by inspection only.

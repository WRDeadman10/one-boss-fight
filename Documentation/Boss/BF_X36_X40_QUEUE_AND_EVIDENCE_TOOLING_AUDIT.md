# Queue BF Batch 8 — queue and evidence tooling audit (X36–X40)

Date: 2026-11-11  
Status: focused offline validation complete; no Unreal/build/package operation.

## X36–X37 — queue structure and malformed rows

`Scripts/Tools/validate_queue_batches.py` checks duplicate/missing/extra IDs and ascending 01–50 ordering for supported AA/AB/AT queues. It enforces ten batch headings and five rows per batch for AB/AT; AA uses fifth-row X-batch markers and its two special final rows. This validator does not cover the newer BF queue format. The prior table-row regex could silently accept an empty task cell or a short row. It now rejects supported-prefix rows with fewer than three nonempty cells, preserving AA/AB's three-column and AT's larger-table formats. Added empty-cell and short-row fixtures. `python -m unittest Scripts.Tools.test_validate_queue_batches -v`: **4/4 passed**.

## X38 — evidence manifest containment and symlinks

`verify_evidence_manifest.py` resolves listed payload paths and rejects absolute paths, `..`, and symlinks resolving outside the manifest root. Source references are strict-resolved and must remain inside the root, be listed, and match their hash. Strict-membership mode rejects any symlink under the evidence root and flags unlisted files. Existing tests cover absolute/traversal paths and source-reference listing/hash/traversal. Added an external symlink fixture, but Windows returned `ERROR_PRIVILEGE_NOT_HELD` when creating it, so the test is skipped on this host; the code path is source-reviewed, not fixture-verified here. Combined focused tests: **4 passed, 1 skipped** for this verifier.

## X39 — run receipt fields

Compared the BF-X16–X20 and BE-X26–X30 task-specific C-1155 runner sources and their small status/lock-result receipts (not the raw suite/build logs). Their status files record build/suite exits, test started/passed/failed counts, completion, DD27j manifest hash, and no-assets; the BE runner additionally records transient dry-run and S1/S2 checks. Lock release is in a separate `lock_result.txt` count. The runner's lock object records task, command ID, owner token, PID, UTC start, policy, and scope while locks exist, but that identity record is not retained in the evidence folder. The status receipt also lacks source revision, build target/version, and a binary hash. Therefore the current receipts prove their recorded checks, not a complete source-to-binary identity chain. Preserve these as explicit provenance gaps; no raw suite log was opened for this comparison.

## X40 — documentation links

Ran `python Scripts/Tools/check_doc_links.py` after the prior batch documentation edits: `broken_links=0`. This checks relative Markdown path existence under Documentation; it does not validate anchors, link semantics, or files outside the scanned Documentation tree.

## Disposition

BF-X36–X40 complete. Focused tests: queue validator 4/4; evidence manifest verifier 4 passed / 1 symlink fixture skipped. Documentation-link scan: zero broken links. No full suite, engine, build, package, asset, commit, or push operation. Continue BF-X41–X45.

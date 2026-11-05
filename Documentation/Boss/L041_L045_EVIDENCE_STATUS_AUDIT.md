# Queue L Batch 9 — evidence integrity and status audit

## L041 — evidence pack verifier

`verify_evidence_manifest.py` checks each listed path remains under the pack
root, verifies file hashes and optional byte counts. For the stricter Queue L
capture, it now supports:

```powershell
python -I Scripts/Tools/verify_evidence_manifest.py Saved/G044/runs/<run>/evidence_manifest.json --require-bytes --verify-source-references --strict-membership
```

`--verify-source-references` finds JSON `source_log`/`source_log_sha256` pairs,
requires the source log to resolve inside the pack, requires it to be listed in
the manifest, and hashes the retained bytes. No current selected-route evidence
pack exists to run this against.
`--strict-membership` also rejects payload files not listed by the manifest
(excluding the manifest itself and the conventional `evidence_sha256.txt`
companion). Strict mode rejects symbolic-link members because recursive
enumeration may not descend through directory symlinks and resolved aliases do
not prove pack membership.

## L042 — parity receipt completeness

The strict v2 builder requires captured run identity, selection, participants,
terminal/check data, and per-observable trial ID and source-log digest. The
comparator validates receipt identity and trial correspondence; its
`--verify-source-logs` option verifies the raw bytes. The builder validates
caller-supplied values but cannot prove they were measured. No receipt/log pack
exists, so no completeness pass is claimed.

## L043–L045 — project status and review

- TEST_PLAN, TASKS, PROJECT_STATE and the decision packet distinguish source,
  native automation, Editor, PIE, package, parity and performance evidence.
- KNOWN_ISSUES retains KI-182's missing selected-route content/PIE gates and
  KI-183's Shipping setter/content-callsite boundary.
- Batches are reported to Claude by X-message; review remains asynchronous and
  any rejection is handled as a hotfix next cycle. No current project status is
  promoted to feature/release completion.

The new verifier option was source-edited only; no pack exists to verify and no
tests, build or Unreal run was performed.

# Queue X X-C016-X-C019 — G044 numeric and parity audit

Date: 2026-11-06. Read-only review of current G044 manifests, source tables, saved parity receipts, and comparator behavior. No Editor, Unreal, build, or live parity rerun.

## X-C016 — typed G044 paths vs source defaults

Ran `compare_manifest_to_legacy_defaults.py` on `Saved/G044/encounter_manifest.json` with `Scripts/Tools/legacy_defaults_g044.json`. Current result: **424 leaves, 214 MATCH, 0 MISMATCH, 210 NOT-COMPARABLE**. All 424 row paths, statuses, manifest values, and legacy values matched the checked-in `D5_G044_LEGACY_DEFAULT_AUDIT.md`; current source citation excerpts were revalidated during the run. All NOT-COMPARABLE leaves remain player-definition leaves and are not evidence of parity.

The row content is current, but the report's recorded provenance hashes are stale: the manifest SHA matches (`148a6cee…`); report line 6 records defaults table `c0fefeb2…` while current is `5c3d7b0e…`; line 7 records audit tool `596eceb5…` while current is `fd8b1463…`. `D5_G044_LEGACY_DEFAULTS_EXPECTED.md:10` agrees with the census. Refreshing report metadata is a documentation follow-up; no report was rewritten in this audit.

## X-C017 — numeric source-token coverage and fixture

The defaults table has 102 scalar numeric legacy values plus two numeric fireball cooldown array elements. Static token extraction from each cited source excerpt found a matching numeric literal for all 104 values; there is no current numeric-token mismatch. This is source-token evidence only, not proof of runtime Blueprint CDO state; the 210 player rows remain NOT-COMPARABLE.

There is a synthetic false-pass gap: `compare_manifest_to_legacy_defaults.py` verifies that the cited source line still equals its stored excerpt, then compares the manifest value only to `legacy_value`. It does not bind numeric `legacy_value` to the numeric literal in the excerpt. A temporary fixture with the source line `float MaxHealth = 2000.f;`, a table legacy value of `1800.0`, and manifest value `1800.0` returns `MATCH`. The current table's 104 values independently match their cited tokens, but the checker cannot enforce that property against future drift. Existing focused tests pass 8/8 and do not exercise this counterexample.

## X-C018 — saved paired receipt identity and evidence hashes

Read-only scan of `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY` found 59 legacy/data receipt pairs. All eight shared identity fields match within every pair; all 59 route pairs are `legacy`/`data`. Where `identity.json` exists, its fields match the paired receipt identity. The pairs span historical build labels BUILD-219, -220, -221, -227, -229, -231, and -233; they are not one-build evidence. Verified 124 `evidence_sha256*.txt` manifests against their listed files: **0 hash/missing-file issues**. This confirms stored-file integrity and recorded identity consistency, not that a historical build ID is independently authentic.

## X-C019 — warning/typed-observable blind spot

**BUG:** `compare_encounter_parity.py:128-130,142-150` treats typed measurements as authoritative and skips check-message comparison/warnings. The existing fixture `test_compare_encounter_parity.py:312-320` sets equal PASS statuses, typed timing values 0.400 vs 0.427 (inside tolerance), and check messages `health 2000` vs `health 1500`; `compare()` returns no issues, while `_message_warnings()` also omits the differing health. This is a concrete health mismatch hidden by a passing typed timing comparison if no separate health observable is emitted. The intent to avoid comparing incidental prose is understandable, but gameplay fields carried only in `check_message` need a warning or explicit typed field. The focused comparator suite passes 30/30 while encoding this behavior; no hotfix was applied as this batch is review-only.

## Disposition

C016-C018 found no current row/value mismatch, no current numeric source-token mismatch, and no saved pair identity/hash inconsistency in the scanned corpus; they did find stale D5 provenance hashes and a validator gap demonstrated by the synthetic fixture. C019 has the concrete hidden-health counterexample above. No G044 inputs, pair receipts, logs, or comparator sources were changed.

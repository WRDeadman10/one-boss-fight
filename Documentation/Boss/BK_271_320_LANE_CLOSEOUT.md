# BK-271..320: 50-task lane closeout (10 batches of 5): offline tooling and caller resilience

Written by C (implementer) for X-2151 task 320, 2026-11-12. The lane was set by Codex (lead) in X-2122. The cadence: C implements, AG reviews each batch independently, and Codex reviews and hotfixes; C continues without waiting.

**How to read the columns:**
- **Lead**: Codex's disposition (X- posts).
- **AG**: the Antigravity review range and post, from mailbox headers.

This file reconciles existing records; it is not a new verification.

| # | Batch | Report | Test file (result) | Source change | Lead | AG |
|---|---|---|---|---|---|---|
| 1 | BK-271..275 | `BK_271_275_CALLER_FAILURE_SEMANTICS.md` | `test_bk271_275_caller_failure_semantics.py` (10) | O1 message fix in `inventory_editor_asset_writers.py` + `audit_editor_save_safety.py`; lead reworded it (X-2124) | accepted | AG-R121..R125 (A-867) |
| 2 | BK-276..280 | `BK_276_280_REPLACE_CALLER_FAILURES.md` | `test_bk276_280_replace_caller_failures.py` (4) | none | accepted (X-2128) | AG-R126..R130 (A-868) |
| 3 | BK-281..285 | `BK_281_285_EVIDENCE_PACK_PARTIAL.md` | `test_bk281_285_evidence_pack_partial.py` (6) | none | accepted (X-2130) | AG-R131..R135 (A-869) |
| 4 | BK-286..290 | `BK_286_290_EVIDENCE_PACK_SOURCE_RACE.md` | `test_bk286_290_evidence_pack_source_race.py` (5) | none | accepted (X-2132) | AG-R136..R140 (A-870) |
| 5 | BK-291..295 | `BK_291_295_REPLACE_CALLER_EARLY_FAULTS.md` | `test_bk291_295_replace_caller_early_faults.py` (5) | none | accepted (X-2135) | AG-R141..R145 (A-871) |
| 6 | BK-296..300 | `BK_296_300_POST_PREFLIGHT_COLLISIONS.md` | `test_bk296_300_post_preflight_collisions.py` (3) | none | accepted (X-2138) | AG-R146..R150 (A-872) |
| 7 | BK-301..305 | `BK_301_305_OUTPUT_INPUT_ALIASING.md` | `test_bk301_305_output_input_aliasing.py` (5) | alias guards in 4 replace writers (C); Source-subtree containment in `make_source_manifest.py` (**lead** hotfix, X-2141) | accepted after the hotfix (X-2143) | AG-R151..R155 (A-873; hotfix re-check A-874) |
| 8 | BK-306..310 | `BK_306_310_ALIAS_NORMALIZATION.md` | `test_bk306_310_alias_normalization.py` (4, 1 symlink skip) | none | accepted (X-2147) | AG-R156..R160 (A-875) |
| 9 | BK-311..315 | `BK_311_315_ALIAS_EDGES.md` | `test_bk311_315_alias_edges.py` (5) | none | accepted (X-2151, X-2153) | AG-R161..R165 (A-876) |
| 10 | BK-316..320 | `BK_316_320_ALIAS_GUARD_MATRIX.md` + this file | `test_bk316_320_lane_static_checks.py` (5) | none | accepted (X-2155) | AG-R166..R170 clean (A-877) |

## Outcome

- **Fixed:**
  - **O1** (a false "existing" message);
  - **input destruction through output aliasing** in 4 report writers (3 of them had exited 0);
  - the **manifest self-inclusion under Source/** (lead).
- **Verified fail-closed, no change:**
  - replace-caller faults at `fsync`, `fdopen` and `replace`;
  - evidence_pack partial publication and source races;
  - post-preflight collisions;
  - path-normalization, hard-link and junction aliases;
  - `samefile` failures.
- **Totals:** 47 focused tests for BK-271..315 (1 host skip), plus 5 static tests for BK-316..320.

## Residual limitations

These are reconciled in `BK_316_320_ALIAS_GUARD_MATRIX.md` §BK-319:
- Windows-only, with no POSIX run;
- symlink aliases unverified (no privilege);
- `samefile` failures injected only;
- generic alias message and exit-style parity left as lead options;
- `token_coverage` exit-1 overload;
- partial roots need manual cleanup;
- **no global `git diff --check` clean claim** (pre-existing whitespace in unrelated files).

No production data, lock, pack, asset, Unreal, build, PIE, commit or push in any batch. X-1991 remains open.

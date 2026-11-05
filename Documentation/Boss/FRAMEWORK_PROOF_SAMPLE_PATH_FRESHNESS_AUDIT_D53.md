# FrameworkProof sample-path freshness audit (Queue D D53)

## Reconciliation

Read `Documentation/Boss/FRAMEWORK_SCHEMA_SAMPLE_BUNDLE_S133.json` without rewriting it and checked every record against the current checkout and validator. The manifest has 138 entries for 138 current schema tokens: all 133 `real_log` paths exist, each stored line number points to the exact recorded sample text, and each sample still passes the current validator under its recorded token. The other five records have `source=no_real_sample` and null path/line/sample fields. Result: 133 verified sample records, five explicit unsampled records, zero mismatches.

The five unsampled tokens are `attack_row_refused`, `pending_hit_refused`, `strafe_budget_exhausted`, `strafe_budget_restarted`, and `strafe_stuck`. They remain labeled as evidence gaps, not substituted with synthetic examples. This agrees with the current D52 schema audit.

## Freshness limits

This check establishes that the manifest's cited files/lines/text remain present and valid against the current validator. It does not establish that the sample still demonstrates correct feature behavior, that it is the newest or most representative occurrence, or that the schema captures all semantic constraints. The manifest records first real samples from its generation; it was not regenerated or mutated. Read-only Python verification only; no tests, build, or Unreal run.

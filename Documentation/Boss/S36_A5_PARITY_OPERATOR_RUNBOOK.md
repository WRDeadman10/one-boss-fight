# S36 — A5 parity pair operator runbook

This page separates live pair execution from receipt comparison. The live runners check that each arm reaches its registered check threshold; `summary.md` is not itself a legacy-versus-data comparator report.

## 1. Review the 31-pair plan

From the project root, use a new, unused output root and list the commands first:

```powershell
$outRoot = 'Saved\A5ParityNightly\Nightly-YYYYMMDD-HHMMSS'
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityNightly.ps1 -OutRoot $outRoot
```

The default is dry-run. It prints all registered drivers and does not create the output root. When the Editor owner is ready to run, add `-Execute` to the same command. The runner launches two fresh Editor processes per pair (legacy then selected-data), writes per-arm logs and updates `summary.md` after each driver. It continues after pair failures and returns nonzero if any pair failed.

For one driver, the lower-level command is:

```powershell
$pairOut = 'Saved\A5ParityNightly\Single-YYYYMMDD-HHMMSS\pie_a4_low_sweep'
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityPair.ps1 -Driver pie_a4_low_sweep -OutRoot $pairOut
```

`-OutRoot` must not already exist. `-Driver` must be one of the 31 registered names in `RunA5ParityPair.ps1`. Only `pie_player_death_reset` accepts `-DeathResetRepetitions 3`; both arms receive the same value. These commands launch Unreal and are operator procedures, not offline checks.

## 2. Read the pair result

The live runner's `PASS <driver> <arm> <passed>/<total>` means that arm's terminal marker was found, all observed checks passed, and its total met the driver's registered minimum. The nightly `summary.md` records these per-arm results. It does **not** prove matching identity or compare gameplay observables.

For each arm, provide the closed complete log, an identity JSON with the eight required identity fields, a unique run ID, and a new receipt path. Repeat with route-appropriate evidence for legacy and data:

```powershell
python Scripts/Tools/write_a4_parity_receipt.py --log LEGACY_EDITOR_LOG --identity LEGACY_IDENTITY.json --run-id LEGACY_RUN_ID --out LEGACY.json
python Scripts/Tools/write_a4_parity_receipt.py --log DATA_EDITOR_LOG --identity DATA_IDENTITY.json --run-id DATA_RUN_ID --out DATA.json
```

Despite the historical filename, this receipt writer accepts every registered A5 driver. It derives fields only from explicit driver capture messages and refuses unknown drivers or existing receipt outputs; it does not infer missing facts.

To compare closed legacy/data receipts, use:

```powershell
python Scripts/Tools/compare_encounter_parity.py LEGACY.json DATA.json --verify-source-logs --report-json PARITY_REPORT.json
```

Receipts must be separate, complete v2 files with matching run identity except route/run ID; `--verify-source-logs` verifies each cited raw-log path and SHA-256. The report output must be a new path and must not overwrite either receipt or source log. Exit 0 is PASS; exit 1 is FAIL; exit 2 is INCONCLUSIVE. Preserve the raw logs, receipts, report and exact command together.

## 3. Classify comparator warnings

- **D6b deterministic message checks:** status and scenario identity must match. Volatile pointer/object-instance suffixes are stripped; remaining text and numeric-token count must match. Numeric tokens use absolute tolerance `2/60 s` OR relative tolerance `10%`. Typed comparisons take precedence where defined. A warning is diagnostic text, not a waiver for a failed typed or exact field.
- **D6c sampled observations:** bracketed frame-sample series and sample-count deltas are WARN rows because sampling/completion boundaries can vary. Preserve the full messages. Values promoted to typed per-trial observables remain exact where specified; unmatched trials are INCONCLUSIVE.
- **D6d declared stochastic observations:** only named free-fight C7/R5 counts and the six natural-soak checks use scenario-run/threshold parity and retain raw values as WARN. Both arms must meet the same authored driver condition. Scripted soak checks remain deterministic.
- **O4 boundary cases:** A4 S9 roll at 0.40 s and P06 `world_hits` are WARN-stochastic based on the paired run history. Keep P06 trial IDs, `hits`, and `iframe_passes` exact. The S9 jump-at-0.05 s discrepancy was closed separately by two matching BUILD-221 pairs.
- **Typed timing/rate values:** values must remain inside their authored range; `timing_seconds` uses the comparator's `2/60 s` absolute tolerance and `rate_ratio` uses `0.01`. Aggregate count fields remain exact unless explicitly covered by an accepted rule above.

Never relabel an unexplained FAIL as WARN. If a row does not match one of these declared categories, keep it FAIL or INCONCLUSIVE and send the raw evidence for review. A5's Lead-reported 31/31 matrix result is parity evidence; it does not close A7 release gates.

The companion packaging regression test, `Scripts/Tools/test_make_bench_kit_dependencies.py`, inspects every script in `MakeBenchKit.ps1`'s copy manifest and fails when a literal `Import-Module` or `Join-Path $PSScriptRoot` target is absent from that manifest. It passes 2/2 locally; the full `Scripts/Tools` suite passes 185 tests with one skip.

Sources: `Scripts/MakeBenchKit.ps1`, `Scripts/RunBenchmark.ps1`, `Scripts/RunA5ParityNightly.ps1`, `Scripts/RunA5ParityPair.ps1`, `Scripts/Tools/write_a4_parity_receipt.py`, `Scripts/Tools/compare_encounter_parity.py`, `Documentation/Boss/P15_A7_PARITY_SUMMARY_DRAFT.md`, and C-857–C-865/C-885.

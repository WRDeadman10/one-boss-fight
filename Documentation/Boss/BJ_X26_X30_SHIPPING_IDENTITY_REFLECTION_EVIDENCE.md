# Queue BJ Batch 6 — Shipping identity and reflection evidence

Date: 2026-11-11. Static inspection only; no checker, binary scan, test, build, UHT, package, smoke, or Unreal operation was run.

## BJ-X26 — Current staged-file inventory

Read-only filesystem inspection of `Saved/StagedBuilds_Shipping/Windows` found:

| Artifact | Bytes | Last write UTC |
|---|---:|---|
| `OneBossFight.exe` | 346,624 | 2026-11-06 06:35:55Z |
| `OneBossFight/Binaries/Win64/OneBossFight-Win64-Shipping.exe` | 148,851,200 | 2026-11-06 06:34:32Z |
| `Manifest_UFSFiles_Win64.txt` | 1,432,790 | 2026-11-06 06:36:16Z |
| `Manifest_NonUFSFiles_Win64.txt` | 2,487 | 2026-11-06 06:36:15Z |
| `Manifest_DebugFiles_Win64.txt` | 362 | 2026-11-06 06:36:16Z |
| `OneBossFight/Content/Paks/OneBossFight-Windows.pak` | 10,754,310 | 2026-11-06 06:35:57Z |
| `OneBossFight/Content/Paks/OneBossFight-Windows.ucas` | 3,255,482,288 | 2026-11-06 06:36:14Z |
| `OneBossFight/Content/Paks/OneBossFight-Windows.utoc` | 1,733,945 | 2026-11-06 06:36:14Z |
| `OneBossFight/Saved/BuildStamp.txt` | 40 | 2026-11-06 07:12:40Z |

Stamp content: `OBF-SHIPPING-20261106T071240Z-ac05f0da`. A prior Queue BI report stated the root launcher was missing; this reread finds it present. The reason for that discrepancy is unknown. No hash, source-tree identity, UAT log, build command, map/route identity, or artifact-to-build binding was established. A stamp and timestamps are metadata, not package provenance.

## BJ-X27 — Shipping reflection boundary

The current source receipts `BE_X21_X25_SHIPPING_REFLECTION.md` and `BF_X11_X15_SHIPPING_REFLECTION.md` enumerate test-only reflected hooks guarded by `WITH_EDITORONLY_DATA` and production reflected APIs intentionally retained. Their contracts and Development build do not prove Shipping UHT output or the packaged `UClass` function table. Lead evidence still needs a Shipping UHT log and a same-build cooked/runtime reflection dump showing the test hooks absent and required production APIs present.

## BJ-X28 — Package provenance chain

`Scripts/Package.ps1` selects separate default Development/Shipping stage roots and cooks `/Game/OneBossFight/Levels/L_SevarogArena`; an explicit `-StageDir` can override the root. The current directory inventory does not connect its payload to HEAD/source hashes, UE version, target, exact UAT invocation/exit/log, cooked map/route/config, or an accepted package ID. The Shipping stamp itself records only its formatted config/time/id. Lead's package intake should bind those inputs, resolved root, launcher/config binary, all manifests and payload hashes, and logs to one build ID.

## BJ-X29 — Scan and smoke input scope

`Scripts/CheckShippingBinary.py` scans the configuration binary for `rpg.Debug` and `LogRPGDebug`; `Scripts/CheckShippingFeatureSymbols.py` scans for `rpg.Art.Tier2`, `BuildStamp.txt`, and `DEVELOPMENT BUILD`. Both require exact executable path/hash and captured exit/output for reproducibility. `Scripts/ShippingSmoke.ps1 -Execute` invokes Shipping packaging, `RunBenchmark.ps1` against the root launcher, then the feature-symbol scan against the inner binary. Its dry-run default is not smoke evidence. No scan or smoke was run in this batch.

## BJ-X30 — Disposition

Corrected the previous report's erroneous “launcher missing” finding in the BI-X36–X40 report, Queue BI, BI closeout, BI-X41–X45 report, TEST_PLAN, TASKS, and PROJECT_STATE; the correction was sent to Claude as X-1914. The stage's listed files are currently present, but provenance, Shipping UHT/reflection, binary scans, and smoke remain open Lead gates. No source/runtime change was justified. Continue with BJ-X31–X35 without waiting for review.

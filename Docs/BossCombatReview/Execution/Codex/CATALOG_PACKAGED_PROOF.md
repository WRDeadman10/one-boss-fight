# Catalog cold packaged proof

2026-10-26, X-T8. Procedure for Claude (sole build/editor/runtime owner). Codex only inspected files and ran the read-only packaged log checker against archived logs; no packaging/game launch.

## Current independently inspected evidence

| Artifact | Direct observation |
|---|---|
| Saved/package_dev_catalog.txt, tail | BUILD SUCCESSFUL, UAT ExitCode=0,106.69s. Not a Codex run. |
| Claude/Evidence/exports/packaged_dev_data_run.log | SHA256 `9e0ec4998d3558a179f094435f7e9de470a459983259f0f22a3b1be89ee114a8`; line235 Development,237 `-nosound -log`;847 `epoch=CC899CA24B0A361B00B354829A3CAE7F source=data reason=`. |
| packaged_dev_legacy_run.log | SHA256 `8e54909101db5c3ede561dd718a68d119a1654c13ffc8cb26c6a0891dce10296`; command line forces `-ini:Engine:[SystemSettings]:rpg.CatalogSource=legacy`; separate epoch `8EAD504F42E77DD876AC79B23CF3B5D3 source=legacy`. |
| Both archived runtime logs |19 `LogMaterial: Error:` each, zero matching fatal lines. Same error count is consistent with common existing material problem, NOT proof of full visual parity or independent proof of KI080 root cause. CheckPackagedLog still returns FAIL. |
| Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt:3507 onward | Seven catalog uasset names present (and associated uexp). This is content inclusion, not runtime source selection by itself. |

**Development cold complete-data publication witnessed.** FContext only publishes candidate after complete Compile succeeds, so source=data is stronger than a catalog pathname existing. Does not prove all three builds equipped in this packaged session; runtime log has no per-build full-equipment proof. Do not mark whole packaged quality gate PASS while material checker fails. Shipping same-path runtime provenance remains unproved.

## Preconditions / pinning

Close editor before building. Record HEAD/dirty list, source/config/script hashes, seven original catalog asset hashes, current binary and baseline gate pin. Do not reset user's work, rename/delete assets or reauthor catalog during proof. Package.ps1 cooks only L_SevarogArena, runs UAT build/cook/stage/pak into Saved/StagedBuilds. It does not take a separate output path parameter: archive prior evidence and explicitly preserve needed stages before another configuration replaces stage output. No automatic cleanup/deletion is prescribed here.

For each launch: process tree must be absent beforehand, runtime log path and prelaunch hash/mtime pinned, new run log copied to a NEW versioned evidence name immediately afterward. A hot editor or reused PIE epoch cannot supply the witness. No need to clear machine DDC to demonstrate process-cold asset load; call that a distinct cook-cache experiment if desired.

## Exact Development recipe

Run from `C:\UnrealProject\OneBossFight` (Claude only):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Package.ps1 -Configuration Development
python -I Scripts/CheckStagedContent.py --manifest Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/PackagedSmoke.ps1 -Seconds 30 -ExePath C:\UnrealProject\OneBossFight\Saved\StagedBuilds\Windows\OneBossFight.exe
```

Capture each command output/exit independently (a pipeline's last success must not conceal an earlier failure). PackagedSmoke launches launcher with -nosound -log, requires liveness, stops actual process tree including game child, then checks fresh runtime log. It accepts no catalog-mode argument. Its result may FAIL on known materials; do not modify checker or ignore errors silently.

Use its actual discovered runtime log path. Then:

```powershell
Select-String -LiteralPath <fresh-runtime-log> -Pattern 'LogRPGCatalog|catalog unavailable|data required|Failed to load|Failed to find|Fatal error'
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/CheckPackagedLog.ps1 -CookLog <saved-UAT-output> -RuntimeLog <fresh-runtime-log>
Select-String -LiteralPath Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt -Pattern 'OneBossFight/Data/Catalog/DA_'
```

Angle-bracket placeholders MUST be replaced by captured absolute paths, not typed literally. Expected selected epoch: `LogRPGCatalog: Display: epoch=<nonempty new guid> source=data reason=`. Fail the catalog claim on `source=legacy`, `COMPLETE legacy compatibility fallback`, `data required: initialization failed`, unresolved catalog dependencies or no current epoch witness. Auto mode without those lines is INCONCLUSIVE, not success.

Require exactly these package names (case-insensitive manifest spelling): DA_CombatCatalog; DA_Build_Starter/Strength/Dex; DA_Weapon_Sword/Claymore/DualSwords under OneBossFight/Content/OneBossFight/Data/Catalog. Existing CheckStagedContent scans C++ literals, so its pass alone may omit indirect data-asset dependencies. Check all seven explicitly, plus runtime validator-loaded item/style/actor/ability closure.

### Optional strict-mode contrast, no asset mutation

Development only. For a separately logged launch through the same staged launcher, append `-ini:Engine:[SystemSettings]:rpg.CatalogSource=data` to -nosound -log. This is the same startup ini mechanism independently visible in the archived legacy contrast log. If scripting, use Start-Process -WindowStyle Hidden and explicit absolute launcher path; capture launch time/PID, child liveness, fresh log and terminate only that launched process tree. Existing PackagedSmoke has no Arguments parameter, so do not invent one. Do not reuse the legacy contrast log as a data proof. A fresh default-auto launch afterward must again publish data. Fixture-invalid tests remain Development-only and must be restored before baseline run.

### Expected content values / capability boundaries

Runtime selected data must still encode Starter->SwordCombatStyle/Sword, Strength->ClaymoreCombatStyle/Claymore, Dex->DualSwordCombatStyle/Dual Swords; original item/actor/ability full paths, icons, aliases and legacy slots0/1/2 unchanged. Pin actual asset authoring readback and compare with preimage RPGBuildRules rows; do not infer these fields just from one epoch log. Owner/Claude can use B + keys1/2/3 before waking and capture actual/chosen HUD/loadout evidence in separate fresh packaged sessions. If no existing non-Shipping packaged diagnostic exposes required full identities, record that evidence gap rather than invent a console getter or claiming UI proves class ancestry. Fourth fixture shares Sword; new-weapon art/complete coverage stays P8.

## Shipping: separate proof and real gap

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Package.ps1 -Configuration Shipping
python -I Scripts/CheckStagedContent.py --manifest Saved/StagedBuilds/Windows/Manifest_UFSFiles_Win64.txt
python -I Scripts/CheckShippingBinary.py Saved/StagedBuilds/Windows/OneBossFight/Binaries/Win64/OneBossFight-Win64-Shipping.exe
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/PackagedSmoke.ps1 -Seconds 30 -ExePath C:\UnrealProject\OneBossFight\Saved\StagedBuilds\Windows\OneBossFight.exe
```

Actual CheckShippingBinary only searches rpg.Debug/LogRPGDebug. It does NOT prove CatalogSource stripping, catalog selected source, live class closure or all debug symbols absent. PackagedSmoke correctly skips missing Shipping log and checks liveness/debug binary names: **that is not source=data proof**. Do not request LogRPGCatalog lines, test fixtures or CatalogSource console in Shipping; code compiles those switches/logging out.

Content presence + Development proof + identical Shipping source path is useful inference but not direct Shipping provenance. To establish it directly requires an owner-approved noninteractive read-only provenance mechanism (e.g. one startup report exposing selected epoch/source/schema/definition digests through an approved shipping-safe UI/attestation), or explicit owner acceptance of the weaker inference. Such a mechanism is NOT implemented or authorized by this procedure, must not expose test mutation controls, and must not be smuggled into a docs-only task. **EDITOR/OWNER DECISION NEEDED only if direct Shipping provenance is required now.** Shipping tests may proceed with honest INCONCLUSIVE source selection, not a false catalog PASS.

## Acceptance record

Keep separate verdicts: build/cook; seven-package inclusion; Development cold data publication; three-build packaged functional witnesses; Shipping liveness/debug-off; Shipping source provenance; material quality; full performance/feel. Current evidence closes Development catalog loading only. No benchmark, full packaged duel, Shipping selection, missing-shader resolution or P8 canary is claimed here.

# WP-1 — step 1 implementation submission

2026-10-25, Codex. **NOT BUILT / NOT RUN; implementation submitted for Claude's independent review, not accepted or runtime-confirmed.** Owner's work order supersedes the former docs-only restriction for the claimed step1 files only. No assets authored, no engine invoked, no build/commit/push. Continue to WP2 without waiting.

## Assumptions

- No-context RPGBuildRules functions remain immutable legacy APIs, preserving enum99->Dex and pointer lifetime. New context-explicit overloads and actual runtime consumers use the game-instance epoch. Reversible by removing the owned integration delta; no global mutable facade.
- Legacy source permits the existing table fallback; `data` fails closed. Optional artwork degrades to existing text-only UI. No stat/timing/equip-sequence change intended.
- The Development fourth-build fixture shares the existing sword WeaponId; it tests non-injective build identity, NOT a genuinely new weapon capability or asset. The latter needs a resolved live pack-compatible weapon fixture/content and remains an explicit WP2/editor proof gap; no claim it is already proved.
- Reference validation checks full paths, loaded types, item ancestry, cooked roots and serialized item/actor/style references. The precise installed pack property layout is an EDITOR NEEDED readback, not inferred from class names. Strict-data failure is preferable to guessing a mismatched pack binding. Claude must review this validator against the actual objects before acceptance.

## Existing-file preservation and owned delta

Immediately before editing, all seven existing files matched Claude/DD1/preimages copies, including shared dirty Scripts/RunDrivers.ps1. No existing dirty change was discarded. Runner owned delta is exactly one row immediately after pie_builds:

`@{ N = 'pie_combat_catalog'; K = 'R'; Min = 66; T = 300 },`

Reverse only this row, not the whole file. The other six existing files had no reported dirty status at that observation. Rollback uses the checked preimages plus this owned delta, reconciled against any later concurrent edits; never checkout/reset/stash/clean. Newly created source/tests/scripts remain untracked until owner action.

## Self-review against D06/D08 and specifications

Line anchors describe this submission; later WP2 additions may move them. Every row is source inspection, never a pass claim.

| Requirement | Implementation anchor | Self-review / proof still needed |
|---|---|---|
| D06 R1, D08 reverse mapping; specv2:9/23/38 | RPGBuildLoadout.cpp:262/280/398/514/657/802; Catalog.cpp:42 | Stable IDs for parse/choice/equip/HUD, separate legacy view; fourth shared-style fixture. Fresh real selector/equip/reset/respawn proof WP2/Claude pending |
| D06 R2 epoch publication; v2:10; v3 A2/B | Catalog.h:107/124; Catalog.cpp:192/214; BuildLoadout.h epoch ref | Single-attempt context, GI ownership, explicit ForWorld; no global epoch stack. Simultaneous runtime GI/init/travel/GC proof pending |
| D06 R2 lifetime | Catalog.h FEpoch value arrays and strong leases; BuildLoadout.cpp:299 | Epoch owns strings; no asset-backed temporary pointer. Existing no-context FBuildEntry stays static. Reference lease/teardown tests WP2 |
| D06 R3 / D08 V2-R1 / v2:11/37/43 / v3 B,D1 | Catalog.cpp:192/214; both scripts | Auto/legacy/data startup modes, no live publication; no rename/delete. Test contexts explicit; no production invalid mode. Initial driver uses fresh sessions; late-cvar readback included |
| D06 R4 / v2:27-32 / v3 A3,D2 | BuildSelect.cpp:123/143/183/204/411/436; Catalog.cpp:54 | Registry-driven rows/icons and common geometry predicate; current legacy labels/suffixes retained. Real DPI/layout/keyboard/focus inspection pending |
| D06 R5 / D08 baseline | No new manifest generation or engine run | Existing pin preserved. Claude's clean baseline/supplement required before build/acceptance; editing scripts after a running gate has read them must be reflected in end-of-run drift |
| D08 V2-R2 / v3 C1/C2 | Catalog.cpp:159-181, GetCoverageLines | Coverage route exact/any/fallback and effective values; required-row policy rejects missing exact. Existing table not edited. Attack-kind/alias completeness needs WP2 tests and live table evidence |
| D08 whole closure / v3 C3 | Catalog.cpp:93/154-174; make_combat_catalog.py preflight | Full references/types/cook roots and wiring serialization, not registry base-name search. Pack layout compatibility not engine-validated; no semantic guarantee from export text alone |
| D08 V2-R3 / v3 D1 | Verified preimages; one runner row | Preserve dirty shared changes. Never restore whole shared file blindly |
| Specv2:1-8/15-23 | Catalog.h all definitions; Catalog.cpp; authoring helper | Seven asset definitions/creator, no asset created. Schema1 validated. Data remains invalid if required fields unresolved |
| Specv2:25-28/34-39 | Existing driver list unchanged plus new tests/driver | LegacyParity block tests old functions before/after; existing counts not reduced. Runtime parity assertions and extra cases WP2. No claim of unchanged behavior until Claude runs |
| Specv2:41-47 | Startup source policy and claimed files | All implementation writes inside claim. Driver row count bound finalized in WP2; invalid catalog never mixed per lookup |
| Specv2:49-53 / v3 A | CatalogSubsystem, Shipping guards, optional icon warning | GI lifetime, source controls compiled out Shipping, optional absent icons text-only; final canary must assert data source |
| v3 E/F | Docs only / work-order exception to author code now | Automation record previously reviewed, clean gate pending. Work order permits source authoring now; no build before Claude's baseline gate |

## API/header ledger (engine root C:/Program Files/Epic Games/UE_5.5/Engine/Source)

Read local declarations for the introduced integration APIs: UPrimaryDataAsset in Runtime/Engine/Classes/Engine/DataAsset.h; UGameInstanceSubsystem in Runtime/Engine/Public/Subsystems/GameInstanceSubsystem.h and Initialize/Deinitialize in Subsystems/Subsystem.h; UGameInstance::GetSubsystem and UWorld::GetGameInstance in Engine/Classes/Engine/GameInstance.h and World.h; FSoftObjectPath TryLoad/IsNull/GetLongPackageName/GetAssetName in Runtime/CoreUObject/Public/UObject/SoftObjectPath.h; TStrongObjectPtr construction/Get/IsValid in Runtime/Core/Public/UObject/StrongObjectPtrTemplates.h (forwarding StrongObjectPtr.h in CoreUObject); FProperty ExportText_InContainer and object reflection/TFieldIterator pattern in CoreUObject/Public/UObject/UnrealType.h; console variable GetValueOnGameThread in Core/Public/HAL/IConsoleManager.h; GConfig::GetArray in Core/Public/Misc/ConfigCacheIni.h; FParse::Value in Core/Public/Misc/Parse.h; FGuid NewGuid/ToString in Core/Public/Misc/Guid.h; FName lexical/ToString in Core/Public/UObject/NameTypes.h; UUserWidget::NativeTick and UWidget::GetCachedGeometry in Runtime/UMG/Public/Blueprint/UserWidget.h and Components/Widget.h. Existing widget construction/input/pack reflection APIs reuse the preimage's established paths, but still require Claude's compile review. No API was tested by reading a declaration.

Python authoring/driver follow existing make_weapon_table.py, pie_builds.py and pie_build_select.py APIs (AssetTools/DataAssetFactory/EditorAssetLibrary/SystemLibrary/GameplayStatics/Slate post-tick). No Python Unreal import/run occurred. Python bridge conversion for nested soft-reference arrays/USTRUCT fields requires editor verification.

## Exact commands for Claude (not executed)

After the clean gate has ended and its source/script drift is reconciled, close the editor before building:

```powershell
powershell -ExecutionPolicy Bypass -File Scripts/Rebuild.ps1 -Tests
python -I Scripts/run_in_editor.py Scripts/Editor/pie_combat_catalog.py
powershell -ExecutionPolicy Bypass -File Scripts/RunDrivers.ps1 -Only pie_combat_catalog,pie_builds,pie_build_select,pie_build_hud,pie_build_hyperarmor,pie_flask_hud
powershell -ExecutionPolicy Bypass -File Scripts/RunDrivers.ps1
```

The authoring helper is NOT in the commands above: asset creation is outside Codex authority and needs Claude's approved scheduling/scope, then a fresh-session strict-data readback. The driver deliberately fails if those assets are absent. Full source/class readback needed before its strict-data stages.

For a legacy preimage parity run, extract ONLY the `FRPGCatalogLegacyParityTest` block plus `Misc/AutomationTest.h` and the OLD RPGBuildRules.h include into an isolated test source in Claude's approved environment; it contains no new catalog dependency. Run `Automation RunTests OneBossFight.Catalog.LegacyParity`. Do not replace live workspace files to simulate the preimage. Assertions: invalid enum clamp, shield/twin/unknown/offbuild labels, defer/wait/failure suffixes, reserved off and invalid text preserving output. Existing103 builds checks remain the runtime baseline; WP2 extends the new integration driver.

## Validation performed

Preimage hash comparisons, source/diff inspection only. Scoped whitespace validation is repeated in WP2. An unscoped git diff check reported unrelated AG Markdown trailing spaces; those were left untouched. NOT BUILT / NOT RUN; no test/asset/cook/network/PIE acceptance. Claude is the independent code reviewer for this package.

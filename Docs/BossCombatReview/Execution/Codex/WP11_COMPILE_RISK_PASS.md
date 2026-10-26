# WP11 — compile-risk and static self-review

2026-10-25. **NOT BUILT / NOT RUN in Unreal.** This is a compiler-style read-through, not a compiler verdict. Step1 is already built by Claude (C114,40/40 pure automation); step2/3 remain outside the module. Do not build a half-promoted set. All live Source/Config/Scripts remain untouched this session.

## Scope read

Re-read complete step1 implementation: RPGCombatCatalog.h/.cpp; RPGBuildRules.h; RPGBuildLoadout.h/.cpp; UI/RPGBuildSelectRules.h; UI/RPGBuildSelect.h/.cpp; Tests/RPGCombatCatalogTests.cpp; make_combat_catalog.py; pie_combat_catalog.py; RunDrivers.ps1 (our owned row remains only the catalog entry). Read all8 staged C++ headers/translation units and both staged Python diagnostics, plus tracker seam specification. New code is excluded from UBT by directory placement, not a C++ preprocessor trick.

## Issues found and corrected

Paths below are under staged `Drafts/Source/OneBossFight/` unless explicitly live; line anchors refer to the current draft and may shift with later fixes.

| Issue | Fix / current anchor | Verification boundary |
|---|---|---|
| Live step1 macro else C2181 | Claude already added braces at live Player/RPGCombatCatalog.cpp:216-223 | Confirmed current source/build1 error/build2 automation summary; no overwrite |
| Unsupported TArray::CountByPredicate | Explicit loops in Player/RPGEncounterBinding.cpp:263/270 | Array.h searched; no reliance on nonexistent helper |
| Condensed JSON writer policy lacked direct include | Boss/RPGShadowCompare.cpp:12 includes Policies/CondensedJsonPrintPolicy.h; explicit Dom/JsonValue.h too | JsonWriter.h only brings Pretty policy; serializer template signatures read |
| Animation type could be incomplete at GetPathName | Explicit Animation/AnimSequenceBase.h in shadow cpp | Existing engine forward declarations no longer relied upon |
| Configure callback could reenter/change record array, leaving stored FRecord* dangling | Binding cpp303 guard + held Snapshot/OriginalKey; cpp337 reacquires record after register callbacks; strong leases for plan classes and unregistered components | Static fix; no rollback of registration side effects claimed |
| No production mesh/skeleton gate | Binding cpp69-80 loads/leases typed deps, cpp175 checks real mesh compatibility + GI epoch, explicit definition identity | Bone/pose/cook/retarget proof remains runtime/visual |
| Digest structure inconsistent between binding and timeline | Binding cpp13 validates64hex, same production timeline contract | Structural only, not hash attestation |
| Closed-event sorting mixed old/new clip positions | Timeline sort keeps Closed before new-playback edges, then loop ordinal/time/edge/id | Synthetic test added; not executed in Unreal |
| Unknown asset gap could be treated as continuous old playback | Playback adapter clears Last on unmatched/ambiguous metadata | Unknown active sample counted uncovered, not guessed variant |
| Idle sample counted as dropped record | OnSnapshot only increments unmatched count when active position exists | No misleading no-drop failure solely from idle |
| Current clip wrongly attributed to segment0 | Shadow cpp44 GetSegmentAtTime at actual position; CurrentSegmentAsset naming | Does not convert clip-local metadata to montage-local time automatically |
| No explicit report scope / missing damage semantic could falsely match | coverage_scope names uncovered slots/layers/blend-outs; no active metadata -> MISSING_METADATA; Collision/ActiveDamage accepted names | MATCH remains sampled active-state subset only |
| Notify overhang rejected pack metadata | Explicit clip policy retains RawEnd/ClampedFrom and provenance flag; begin>=length remains invalid | Projection not observed notify cleanup; raw overhang independently confirmed |
| Clipping policy could share a compiled key | FKey ProjectionPolicy included in equality/compiled artifact/report | Caller uses compiled key; no cache implementation claimed |
| Ambiguous loop wraps | Verified exactly-next ordinal + explicit bounds path only; unknown wraps still inconclusive | Native passive adapter cannot infer engine loop count; verified traversal feed remains open |
| Mock vs production key identity unclear | Automation-only SyntheticKey/CompileSyntheticParticipant; synthetic-domain flag reported | Production64hex unchanged, no asset-authored bypass |

## Includes, UHT, ABI and lifetime checks

- Reflected headers have generated include LAST: live catalog/loadout/selector; staged binding/shadow. Native structs/optional/shared pointers/TFunction/strong leases are NOT UPROPERTY/UFUNCTION parameters. Reflected fields use supported scalar/string/FName/FGuid/UObject/soft refs/arrays; definitions have GENERATED_BODY. No same-named reflected type found in live Source. Actual UHT pass remains Claude's job.
- Include graph is acyclic at header level: tracker seam -> shadow -> timeline -> binding -> catalog -> weapon table/attack kind; catalog includes build rules only in its CPP, not header. Shadow header forward-declares tracker; cpp includes full tracker. The seam and shadow cpp must be promoted TOGETHER or the new member won't exist. No new dependency in the step1 running binary.
- Native shared-pointer publication uses implicit mutable -> const conversions while constructing locally; per-context/cursor mutation isn't on definition assets. TStrongObjectPtr copy/move/reset/IsValid declarations read in **Core/Public/UObject/StrongObjectPtrTemplates.h**, wrapper in CoreUObject/Public/UObject/StrongObjectPtr.h. Epoch, skeleton/animation and temporary components/classes have explicit strong owners; actor/context subscriptions weak. Real GC coverage still unrun.
- Native configure lambdas are consumed synchronously and don't retain borrowed record pointers. Scope-exit snapshot runs at end of each tracker Tick path, never a second tracker evaluation. Weak UObject delegate unsubscribe on EndPlay. No arbitrary Blueprint callback/imported property application.
- `ExportText_InContainer` live catalog cpp184 exactly matches UE5.5 `CoreUObject/Public/UObject/UnrealType.h:677`: Index,FString&,Data,Delta,Parent,PortFlags,optional root. Owner UObject* and null Delta valid; return bool ignored for conservative text-wiring test. Text membership is NOT semantic parent-ABI/equip proof.
- UWorld CreateWorld/DestroyWorld, UWorldSubsystem Initialize/Deinitialize/ShouldCreateSubsystem, component lifecycle and AnimInstance/AnimMontage public read APIs checked against local headers. Skeleton gate uses runtime IsCompatibleMesh, not editor-only IsCompatibleForEditor. FileHelper SaveStringToFile FStringView overload and FileManager MakeDirectory signatures read. Json serializer writer-policy templates checked; ScopeExit macro header read. Automation TestNotEqual overload exists. This is signature inspection only.
- Build.cs already includes Core/CoreUObject/Engine and private Json; UMG/Slate/SlateCore/InputCore already cover step1. Shadow public header forward-declares JSON object; JSON headers stay CPP. No MotionWarping or new external module API used. **Build.cs unchanged; no extra claim needed.** Module classes/functions carry ONEBOSSFIGHT_API where exposed; helpers are same-module native records.
- Rechecked live catalog's remaining UE_LOG sites: no additional `if(...) UE_LOG(...); else ...` macro-body pattern. An `else UE_LOG` with an ordinary if-body is not the C2181 cause. No speculative live-source reformatting during Claude's gate.

## D06/D08/spec closure and unclosed risks

All original-three pins/aliases/HUD labels, strict data null epoch, immutable publication/late-cvar policy, fourth shared-weapon limitation and viewport guards remain unchanged from C107 fixes. No slot/equip/HP/posture/balance/time/animation changes to live code. Original player0/global legacy enum caches are known existing limitations, not a new two-world gameplay proof. Step1 resolved references still need actual semantic ABI/equip/cook proof; do not weaken path validation merely to make data mode pass.

WP8/WP9 reports map D07 contracts to symbols and explicitly leave full typed private-field adapters, imported metadata/segment/branch maps, complete consumer closure and actual ready-first-read order OPEN. C118 accepts the choice to scope this draft to flat already-mapped artifacts; that is not completion of a full branching compiler. Registration is not transactional rollback. Current binding rejects post-BeginPlay respawn attachment; deferred/respawn lifecycle adapter must be completed before promotion can replace the old path. No second-boss/canary/network/visual acceptance from these drafts.

## Checks actually run

Python AST parse4/4 scripts without importing Unreal;8 staged C++ files have0 invalid control bytes; generated headers last in both reflected draft headers. Scoped `git diff --check` on changed coordination docs passes with CRLF conversion warnings only (new untracked files separately checked for control bytes). CSV83rows/83unique, exact9-field artifact range equality with generator and unchanged statuses66PARTIAL/16UNVERIFIED/1MISSING. Spreadsheet phase before/after preview inspected; no extra xlsx. AG16 Rev01 five self-tests independently run without main/output writes,27input hashes match and clamp counterexample reproduced. None is a C++ compilation or PIE pass.

## Claude commands

After step1 acceptance and integrated draft review, take preimages immediately before applying exact seams, promote complete agreed set, close editor: `powershell -ExecutionPolicy Bypass -File Scripts/Rebuild.ps1 -Tests`. Relaunch -nosound/warm/unminimized; run focused WP10 witnesses, then entire current `Scripts/RunDrivers.ps1` table. Missing fixtures/importer/adapters must be completed first; don't run diagnostic scripts on the unchanged arena and call expected fixture failures product regressions. No Codex editor/build/PIE or commits/pushes.

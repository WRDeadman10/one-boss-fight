# Queue AB-C26–C30 — UE 5.5 compatibility, guard, lifecycle, dependency audit

Status: static source/log review complete, 2026-11-07. No Unreal build, editor, PIE, asset edit, or runtime test was run by Codex. Scope: the current ER input/array override and montage helper work, the DLSS settings implementation, Tier 2 presentation hooks, and `OneBossFight.Build.cs`. C-16's cook-root change is configuration-only; it adds no C++ source delta. The prior C-871 verdict supplies the guard checklist: exact declaration/definition and include review, count conditional pairs, check captured state, keep Shipping behavior intentional, and require explicit approval for product behavior.

## AB-C26 — UE 5.5 API/deprecation scan

- `RPGDodgeTiming.cpp` compiled in C-975's BUILD-247 (`B_C975_X1379/build.log`, compile action 5/12); the authored Air rules test compiled at 2/12. That receipt predates `SetMontageSegmentRange`, so it does **not** validate the new helper.
- The helper uses `UAnimMontage::CalculateSequenceLength`, `SetCompositeLength`, `UpdateLinkableElements`, and editor-only `PostEditChange`. These are present in the installed UE 5.5.4 headers; `SetCompositeLength` updates the montage's frame-backed data model in editor builds. It validates finite, ordered source times and an existing first slot/segment/reference before mutation, then recalculates length and marks the package dirty (`RPGMontageUtils.cpp:55–80`).
- Native test `OneBossFight.Authoring.MontageSegmentRange` covers null/empty inputs, invalid and over-length ranges, the accepted F10..F34 slice, resulting 0.8 s length, and dirty state (`RPGMontageUtilsTests.cpp:8–44`). It is authored only; BUILD-248/native automation must confirm UHT/API/runtime details.
- BUILD-247's recorded warning classes are the non-preferred VS toolchain and missing Niagara dependency declarations in the separate UnrealClaude plugin. No project C++ deprecation warning was found in that build receipt. Do not count this as evidence for newly authored code.

## AB-C27 — C-871 checklist re-run

| Check | Result |
|---|---|
| Declaration/definition and module export | `URPGMontageUtils::SetMontageSegmentRange` declaration and definition match; class has `ONEBOSSFIGHT_API`; declaration and implementation are both `WITH_EDITOR` (`Combat/RPGMontageUtils.h:34–38`, `.cpp:54–80`). |
| Includes | Montage utility includes `AnimMontage` and notify types in its `.cpp`; generated header remains last in its `.h`. The montage test includes `AnimMontage`, `AnimSequence`, utility header, and automation header. Air and DLSS settings types are declared in module-local headers and used from `.cpp` implementations. |
| Access / reflected API | Slot tracks and segments are public engine data; helper is editor-only and callable by editor scripts. `FAnimSegment::UpdateCachedPlayLength` is private to engine editor classes, so the helper correctly avoids calling it; cached length records the full source animation and the changed playable range does not make that cache stale. |
| Captured state / lifetime | The helper has no lambda or asynchronous capture. Air and guard overrides retain weak ability references, array property names, and serialized array backups; restoration imports the snapshot, clears the backup list, and runs on montage start/timeout or component EndPlay (`Player/RPGDodgeTiming.cpp:598–641`, `633–678`). |
| Conditional balance | A direct `#if/#ifdef/#ifndef` versus `#endif` stack scan reported zero unmatched or premature directives in the reviewed helper, input, Tier 2, DLSS, and Build.cs files. This is a lexical balance check, not a C++ parser/UHT proof. |
| Shipping behavior | The montage slicer is absent outside editor builds. Air montage routing is deliberately runtime behavior, approved as an empty-default production change in C-973; saved fields remain empty. Tier 2 CVars and reads are enclosed by `UE_BUILD_DEVELOPMENT`; non-Development returns false. DLSS setting API is runtime-visible, with `Off`/TSR the saved default; this audit does not choose a DLSS player default. |

## AB-C28 — optional-feature ownership and teardown

- Air/GuardCounter array override state is owned by `URPGDodgeTiming`; each backup identifies its ability and exact array name. `EndPlay` restores all saved arrays and clears the guard timestamp. Missing component/property/empty target arrays fail closed. The shared restoration helper's legacy name (`RestoreGuardCounterMontageOverride`) now covers air arrays too; this is a naming-only clarity issue, not a separate owner.
- Tier 2 aura is attached to the boss mesh and its component pointer is destroyed in `ClearPhaseTwoVisuals`; the clear path is called from director `EndPlay` and encounter reset/phase teardown (`Boss/RPGSevarogDirector.cpp:54–61, 224–242, 453, 561`). Recoil montage playback is delegated to the mesh `AnimInstance` and has no separate owned component.
- Tier 2 glow uses a Material Parameter Collection, which is shared world state. Entry sets the named scalar to 1 and cleanup writes 0 only when this director recorded a successful set (`RPGSevarogDirector.cpp:212–241`). It does not preserve an earlier nonzero value or coordinate multiple directors. The current one-boss arena path does not establish multi-director use; keep this limitation explicit if the hook is reused.

## AB-C29 — Development CVar guard scan

- `rpg.Art.Tier1` and `rpg.Art.Tier2` are declared inside `#if UE_BUILD_DEVELOPMENT`; both accessors return false in other configurations (`Player/RPGTier1VisualRules.cpp:9–34`). `RPGPresentationRules::IsTier2PreviewEnabledForBuild` also requires the Development flag (`Player/RPGPresentationRules.h:9–12`).
- Tier 2 visual application and recoil each check `IsTier2PreviewEnabled` before loading/spawning or playing the optional asset (`Boss/RPGSevarogDirector.cpp:195–198, 246–252`). No direct Shipping CVar read was found in the scanned implementation. Authored optional references are intentionally usable in Shipping by the existing Tier 1 rule contract; Tier 2 authoring fields remain empty by default.

## AB-C30 — Build.cs dependency scope

- `DLSSBlueprint` is a private dependency, matching its use from `RPGDLSSGameUserSettings.cpp`; no DLSS plugin type appears in that class's public header. `Renderer` and `RHI` are also private and documented for benchmark telemetry. `UnrealEd` is added only when `Target.bBuildEditor` (`OneBossFight.Build.cs:33–53`).
- `Niagara` remains public because public module headers expose Niagara types; removing or privatizing it without moving those declarations would risk module consumers. No dependency change is justified by this review.

## Outcome / remaining verification

No confirmed UE 5.5 compile defect was identified by this static review. BUILD-247 is evidence for its recorded source state only; it does not compile the new editor helper or run the new native test. Lead BUILD-248/native automation must verify UHT and the range test. The copied post-air probe is separately pending both-route Lead PIE; no runtime restoration claim is made here.

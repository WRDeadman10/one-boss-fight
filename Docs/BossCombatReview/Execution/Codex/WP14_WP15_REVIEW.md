# X-T1: WP14/WP15 independent source review

2026-10-26. Read-only review; no build/PIE executed by Codex. Scope: current source, not a claim that all spec obligations pass.

## Findings

1. **Resolution negative test does not exercise resolving rejection.** `Source/OneBossFight/Tests/RPGCombatCatalogTests.cpp:138` changes the pinned Starter StyleName. `Player/RPGCombatCatalog.cpp:161` rejects that structural legacy-contract change before the resolving block at 184. Test label at 140 overstates its witness. Add a structurally valid fourth weapon/build with a deliberately incompatible full reference, or alter a non-pinned resolved dependency while preserving the structural contract; assert the exact failure field, not just nonempty text.
2. **Ancestry negative coverage remains missing.** Tests:128 sets ItemBaseClass to the loaded item's actual class, making the positive IsA relation true by construction. This checks installed assets load, not that malicious/incorrect declared ancestry is rejected against a fixed expected weapon-item ABI. Catalog:184 accepts any UClass as AbilityClass. These are v3 C3 acceptance gaps, not evidence that the shipped three assets are wrong.

## Clean checks

- DormantWake:104-127: test-switch branch checks character, mesh, anim instance and weak montage before stopping precisely the dormant montage; clears its weak handle. No stop-all-montages operation.
- DormantWake:101-128: skip behavior is non-Shipping only. Enabled wake path below 129 is unchanged by the stop fix.
- Encounter:264-276 guards repeated Wake with bDormant, clears dormancy before BeginWake, and finishes immediately when it returns false. No recursive CancelWake from the new branch. BeginDormant resets prior wake state through StopClips.
- Catalog:216-231: braces make UE_LOG's macro expansion an unambiguous if/else; strict data failure returns a null epoch, not a legacy partial merge.
- Catalog:55-71: Describe prioritizes a verified matching BuildId and reports unbound shared-style ambiguity; it does not silently choose the first legacy row.
- BuildLoadout:277-294: GetBuildName uses the same verified identity / explicit ambiguity rule, preserving Unknown versus OffBuild classification.
- BuildLoadout:549-557 and 819-831: chosen state is stable BuildId and verification remains style match; removing redundant Chosen enum does not remove the chosen-id path. Style-only verification is a bounded existing capability, not proof of arbitrary new item correctness.
- Tests:119-135: resolving positive test actually calls Compile(..., true), not the structural-only path; it checks all three builds survive.

## Verdict

WP14/WP15 fixes accepted for their bounded purpose. Request the two test/validator follow-ups above before claiming full v3 reference-closure acceptance. Editor automation and gate claims are reviewed separately in X-T2; this source review is not a new run.

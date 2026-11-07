# AB-C01–C05 — Guard Counter integration handoff

Date: 2026-11-07. Source/offline review only; no Unreal, import, build, package, or asset write.

## C01 — accepted asset and importer readiness

The local GuardCounter deliverable has FBX, review MP4, look render, frame strip, and text metadata under `Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Attack_GuardCounter/`. Metadata declares a one-shot 0.800 s clip, 100 cm forward motion, 0.333–0.533 s hit window, and preserved yaw. `Scripts/Editor/import_er_clips.py` targets `/Game/OneBossFight/Player/Animations/AN_ER_Attack_GuardCounter`; it checks new-only, AnimSequence class, skeleton, sequence length, and nonempty data before save. `Import/Player/Animations/` does not exist; the deliverable-folder FBX source is available. C-968 authorizes only GuardCounter import; it is not yet an owner visual approval or evidence of a completed import. `ENGINE_LOCK.json` is held by Antigravity. **Do not run the importer while that lock is held.** Static tool risk: with no `IMPORT_CLIP_FILTER`, the importer selects all four entries, including three clips C-968 rejected for R4. Before any unfiltered run, the importer should gain a fail-closed accepted-clip allowlist or be invoked with the exact GuardCounter filter.

## C02 — state cleanup audit

| Lifecycle | Current behavior | Gap / disposition |
|---|---|---|
| Successful block | `NotifySuccessfulGuardContact` timestamps only a `Guarded` contact; R2 consumes one eligible timestamp. | Correct for a single attempt; no explicit encounter-reset invalidation entry point was found. |
| Montage start | Tick observes the active montage and restores original `StrongAttackMontages`. | Normal path restores promptly after observed playback. |
| Montage absent/fails to start | Temporary array override has a 1.0 s timeout. | Normal tick is the fallback cleanup. |
| Player death or same-pawn reset | No dedicated hook clears `LastSuccessfulGuardTime` or restores the override at the transition. | EndPlay cleanup below handles component world teardown; same-pawn reset remains a future explicit lifecycle integration point. |
| Component EndPlay | Previously no override cleanup existed. | Fixed here: restore arrays and invalidate the counter window before `Super::EndPlay`. |
| Component unregister | No separate OnUnregister cleanup. | EndPlay is the owned gameplay teardown boundary; if component unregister is used independently, add a separate path only with a concrete caller/test. |

## C03 — cleanup regression contract

Added a focused offline source-contract assertion that EndPlay restores temporary ability arrays, invalidates the block timestamp, and calls the superclass. This complements the current successful-contact/fallback contract; it does not substitute for a native automation test or Lead build/PIE.

## C04 — rule boundary map

`RPGGuardCounterRules::IsCounterPress` accepts the closed interval `[blockTime, blockTime + window]`; it rejects earlier presses, after-window presses, nonfinite values, and nonpositive windows. Native `RPGGuardCounterRulesTests.cpp` has exact start/end, epsilon-after, before-start, invalid-window, and nonfinite assertions. The 0.60 s property remains a proposed/default integration value; these rule tests prove boundary semantics, not owner approval or live gameplay balance.

## C05 — hand-test prerequisites

The ER hand-test sheet already requires a living player and an observed front-facing blocked contact before the counter attempt; the row is gated on import, owner video review, and Lead build. The import lock is active, and successful compile/PIE evidence is not present in this batch. The A1/A2/A3 test rows remain pending their R4 clip decisions. Do not mark any row passed from static evidence.

## Validation boundary

No engine lock was acquired or modified. No asset/import operation was run. Focused Python contract test and `git diff --check` are reported in the batch receipt; C++ compile, native automation, import, CookCoverage, and PIE remain Lead-owned or pending the lock release.

# AK-C16–C20 — native test and source review

This batch is static only. C-1022 accepted the isolated Python and runner dry-run hotfixes, but it did not report a build/native result for the X-1431 test additions. The Lead holds `ENGINE_LOCK` for full-fight capture. No test is marked runtime green from that acceptance.

| Task | Review |
|---|---|
| C16 | `RPGGuardCounterRulesTests.cpp` now checks the `BlockReaction_C` suffix with exact case/trailing-token rejection and `IsNewBlockedContact` as blocking plus a reaction rising edge. Those expressions match the pure header; compilation/native result remains Lead-owned. |
| C17 | `RPGResolveActiveMontageOverride` returns the active semantic kind only for a nonnull montage with the same object identity. New null/different-object tests match that contract. `RPGDodgeTiming.cpp` retains the kind after arrays restore while the montage is playing, then clears it on stop/timeout/EndPlay. This is a source path, not proof that a counter swing played. |
| C18 | `SetMontageSegmentRange` rejects null montage, nonfinite/invalid time, zero slots and zero segments before `Modify()`. The new cases cover NaN/infinite bounds and zero slots; the two-slot case asserts only the first track's first segment changes. Build/native execution remains open. |
| C19 | The helper intentionally edits `SlotAnimTracks[0].AnimSegments[0]`, then recalculates montage length from the whole montage. A longer second slot may therefore keep the composite play length longer than the first trimmed segment; that is an API scope caveat, not a demonstrated defect. No production change without a failing acceptance case. |
| C20 | The test-only patch passed scoped whitespace checks. The exact Lead suites to run are `OneBossFight.Player.GuardCounterRules`, `OneBossFight.Hit.Classify`, and `OneBossFight.Authoring.MontageSegmentRange`. No Codex Unreal build, PIE or asset edit. |

Lead must report compiler/native results for the X-1431 additions after the lock is released; any rejected case becomes an immediate hotfix.

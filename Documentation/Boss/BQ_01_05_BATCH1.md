# BQ-01..05: Queue BQ batch 1, framework boss robustness (source-only)

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`, per X-2318.

**All C++ here is written but NOT compiled or run.** Binary acceptance needs the Lead's C-1155 build and automation suite. No engine, editor, PIE, tool, asset or PARRY edit was made, and nothing was committed.

| Task | Status | Files | Evidence |
|---|---|---|---|
| **BQ-01** KI-155 parry-abort starvation | accepted at source-review level (X-2322; AG A-948) after the X-2320 hotfix | `Player/RPGBossFrameworkProfile.h/.cpp`, `Tests/RPGFrameworkRuntimeTests.cpp` | Details below the table |
| **BQ-02** KI-174 leash during combo pause | **scope reconciled: already covered statically**; no new code | none | Details below the table |
| **BQ-03** retry generation fence on a reused actor (BF-X23/X24) | done (test only; the fence already existed) | `Tests/RPGOwnedTagCleanupTests.cpp` | Details below the table |
| **BQ-04** KI-128 arithmetic guards | accepted at source-review level (X-2327; AG A-951) | `Player/RPGBossMath.h`, `Player/RPGBossPosture.cpp`, `Boss/RPGFrameworkBossCharacter.cpp`, `Tests/RPGPostureDrainFiniteTests.cpp` (new) | Details below the table |
| **BQ-05** | this report | | |

## Task details

**BQ-01:**
- **Change:** a new opt-in field `MaxAbortedAttacks` (default 0 keeps the KI-149 rule unchanged). The pure `PhasePoolCannotStarveWithAborts` and `CooldownStarvationError` are wired into profile compilation, and `ValidateProfile` has a Domain refusal for bad values.
- **Tests:** `Framework.Runtime.PhasePoolAbortStarvation` (the KI-155 trace, a 6×4×10 sweep, the decision cases) and 3 `ProfileDomains` cases.
- **Review:** C-1546 and C-1548.

**BQ-02:**
- **Already pinned:** BM-36..40's `Scripts/Tools/test_framework_boss_static_pins.py` pins every KI-174 fact. The leash return precedes the combo-pause check in `Tick`; the pause deadline is absolute world time; `HandleLeash` writes no pause state.
- **Why no native test:** a runtime test needs an initialized `ARPGFrameworkBossCharacter` ticking in a test world. That is engine-scope, so it moves to the ENG lane.
- **The production change** still waits on the lead's intent decision (O8).

**BQ-03:**
- **The fence is already in source:** `RPGOwnedTagCleanup::MayRemoveForGeneration`, with `OwnedTagGeneration` captured by parry and i-frame teardown. It had no regression test.
- **New test:** `Player.OwnedTagCleanup.GenerationFence` covers the same owner and generation (allowed), a newer or older generation (cancelled), a different owner (cancelled), a null owner (cancelled), the ambiguous `MAX_uint64` (cancelled), unbound 0/0 (allowed, legacy), and unbound-then-bound (cancelled).

**BQ-04:**
- **Fixes:** `IsValidDrainAmount` is now the `URPGBossPosture::ApplyPostureDamage` guard. `SanitizeDrainAmount` guards the framework-boss `ApplyHit` posture sink, where `Row.PostureDamage` had no check and a NaN or negative value poisoned or raised posture. `RegenStep` now keeps the posture on a NaN or −inf result, while +inf still clamps to max.
- **Already covered:** bleed accumulation and threshold growth (BM-26..30, the bleed finite-input tests).
- **Test:** `Framework.Posture.DrainAmountFinite`.
- **Review:** C-1550, C-1552 and C-1554.

## Scope reconciliation

- **BQ-02** is satisfied by the existing static pins; its runtime arm is ENG.
- **BQ-04's bleed parts** were already covered; only the posture accumulators needed changes.

## Gates still open

1. **The Lead's C-1155 build plus the native automation suite** for all new and changed tests:
   - `Framework.Runtime.PhasePoolAbortStarvation`
   - `Framework.Runtime.ProfileDomains`
   - `Player.OwnedTagCleanup.GenerationFence`
   - `Framework.Posture.DrainAmountFinite`
2. **O8:** the KI-174 intent.
3. **Opting PARRY into `MaxAbortedAttacks`:** an asset edit, if wanted.

## Earlier working-tree edits

Every edited file that already had uncommitted changes (from the BK lane and earlier) was preserved; my edits were insertions or in-place guard changes only.

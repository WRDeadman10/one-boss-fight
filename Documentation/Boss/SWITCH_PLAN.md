# Boss architecture switch plan (C-1177)

**Status:** target architecture and plan only; implementation is not authorized by this document. The owner approved the architecture in C-1177 and `Documentation/DECISIONS.md`. Lead review of this migration plan is the next gate. The Ember Warden sword/trace Phase 1 is implemented and measured separately in `C1172_EMBER_VISUAL_WEAPON_TRACE.md`; its visible grip alignment and hit/parry acceptance still need AG/Lead follow-through.

## Target

Add a boss by supplying that boss's animation set, montage timing annotations, encounter data, and AI move selection. Existing shared C++ owns reusable combat rules: damage resolution, poise/posture, parry, i-frames, stagger, camera, attack-window consumption, and the interface between AI and an executing move. A boss-specific montage remains authoritative for its attack timing; shared code reads it and does not select a product's moves or supply its per-move timing table.

| Responsibility | Target owner | Boundary |
|---|---|---|
| Damage, posture, parry, i-frames, stagger, camera, shared move execution | Shared C++ combat core | No boss names, boss-specific move choices, or per-boss timing constants in the shared core. |
| Warning tell, commitment, active/hit interval, parry contact, recovery | Notify data on that boss's own montage | Montage-local seconds; move identity and flags travel with the authored event. No inferred timing for an unmeasured montage. |
| Health, poise, range, turn limits, branching parameters, ability settings | Per-boss encounter definition | Defaults belong to the boss data; shared code consumes validated values. |
| Move choice, follow-ups, phases, distance/health conditions | Boss Behavior Tree plus data move list | AI chooses a move; the shared executor plays it and observes authored timing. |
| Unique mechanics such as low sweep, javelin, leap wave, or a new boss-only special | Reusable special-attack modules selected/configured by boss data | Modules expose a stable interface and do not add branches to the common tracker for each boss. |

## Montage annotation design

### Proposed authored object

Use one `UAnimNotifyState_BossMoveTiming` instance on each move montage. Its notify-state span covers the move's authored execution interval. The notify carries these explicit, validated fields (all time values in montage-local seconds, independent of play rate):

| Field | Meaning |
|---|---|
| `MoveId` | Stable data identifier for this boss move/stage (for example Ember `A3a`; Sevarog IDs are authored with his move list). |
| `TellStartTime` | Start of the readable warning within the montage. |
| `CommitTime` | Last time the AI/executor may steer toward the target; heading is locked after it. |
| `WindowStartTime`, `WindowEndTime` | Inclusive opening/exclusive closing policy to be fixed by Lead review; bounds of the attack's damage/trace window. Each separate damaging interval gets its own state instance or an explicitly supported repeated window, never a widened gap. |
| `ParryContactTime` | Montage-local target for parry contact; `-1` means the Lead has not measured/approved one. Do not synthesize one from the hit-window midpoint. |
| `RecoveryEndTime` | Earliest legal move-selection time after recovery. |
| `bIgnorePlayerIFrames` | Explicit per-move authorization for bypassing player i-frames; default false and rejected unless a reviewed design requires it. |
| `TrackTurnRate` | Maximum tracking rate before commitment. |
| `bBranchStage`, `BranchRange`, `BranchConeDegrees` | Optional chain-stage gate, read as data; unused for non-branching moves. |
| `bAuthoredWindup` | Whether the animation contains its authored tell/windup and must bypass any generic close-telegraph scaling. |
| `SpecialModuleId` and settings | Optional module selection/configuration for unique hit delivery or mechanic. The core receives a module interface, not boss-specific conditionals. |

Runtime behavior: the shared montage observer resolves the current notify state by montage instance and `MoveId`, opens/closes the same trace/damage window used today, publishes the tell and commitment events, and supplies the measured parry-contact time to the existing parry resolver. It must handle interruption, blend-out, montage replacement, duplicate notify events, chained stages, missing annotations, and unknown IDs fail-closed: close damage windows and expose a diagnostic rather than inventing a time. Notify state end or montage end must always release the active move. The implementation must not assume a single montage instance or use asset names as identity.

If UE's notify-state instance lifetime or cooked-data serialization cannot safely carry the required values, the fallback design is an immutable montage-authored `UAnimNotifyState` that references a validated move row in the boss encounter definition. Lead must review the authoring/readback tradeoff before implementation; do not silently split authority between a notify and a second timing table.

## Phase 1 — Ember Warden migration (after plan review)

Today the source of the tracker's phase/commit/recovery values is `FRPGAttackTrackerConfig` in `Source/OneBossFight/Player/RPGAttackTracker.cpp` (A1/A1b/A3a/A3b/A2/A4/A5/A6). Migration must copy values exactly before deleting or disabling the C++ defaults. These table bounds are tracker observation/heading bounds: `RPGAttackTracker.h` explicitly says the tracker observes the move while the pack montage's collision-trace notify opens the real hit window. Therefore the `ActiveStartTime`/`ActiveEndTime` values below must not be presented as a complete inventory of damaging notify intervals. Lead must inventory/read back each montage's actual damage events and special-module delivery before claiming identical behavior.

| Move | Current montage / fallback | Commit | Current tracker active bounds | Recovery end | Turn rate | Other current semantics / damage delivery |
|---|---|---:|---:|---:|---:|---|
| A1 | `AM_Boss01_A1` / `GS_Attack03_Montage` | 0.33 | 0.35–0.50 | 1.20 | 360 | Authored windup; no branch |
| A1b | `GS_Attack04_Montage` | 0.12 | 0.16–0.46 | 1.25 | 360 | Branch stage; no authored-windup flag |
| A2 | `GS_ChargedAttack_Montage` (optional tracker preview `AM_Boss01_A2`) | 1.68 | 1.93–2.11 | 3.14 | 120 | Pack ability remains live path pending separate approval. Source comments/PIE report two actual pack trace intervals (1.57–1.76 and 1.93–2.11); only the second damaged in the cited scenario. Preserve both trace intervals if migration owns those events, while preserving this single tracker-observation range. Verify against the live notify readback before claiming parity. |
| A3a | `AM_Boss01_A3a` / `GS_Attack01_Montage` | 0.38 | 0.40–0.60 | 0.80 | 360 | Authored windup; first combo stage |
| A3b | `AM_Boss01_A3b` / `GS_Attack02_Montage` | 0.13 | 0.15–0.40 | 1.3333 | 360 | Branch stage; authored windup |
| A4 | `AN_Boss01_A4_LowSweep` | 0.40 | 0.60–0.90 | 1.75 | 180 | Custom low-sweep module delivers damage rather than pack trace; retain same notify window contract. |
| A5 | `AN_Boss01_A5_JavelinThrow` | 0.45 | 0.45–0.50 | 0.95 | 240 | Projectile release is the short active interval; projectile flight remains owned by the javelin module. |
| A6 | `GS_LeapAttack_Montage` | 0.16 | 0.75–1.17 | 1.80 | 120 | Landing wave starts at active-window open; keep movement, trace, and wave semantics intact. |

The C-1132 report provides Lead-measured parry-only montage-origin targets for A1b 0.190/0.199/0.231, A3b 0.152/0.254, A1 0.351, A3a 0.484/0.530, and A2 1.974/2.030/2.104 seconds. These land within the corresponding tracker observation bounds, but that is not proof those bounds equal every real damage-notify interval. The values are observations, not approved single contact timestamps. Lead must choose/measure a stable `ParryContactTime` per move and reconcile multiple observed contacts before migration; absent that decision the field remains unset and the plan does not claim parry parity. C-1152 parry-close/hit results are a separate Lead-owned acceptance gate, not inferred from the notify conversion.

### Parity gates

1. Add pure validation/contract coverage first: ordered bounds, finite values, notify coverage, unique move identity, invalid/missing fields, chained stages, multiple active intervals, and interruption cleanup.
2. Compare emitted tell/commit/window/recovery event sequences against today's `FRPGAttackTiming` entries for every Ember move. Values, windows, branch eligibility, module start/release, trace close, and lock-on behavior must match; no balance retuning in this migration.
3. Keep the current table as a temporary comparison oracle until the comparison suite passes. Then remove its runtime authority in one reviewed change; do not leave two competing sources of truth.
4. Lead runs the existing C-1132 and C-1152 PIE metrics and compares hit/trace timing, parry contact/reward, i-frame behavior, and interrupted-window closure. Existing tests plus source comparison alone do not prove runtime parity.
5. Lead verifies authored notify values after save/reopen and in the packaged/cooked asset path before the migration is accepted. No Shipping/package claim is made by this plan.

### Existing automated coverage and identified gap

`Source/OneBossFight/Tests/RPGBossAttackTrackerAdaptersTests.cpp` contains `OneBossFight.Boss.AttackTracker.TypedDefaultsAndAdapter`. It currently checks default/config field equality, duplicate IDs, non-finite branch range, attack-window ordering, missing montage identity, and refusal to reconfigure after BeginPlay. It does not exercise authored montage notifies, event ordering, runtime interruption cleanup, tell delivery, parry-contact dispatch, `bIgnorePlayerIFrames`, or equivalence of the notify-driven event sequence to the current table. Those are new migration tests, not existing proof. The C-1132 and C-1152 PIE captures remain Lead-owned runtime acceptance inputs; this plan does not assert their current results or replace them with unit tests.

## Phase 2 — Sevarog data and montages

Sevarog gets his own encounter definition, montage set, move IDs, notify annotations, and Behavior Tree/data move list. The C357 staged read-only inventory found 15 `AnimMontage` assets under `/Game/ParagonSevarog` and `/Game/OneBossFight/SevarogPack/Montages`; this is an asset inventory, not a validated move list or runtime graph audit. Current pack montage names and observed notify labels are:

| Montage asset | Existing notify labels from C357 inventory | Timing interpretation |
|---|---|---|
| `LevelStart_Montage` | `PlayParticleEffect` | Entrance/setup candidate; event time unavailable. |
| `Swing1_Medium_Montage` | `SaveAttack`, `ResetCombo` | Attack candidate; event times unavailable. |
| `Swing2_Medium_Montage` | `ResetCombo`, `SaveAttack` | Attack/follow-up candidate; event times unavailable. |
| `AM_SevPack_Backhand` | `ANS_DisableMovement`, `ANS_SetDesiredRotation`, `ANS_CollisionTrace`, `AN_PerformFollowUp`, `End Animating Ability` | Candidate attack; trace interval and event times not read by the C357 Python API. |
| `AM_SevPack_Charge` | `ANS_DisableMovement`, `RPG Charge To Target`, `ANS_SetDesiredRotation`, `ANS_CollisionTrace`, `End Animating Ability` | Candidate charge attack; event times unavailable. |
| `AM_SevPack_Death` | none observed | Death montage candidate; no move timing inferred. |
| `AM_SevPack_Entrance` | `AN_ToggleCombat`, `End Animating Ability` | Entrance/setup candidate, not an attack. |
| `AM_SevPack_Exit` | `AN_ToggleCombat`, `End Animating Ability` | Exit/setup candidate, not an attack. |
| `AM_SevPack_Lightning` | `ANS_DisableMovement`, `ANS_SetDesiredRotation`, `AN_SendEventToAbility`, `RPG Spawn Effect`, `End Animating Ability` | Candidate special attack; no collision-trace label observed in this inventory. |
| `AM_SevPack_Lunge` | `ANS_DisableMovement`, `ANS_SetDesiredRotation`, `ANS_CollisionTrace`, `End Animating Ability` | Candidate attack; trace/event times unavailable. |
| `AM_SevPack_Overhead` | `ANS_DisableMovement`, `ANS_SetDesiredRotation`, `ANS_CollisionTrace`, `End Animating Ability` | Candidate attack; trace/event times unavailable. |
| `AM_SevPack_Roar` | `ANS_DisableMovement`, `End Animating Ability` | Candidate roar/special; no attack window inferred. |
| `AM_SevPack_Shockwave` | `ANS_DisableMovement` (3), `ANS_SetDesiredRotation`, `RPG Spawn Effect` (2), `ANS_CollisionTrace`, `End Animating Ability` | Candidate special attack with repeated labels; exact event ordering/times and damage delivery are unverified. |
| `AM_SevPack_Sweep` | `ANS_DisableMovement`, `ANS_SetDesiredRotation`, `ANS_CollisionTrace`, `AN_PerformFollowUp`, `End Animating Ability` | Candidate attack; trace/follow-up times unavailable. |
| `AM_SevPack_Turn` | `ANS_SetDesiredRotation`, `End Animating Ability` | Turn/positioning candidate, not assumed to damage. |

C357 could read notify names but its Python API could not read notify absolute times or durations; those fields were explicitly recorded UNKNOWN. Montage notify names also do not establish what the Blueprint/ability graph does. Lead must inspect the actual assets and measure contacts before this list becomes Sevarog's move set. For each confirmed attack montage, Lead records tell, commitment, every damage interval, parry contact, recovery, and any i-frame exception using the C-1132 montage-origin method. Unmeasured values stay unset; do not copy Ember timing into Sevarog. Evidence and limitations: `Docs/BossCombatReview/Execution/Codex/SevarogInventory/REVIEW_AND_RUN_PLAN.md` and `run_reviewed/inventory_records.jsonl`.

Sevarog-specific numeric parameters live in his encounter definition. AI branch conditions reference data IDs and validated ranges. Reuse A4/A5/A6-style modules where mechanics match; add a unique module only when the move cannot be represented by existing module configuration. New Sevarog content must not require a new shared-core `if (Sevarog)` path or changes to Ember defaults.

## Sequencing and ownership

1. Lead reviews this plan, including the multiple A2 windows, parry target policy, notify serialization, and interruption behavior.
2. Antigravity/animation author marks up Ember's own montages only after approval; Codex implements the shared observer/validation and test-first migration; Lead owns build, C-1132/C-1152 PIE parity, and packaged readback.
3. Do not change Ember timing, add Sevarog timing guesses, change assets outside the approved montage annotation scope, or remove the old table before the parity gates pass.
4. After Ember parity is accepted, inventory Sevarog montages, have Lead measure his events, and author his data/AI separately. Then validate a data-only boss addition without shared-core edits.

## References

- `Documentation/DECISIONS.md` — owner-approved target architecture (C-1177).
- `Source/OneBossFight/Player/RPGAttackTracker.h/.cpp` — existing timing fields, values, montage resolution, move and branch behavior.
- `Documentation/Boss/C1132_PARRY_MONTAGE_ORIGIN_TARGETS.md` — Lead-reported montage-origin contacts and limits.
- `Documentation/Boss/C1172_EMBER_VISUAL_WEAPON_TRACE.md` — Phase 1 sword work; visual alignment and hit/parry acceptance remain open.
- `Documentation/TEST_PLAN.md` and the Lead C-1152 evidence folder — runtime acceptance should be linked when the migration is implemented, not claimed by this plan.

# Queue S27–S29: repeated respawn pair and component tick reads

Date: 2026-11-05. Static/offline work only; Claude owns the Editor pair.

## S27 — repeated death/respawn x3 on legacy and selected-data arms

`Scripts/RunA5DeathResetX3.ps1 -OutRoot <new-evidence-directory>` invokes the existing `pie_player_death_reset` parity pair with `-DeathResetRepetitions 3`. The pair wrapper sets the same repetition count in each fresh legacy and selected-data arm; it refuses this option for any other driver. The driver repeats the four existing death contexts (stance break, riposte, A4 sweep, A5 projectile) for three cycles and labels each cycle, for 12 respawns per arm. Existing one-cycle behavior remains the default. The existing 25-minimum check threshold still applies; the three-cycle run should emit 75 checks.

The driver/route fixture test passes; both PowerShell scripts parse and Python byte-compilation passes. **LEAD-RUN:** execute the dedicated pair after confirming the Editor is available; compare the two arm logs and preserve their receipts. Codex did not run Unreal or PIE, so no runtime pass is claimed.

## S28 — other component tick-state reads

Static inventory of the project `TickComponent` implementations; “risk” is a test candidate, not evidence of a live race. T1's tracker consumers remain covered by `T1_TICK_ORDER_AND_O3_INSTRUMENTATION.md` and are not repeated here.

| Consumer tick | Cross-component state read | Source | Ordering evidence / disposition |
|---|---|---|---|
| Boss phase flow | encounter dormant state and stagger state gate transition/leap behavior | `Source/OneBossFight/Player/RPGBossPhases.cpp:72–76,129–132` | Explicit Stagger prerequisite; no Encounter prerequisite. Same-frame phase-vs-stagger ordering is source-ordered. The remaining dynamic Encounter read is a test candidate, but actual relative order is unmeasured. |
| Stagger | posture's `IsPackPoisePinned()` decides whether a pack stun is suppressed or requests a break | `Source/OneBossFight/Player/RPGBossStagger.cpp:214–220`; `RPGBossPosture.h:83` | No stagger→posture prerequisite; however `IsPackPoisePinned()` is configured state (`bPinPackPoise && bConfigured`), not a value advanced by Posture's tick. Excluded as a tick-order hazard. |
| Close clip swap | encounter reset/dormancy and death-active state decide restore/skip | `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:52–56,107–125` | Explicit prerequisite on Encounter; no prerequisite on Death. This is an asset-presentation correction; potential single-frame delay only, unmeasured. |
| Boss music | encounter dormant and phase-two state select/stop audio | `Source/OneBossFight/Audio/RPGBossMusic.cpp:139–168` | No tick prerequisites found. Presentation-only; a phase swap may occur one frame later if registration order reverses. No gameplay consequence established. |
| Boss HUD | encounter generation/dormancy and cached phase/posture/stagger values update widgets | `Source/OneBossFight/UI/RPGBossHud.cpp:303–306,370–410` | No tick prerequisites found. Presentation-only; no visual one-frame issue established by this source audit. |
| Boss death | stagger, posture and phase can raise death in the same frame | `Source/OneBossFight/Player/RPGBossDeath.cpp:99–112` | Explicit prerequisites are added for all three sources. Existing designed ordering; retain as a positive control, not a new finding. |
| Dormant wake | encounter dormancy/waking state drives the wake component | `Source/OneBossFight/Player/RPGBossDormantWake.cpp:42–45,167–176` | Explicit Encounter prerequisite in BeginPlay; retain as a positive control. |

Generation checks in HealPunish/Shockwave are event/token comparisons, not a demonstrated cross-component tick-state ordering defect. CombatDebug/TraceAudit reads are diagnostics; TraceAudit already has the tracker prerequisite from T1. This source inventory does not provide runtime registration order for the rows above.

## S29 — test-first proposals, explicitly flagged

| Flag | Proposed test | Acceptance before any prerequisite/source edit |
|---|---|---|
| TEST-FIRST, gameplay | Build a transient world with Encounter and Phases registered in both orders; drive wake completion plus a phase-two threshold in the same frame. Keep the existing Stagger-before-Phases edge as a control. | Dormant gating and phase activation are identical, or a witnessed difference identifies the missing Encounter ordering contract. |
| NO TICK-ORDER CHANGE | Stagger/Posture pin read is static configuration, not tick-produced state. | Do not add a tick prerequisite for this read; a regular configuration assertion can cover the suppression policy if needed. |
| TEST-FIRST, cosmetic | Reverse Death/CloseClipSwap registration for death activation and encounter reset. | Either immediate same-frame restore is guaranteed or the test records the allowed one-frame presentation delay. |
| TEST-FIRST, cosmetic | Reverse Encounter/Phases registration while entering phase two and while resetting. | Audio/HUD reach the expected track/state by the next tick without duplicate restart, stale latch, or missed reset. |

No test code or tick-order source changes were made for S28/S29: current source establishes reads and explicit prerequisites, but not a defect or measured ordering in the live routes. The proposals are deliberately gated on a test that controls registration order.

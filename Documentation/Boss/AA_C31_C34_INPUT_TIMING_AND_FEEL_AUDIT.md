# AA-C31–AA-C34 — ER input timing and dodge feel

Static/source audit and Lead-run PIE plan, 2026-11-07. No Editor/PIE was run by Codex. The driver reports input-to-first-observed player montage start at Slate/game-tick resolution; it is not device latency and sets no pass threshold.

## AA-C31 — input probe

`Scripts/Editor/pie_er_control_latency.py` drives the gamepad mapping through `URPGInputTestUtils::SetKeyDown`, with a directional `IA_Move` injection only for the moving dodge case. Cases: R1 tap; R2 tap; R2 holds at 0.34, 0.35, 0.36, and 0.70 s; jump+R1; jump+R2; standing/moving dodge taps; and a double tap 0.14 s apart. Each sample logs the observed player montage and key-down-to-observation time, or `NO_MONTAGE_START`. Jump setup is excluded from the attack latency clock. Run once per route, preserving the Lead's route/build provenance; the probe holds the boss stable, warms the weapon, then stops PIE at completion.

Clip state from A-581/C-968: ER-A4 GuardCounter is accepted for import; ER-A1 Backstep_Back and ER-A2/A3 air attacks are rejected for R4. Until Lead imports an approved clip under the prescribed lock and the route is wired, the probe can only report active montage/fallback behavior. It does not claim that a fallback montage is the intended ER clip.

## AA-C32 — R2 hold threshold and charged route

| Question | Source evidence | Finding / limit |
|---|---|---|
| What is R2 tap supposed to do? | C-944 input dump; C-945 `pie4`; `RPGDodgeTiming.cpp::OnEldenRingHeavyTap` | R2 tap maps to the strong attack; prior Lead PIE observed `Ability_E_Anim_Montage`. A successful guarded contact may substitute its optional counter montage. |
| What is the R2 hold threshold? | C-944 read-back of `IMC_EldenRing`; C-945 `pie4` runtime proof; C-971 two-route follow-up | Intended mapping is 0.35 s. C-971 observed Ability_E at 0.34/0.35 on both routes and ChargedAttack at 0.70 on both, but 0.36 split: legacy ChargedAttack, data Ability_E. The ~25–32 ms game ticks bound the observation; cause remains unresolved. Raw evidence: `Docs/BossCombatReview/Execution/Claude/P_C971_ERLATENCY/SUMMARY.md`. |
| Is charged attack a separate C++ callback? | C-945 states R2 hold maps directly to `IA_ChargedAttack`; C++ `URPGDodgeTiming` handles the R2 tap replay. | The separate charged-hold route is authored in the input mapping asset; exercise both routes through the real key mapping. |
| What montage duration is guaranteed? | C-945 identifies observed montage names, but no asset length or latency distribution is stated in that mailbox result. | Do not infer duration from the control decision. Lead should record observed montage and asset duration per equipped route. |

## AA-C33 — dodge feel after disabling double-tap long roll

| Input/state | Current source behavior | Evidence limit |
|---|---|---|
| Single tap, moving | Selects the quick-roll clip; pack ability owns activation and direction. | Driver observation pending Lead PIE. |
| Single tap, standing, BackstepMontage empty | Selects quick roll; `bBackwardWithoutInput` turns the character away from camera during root motion. | This is a turn-and-roll fallback, not a backstep. |
| Standing tap, approved BackstepMontage loaded | Selects optional backstep and skips the backward turn. | ER-A1 import/owner approval and runtime proof pending. |
| Double tap within 0.30 s | `bDoubleTapLongRoll` defaults false, so it does not select `FullMontage` or force a full roll. The second press selects quick again; whether the pack accepts a second activation during the first dodge depends on its active/buffer state. | C-945 `pie4` passed the no-long-roll criterion; it did not establish that every second tap yields a second visible dodge. |
| Hold | Pack sprint behavior remains; exact trigger boundary was not independently read from the input asset. | Lead should distinguish hold-to-sprint from a tap/double tap in runtime evidence. |

## AA-C34 — proposals, contingent on evidence

1. Keep `bDoubleTapLongRoll=false`; do not re-enable the long roll while the owner-requested input feel is being evaluated.
2. Keep `BackstepMontage` empty until ER-A1 passes R4/owner review and Lead imports it; then run standing tap, repeated standing tap, and moving tap on both routes.
3. Keep the read-back 0.35 s R2 hold mapping; use the adjacent-duration probe to catch trigger-boundary or montage-selection regressions before changing it.
4. Do not import/wire ER-A2/A3 until R4 passes owner review; rerun jump+R1/R2 and record the actual attack montage, hit-window eligibility, and ground fallback.
5. Lead records build ID, route, raw PIE log, selected montage and sampled tick duration. No numeric latency acceptance threshold is proposed in this batch.

## Stale spec correction

`ER_PLAYER_CONTROLS_SPEC.md` previously described full-roll double tap as current behavior and said nothing was built. Its current-state rows now reflect the disabled default and existing optional plumbing; intended clips and runtime behavior remain gated, not accepted.

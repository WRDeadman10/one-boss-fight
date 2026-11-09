# AX-C06–C10 — KI-155 proof-profile candidate-budget audit

Date: 2026-11-09. Source/document-only review; no code or tests changed or run, no build or Unreal activity.

## Findings

| Task | Finding | Evidence / limit |
|---|---|---|
| AX-C06 | `PhasePoolCannotStarve` accepts a positive attack budget when the pool has at least that many candidates, or any finite zero-cooldown candidate; it rejects budgets below one and otherwise returns false. | `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:21-26`. This is eligibility feasibility; selector score penalties do not make a cooling candidate eligible. |
| AX-C07 | `ResolveProfile` applies the cooldown-starvation rule only inside the two-phase validation branch. | `RPGBossFrameworkProfile.cpp:218-226` gates phase membership and per-phase pool checks under `PhaseTwoFraction > 0`. The single-pool F5/PARRY path does not reach this check. |
| AX-C08 | Native tests exercise the pure helper's representative and generated cardinality cases, but the searched test source does not name the integration error token `Framework.Profile.PhaseCooldownStarvation`. | `Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp:277-295` tests `PhasePoolCannotStarve`; source search found no profile-resolution negative control for the single-pool case. This is a static search result, not evidence that no external/Blueprint test exists. |
| AX-C09 | The parry-recovery gating profile generator sets attack count to four and writes every candidate cooldown to zero, with readback/assertions; its two-card phase pool therefore passes the pure rule. | `Docs/BossCombatReview/Execution/Codex/Proofs/make_parry_recovery_gating_profile.py:16-45`; `PARRY_RECOVERY_EXPECTED.md:7`. This guards this generated proof setup, not arbitrary single-pool authored profiles. |
| AX-C10 | KI-155 remains open as a proof-profile limitation; no runtime/code defect is established by this audit. | `Documentation/KNOWN_ISSUES.md:316`. Existing guidance avoids the observed abort by using zero posture damage and attack count four. The general recommendation to validate candidate budget is not currently enforced for single-pool profiles. |

## Disposition

Source finding: single-pool profiles can pass `ResolveProfile` despite a requested attack budget larger than the candidate pool when all cooldowns are positive; multi-phase profiles have the existing pool-feasibility guard. The current parry-recovery generator explicitly avoids this condition with zero cooldowns. This is an audit result, not a proposed or authorized fix. Any behavior change or new integration test needs Lead/owner disposition. C-1150's separately requested data-route parry-observer attach test remains deferred until Lead reports the BUILD-274 result; its source file is frozen meanwhile.

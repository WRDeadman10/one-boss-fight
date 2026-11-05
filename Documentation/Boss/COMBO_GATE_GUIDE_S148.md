# Framework boss combo gate guide (S148)

This guide describes the framework boss's current combo branch boundary: when a finished card is evaluated, which state is sampled, how a graph edge is consumed, and how ordinary selector control resumes. It is source behavior, not a claim that every branch has live PIE proof.

## Gate timing and snapshot freshness

The boss starts a combo when the selected root card has started, storing the root node and baselines for lifetime accepted, guarded, and parried hit counters. A gate is evaluated only after the move executor reports the current card both finished and clean. The gate snapshot is constructed at that moment from current target and boss positions: encounter/generation/target/frame IDs, phase, world clock, planar range in cm, signed yaw in degrees, vertical separation, and valid/neutral flags. It is not the snapshot from the card's start.

The gate's outcome is computed from executor counter deltas since the current combo node started, with precedence Parried > Guarded > Hit > Whiff. The decision therefore combines current spatial context with the strongest recorded player outcome for that card. The `combo_gate` row logs gate id, source node, outcome, range, yaw, result, next node, and refusal reason; it does not log every candidate edge's individual rejection.

## Edge selection and one-use gate

`RPGBossCombo::Step` checks the current node, then the gate ID. ID 0 recovers with `Combo.GateId`; the same ID as `LastGateId` is ignored as `Combo.GateConsumed` without changing state. A new nonzero ID is written to `LastGateId` before target/range/yaw validation, so even a malformed fresh gate is consumed. The actor monotonically increments `ComboGateCounter` for each real gate. The development-only duplicate hook intentionally calls `Step` twice with the same ID and logs whether the second call was ignored with unchanged state.

After target and finite range/yaw validation, a node with no outgoing edges finishes. Otherwise edges are checked in authored order; the first whose inclusive range band, absolute-yaw limit, and optional outcome constraint match is selected. A selected edge that would exceed graph `MaxDepth` recovers with `Combo.Depth`; a gate with no matching edge recovers with `Combo.DefaultRecovery`. Profile validation separately checks graph shape/domain/depth and resolves each node MoveId against candidate cards.

## Continue, pause, and selector fallback

For `Continue`, the actor resolves the next node's MoveId to a candidate. With no tempo pause, it increments the attack count and prepares the executor, then starts the next card using the same fresh snapshot used for the gate. If prepare fails, the framework playback path fails. If the card is missing or `StartCard` refuses, the combo is disabled and the next tick returns to normal selector choice. The selector is also used after `Recover` or `Finished`, after attack-budget exhaustion, and when the duplicate gate is ignored; these results turn combo mode off and return `false` from the gate handler.

For a positive pause, the actor stores the candidate and deadline, remains neutral until that deadline, then `StartComboCard` takes a new snapshot and starts the card. A missing/invalid pending candidate or refused start disables combo mode; the ordinary between-card selector path proceeds. Thus a paused continuation starts from post-pause context, while an immediate continuation carries the gate snapshot into `StartCard`.

Other actor-level exits include arena leash, watchdog, stance break, and attack budget; these log explicit `combo_end` reasons. Combo graph validation and pure `Step` tests establish rule behavior, while actor lifecycle and fallback evidence should be interpreted from their corresponding integration tests/logs rather than inferred from pure tests alone.

## Retained trace and limits

`Docs/BossCombatReview/Execution/Claude/B_COMBO3/pie_normal/editor_raw.log:1580` starts node A. At lines 1791/1793, gate 1 uses outcome Hit, range 129.503 cm and yaw 0, continues to B and steps into the heavy slam. Lines 1986/1988 show gate 2 Whiff continuing to C. At line 2199, gate 3 returns Finished. This illustrates the logged decision sequence; it does not prove the unlogged candidate-edge checks or a recovery branch.

The combo rule tests cover duplicate consumption, zero IDs, no-match recovery, invalid target/non-finite range, and unknown node (`Source/OneBossFight/Tests/RPGBossComboTests.cpp:74-101`). The integration fallback test is `Source/OneBossFight/Tests/RPGBossComboFallbackTests.cpp`; its presence is not a substitute for a live branch-specific trace. No tests or editor run by Codex for this guide.

## Source lines for review

- `Source/OneBossFight/Player/RPGBossComboRules.h:4-8, 74-98` — graph/gate contract, gate consumption, edge selection and recovery.
- `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:570-580, 600-613` — combo initialization, clean-card gate timing, ordinary next-attack selector handoff.
- `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:754-818` — current snapshot, outcome deltas, gate, immediate/pause continuation and refusal paths.
- `Source/OneBossFight/Tests/RPGBossComboTests.cpp:74-101` — pure gate behavior tests.
- `Docs/BossCombatReview/Execution/Claude/B_COMBO3/pie_normal/editor_raw.log:1580, 1791-1793, 1986-1988, 2199` — retained normal combo trace.

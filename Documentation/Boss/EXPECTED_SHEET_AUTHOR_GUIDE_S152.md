# Expected-sheet author guide examples (S152)

An expected sheet is a test protocol and interpretation contract. Keep each assertion in one of three buckets:

- **Measured:** a raw log field or direct observation, with exact run path and line. Avoid rounding away values needed to distinguish outcomes.
- **Inferred:** a calculation or causal interpretation from measured inputs. State the rule and assumptions; do not present it as a raw log field.
- **Manual:** a check the parser cannot establish, such as collision geometry, actual input feel, or an unlogged visual condition. Name who observes it and how to record it.

Validator success means the structured lines fit registered schemas and semantic rules. It does not convert manual items into measured facts or prove an expected gameplay outcome. `proof_report.py` can check registered positive tokens and `no TOKEN` controls; untagged numeric/gameplay criteria remain manual (`Documentation/Boss/TOOLS.md:37,39`).

## Strong example: player parry stamina

Use `Docs/BossCombatReview/Execution/Codex/Proofs/PARRY_STAMINA_EXPECTED.md` as a model for a strong, bounded claim. It names the exact attribute (`Attribute.Stamina`), the non-shipping cost hook, positive and control runs, and a live gap for insufficient-stamina refusal.

**Measured:** in `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA/pie_stamina_overlay_run1/editor_raw.log`, line 1389 records `rpg.ParryStaminaCost 20`; line 1771 records `before=100 after=80 parried=0`; line 2087 records Perfect grade; line 2155 records `before=80 after=70 parried=1`. These are observations for that run.

**Inferred:** the first delta is a 20-point paid press without contact; the second delta is a 10-point net loss for a 20-point cost with half refunded on a Perfect parry. This interpretation depends on no unrelated stamina consumer changing the attribute during each interval. The pure rule and component source define the cost/refund calculation (`Source/OneBossFight/Player/RPGPlayerParry.cpp:68-83,154-158`; `Source/OneBossFight/Player/RPGParryCostRules.h:22-27`).

**Manual / still open:** confirm the test setup has no other stamina consumers and inspect the player's attribute before/after, as the sheet requests. The insufficient-stamina refusal has not been exercised live, so the example explicitly leaves that branch unproven. Do not treat `parried=0` as evidence that the press was refused or refunded.

## Honest limited-proof example: W3 strafe stuck recovery

Use `Docs/BossCombatReview/Execution/Codex/Proofs/STRAFE_STUCK_EXPECTED.md` together with the retained R3c run to model a sheet whose intended PASS is precise but whose available run does not pass it.

**Measured:** `Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/pie_r3c_run1/editor_raw.log` has three `strafe_start`, zero `strafe_stuck`, and three `strafe_end` lines. The second observed window changes logged direction at line 1955 and ends at line 2045 with `CandidateEligible`; it never emits the required `strafe_stuck flipped=1 movedRatio=<0.5>` event. Claude's C-712 review says the edge did not block the boss, which strafed normally at Y=1900.

**Inferred:** because movement was not blocked and the required token is absent, R3c does not exercise or prove the stuck-recovery branch. Its direction change alone cannot be attributed to the stuck rule; the expected sheet requires comparing it to the seeded direction. The correct disposition is failed setup / negative evidence, while the branch remains unit proven and live not proven (KI-149).

**Manual / still required:** the lead must inspect the actual nav bounds, floor edge, and boss movement capsule in the authored map; then verify a live blocked interval of at least 0.3 seconds and the emitted ratio/flip. The log's expected token parser cannot verify the physical collision setup. If the edge still permits movement, classify the attempt as invalid setup rather than code pass or code failure.

## Source and evidence references

- `Docs/BossCombatReview/Execution/Codex/Proofs/PARRY_STAMINA_EXPECTED.md:1-24` — complete strong protocol and explicit remaining branch gap.
- `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA/pie_stamina_overlay_run1/editor_raw.log:1389,1771,2087,2155` — cost command, measured deltas, Perfect grade.
- `Docs/BossCombatReview/Execution/Codex/Proofs/STRAFE_STUCK_EXPECTED.md:1-24` — intended witness, controls, and manual setup limits.
- `Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/pie_r3c_run1/editor_raw.log:1783,1955,2045` — normal strafe, direction sample, and candidate end; no stuck token in the run.
- `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:489-513`; `Source/OneBossFight/Player/RPGBossStuckRules.h:13-47` — runtime stuck gate and pure rule.

# Opt-in parry grade HUD expected sheet (Queue D151)

Status: protocol only. No HUD feature is implemented or enabled by this sheet. Claude/Lead review of the sheet and default-off behavior is required before implementation; live Editor and packaged proof remain Lead-owned.

## Claim and existing boundary

The proposed feature displays the already-computed Perfect, Good, or Late parry grade to the player. It must be observational only: toggling display must not change input acceptance, parry timing, damage, stamina, posture, recovery, boss state, or grade calculation. The pure grade boundaries come from `Source/OneBossFight/Player/RPGParryGradeRules.h`; the player component exposes the last grade in `RPGPlayerParry.cpp`. `rpg.BossOverlay` is an existing framework-boss debug overlay (`RPGFrameworkBossCharacter.cpp:48,737-748`), not evidence of a player-facing HUD. Its formatter is unit-covered, but it does not prove an authored widget or a live display.

No grade thresholds, colors, animation, placement, duration, or persistence policy are selected here. Those presentation choices need Lead/owner direction if implementation requires them.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw log path, log SHA-256 | **Expected:** unique ID per paired run; preserve raw logs and bind the hash after capture. **Observed:** pending. |
| Build / executable / map | **Expected:** exact build identity and `/Game/OneBossFight/Levels/L_SevarogArena`; **Observed:** pending. Fail setup on wrong map or unknown build identity. |
| Player, controller, parry component | **Expected:** actual possessed player and the component receiving the real parry input; record class/instance identity and input route. **Observed:** pending. |
| Feature state | **Expected:** explicit feature toggle and read-back showing default off before any enable action; record all relevant CVars/config. **Observed:** pending. |
| Test condition | **Expected:** controlled, repeatable attacker/contact and a clean reset between runs. Record unrelated damage/resource sources and suppress them where possible. **Observed:** pending. |
| Grade acquisition | **Expected:** actual combat contact must produce each requested grade; record opening/contact times and grade source. Do not synthesize a grade as a live witness. **Observed:** pending. |

## Paired rows

Run each grade pair from the same recorded baseline. Keep attack, player/boss identities, profile, parry input timing, and relevant random seed the same; change only the display toggle. Repeat separate pairs for Perfect, Good, and Late.

| Pair | Setup | Required observation | Pass condition |
|---|---|---|---|
| Hidden control — Perfect / Good / Late | Feature is default-off and read back off; perform the real parry at a timing that produces the named grade. | Capture the computed grade, parry result, player/boss state, health, stamina, posture, recovery, and raw-log references. Record that no new player-facing grade text is visible. | The expected grade is produced; no proposed HUD text is visible; baseline gameplay values are recorded. |
| Enabled — Perfect / Good / Late | Repeat the matching control setup and timing with only the reviewed display toggle enabled. | Capture the same fields plus a direct screen observation/screenshot showing the named grade text and when it appears/disappears. | Displayed text matches the computed grade; all gameplay outcome fields match the paired control within the documented repeatability of the encounter. No gameplay-state mutation is attributable to display. |
| Negative — no accepted parry / None | Perform a non-parry contact or an attempt that produces no valid grade, under both feature states. | Record no-contact/refusal reason, component grade, and screen state after prior grade text has cleared. | No false Perfect/Good/Late text appears, and prior text does not linger past the reviewed clear condition. Treat invalid setup/no contact as inconclusive, not a pass. |

## Evidence and interpretation

- **Measured:** the computed grade and combat fields from source-tokenized log rows; actual visible text from a screenshot or direct Lead observation. Record file and line/time for every measured log item.
- **Inferred:** a paired gameplay equivalence conclusion only when both runs start from equivalent identity/state and unrelated state mutations are excluded. State any tolerances and confounders.
- **Manual:** whether the text is legible, appears at the intended place/time, is not obscured, and clears at the approved point. A log token cannot establish visual presentation.
- Existing `parry_grade` debug output and `rpg.BossOverlay` are not a player-facing HUD witness. Existing formatter tests are not feature or runtime proof.

## Failure and stop conditions

Fail the feature row if the default is enabled, display text disagrees with the computed grade, text appears for an invalid/no-grade outcome, or any gameplay field/transition changes with display enabled. Stop and report if the toggle cannot be read back, the paired baseline cannot be reproduced, unrelated damage/resource changes cannot be isolated, the feature requires an unreviewed gameplay threshold or presentation decision, or the grade cannot be produced through real input/contact. Keep missing evidence UNKNOWN; do not infer a pass from the debug overlay alone.

## Verification boundary

This is an expected protocol only. No source/UI changes, test/build/editor execution, screenshots, or runtime claims are included. The sheet does not authorize the feature implementation; implementation follows only after the sheet and default-off behavior are reviewed.

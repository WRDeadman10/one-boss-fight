# ER-C4: owner hand-test sheet

Run in `L_SevarogArena` with a gamepad. Use the names in parentheses for the matching XInput controls. For boss-contact rows, face the boss and test one input at a time. Record any unexpected animation, tag, health, or stamina change in Notes. Mark a row only after performing it; rows marked **After clip lands** are pending animation delivery and wiring.

| Control | What to press | Expected result | Result | Notes |
|---|---|---|---|---|
| Dodge tap, moving | Hold the left stick in a direction and tap dodge once (`Gamepad_FaceButton_Right`, Xbox B). | A quick roll in the chosen direction; no turn-away backstep. | [ ] Pass  [ ] Fail | |
| Dodge tap, standing / backstep — **After ER-A1 clip lands** | Keep the left stick neutral and tap dodge once (`Gamepad_FaceButton_Right`, Xbox B). | `Backstep_Back` moves straight backward while the character keeps facing the same way; no turn and no roll. | [ ] Pass  [ ] Fail | |
| Hold dash | Hold dodge (`Gamepad_FaceButton_Right`, Xbox B) while steering with the left stick for longer than the hold threshold, then release. | Sprint starts while held and stops on release; no long roll. | [ ] Pass  [ ] Fail | |
| Double tap | With the stick neutral, tap dodge twice quickly (`Gamepad_FaceButton_Right`, Xbox B). | Does not play the long-roll montage. Record whether the two inputs produce one or two quick actions. | [ ] Pass  [ ] Fail | |
| Ground light attack (R1) | Tap attack once (`Gamepad_RightShoulder`, Xbox RB). | Light attack starts on press and uses the ground light chain. | [ ] Pass  [ ] Fail | |
| Ground strong attack (R2 tap) | Tap attack briefly (`Gamepad_RightTrigger`, Xbox RT); release before the 0.35 s hold threshold. | Strong attack plays; charged attack does not. | [ ] Pass  [ ] Fail | |
| Charged attack (R2 hold) | Hold attack (`Gamepad_RightTrigger`, Xbox RT) for at least 0.35 s, then release. | Charged attack plays. | [ ] Pass  [ ] Fail | |
| Jump light — **After ER-A2 clip lands** | Jump (`Gamepad_FaceButton_Bottom`, Xbox A); while airborne, press R1 (`Gamepad_RightShoulder`, Xbox RB). | Unique airborne diagonal light slash plays, distinct from the ground light clip. | [ ] Pass  [ ] Fail | |
| Jump heavy — **After ER-A3 clip lands** | Jump (`Gamepad_FaceButton_Bottom`, Xbox A); while airborne, hold R2 (`Gamepad_RightTrigger`, Xbox RT) through the charged threshold. | Unique overhead plunge plays and reads through landing, distinct from the ground heavy clip. | [ ] Pass  [ ] Fail | |
| Guard (L1) | Face the boss and hold guard (`Gamepad_LeftShoulder`, Xbox LB) through an incoming attack. | Guard stance is active; a front-facing contact produces the block response and its expected health/stamina outcome. | [ ] Pass  [ ] Fail | |
| Parry (L2) | Tap parry (`Gamepad_LeftTrigger`, Xbox LT) as a boss strike is about to connect. Try a few timings around impact. | A correctly timed input produces the parry response; early/late attempts are not passes. | [ ] Pass  [ ] Fail | |
| Guard counter — **After ER-A4 clip lands and Lead wiring is present** | Hold L1 (`Gamepad_LeftShoulder`, Xbox LB) to block a strike, then tap R2 (`Gamepad_RightTrigger`, Xbox RT) promptly after the successful block. | The dedicated forward-stepping guard-counter clip plays and the counter hit is registered. Use the Lead's integrated window; do not treat the proposed 0.60 s value as an accepted target. | [ ] Pass  [ ] Fail | |

## Recording

- Test build / ID: ______________________________
- Controller and connection: _____________________
- Tester / date: _________________________________
- Unexpected behavior or reproduction steps: ______________________________________________

The project input dump maps dodge to `Gamepad_FaceButton_Right`, jump to `Gamepad_FaceButton_Bottom`, guard to `Gamepad_LeftShoulder`, and parry to `Gamepad_LeftTrigger` (`Docs/BossCombatReview/Execution/Claude/ER_INPUT_DUMP/run1/editor_raw.log:1281-1307`). The ER mapping dump records R1 light on `Gamepad_RightShoulder`, R2 tap on `Gamepad_RightTrigger`, and R2 hold for charged attack (`Docs/BossCombatReview/Execution/Claude/ER_INPUT_DUMP/update2/editor_raw.log:1309-1311`). Backstep, jump clips, and guard-counter animation rows stay pending until their clips land.

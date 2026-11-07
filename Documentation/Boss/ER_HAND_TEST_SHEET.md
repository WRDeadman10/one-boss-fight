# ER-C4: owner hand-test sheet v2

Run in `L_SevarogArena` with a gamepad on a Lead-built test version. Use the names in parentheses for matching XInput controls. For boss-contact rows, face the boss and test one input at a time. Record unexpected animation, tag, health, or stamina changes in Notes. Mark a row only after performing it. All four ER clips and montages are present and trimmed to accepted lengths (A-589/A-590), but Claude accepted delivery only for owner review; owner video review and optional saved-asset assignments are pending. Asset existence alone does not pass an animation row.

| Control | What to press | Expected result | Result | Notes |
|---|---|---|---|---|
| Dodge tap, moving | Hold the left stick in a direction and tap dodge once (`Gamepad_FaceButton_Right`, Xbox B). | A quick roll in the chosen direction; no turn-away backstep. | [ ] Pass  [ ] Fail | |
| Dodge tap, standing / backstep — **After owner review + field assignment** | Keep the left stick neutral and tap dodge once (`Gamepad_FaceButton_Right`, Xbox B). | With `BackstepMontage` assigned, `Backstep_Back` moves straight backward while facing stays unchanged; no turn and no roll. Empty field retains pack behavior. | [ ] Pass  [ ] Fail | |
| Hold dash | Hold dodge (`Gamepad_FaceButton_Right`, Xbox B) while steering with the left stick for longer than the hold threshold, then release. | Sprint starts while held and stops on release; no long roll. | [ ] Pass  [ ] Fail | |
| Double tap | With the stick neutral, tap dodge twice quickly (`Gamepad_FaceButton_Right`, Xbox B). | Does not play the long-roll montage. Record whether the two inputs produce one or two quick actions. | [ ] Pass  [ ] Fail | |
| Ground light attack (R1) | Tap attack once (`Gamepad_RightShoulder`, Xbox RB). | Light attack starts on press and uses the ground light chain. | [ ] Pass  [ ] Fail | |
| Ground strong attack (R2 tap) | Tap attack briefly (`Gamepad_RightTrigger`, Xbox RT); release before the 0.35 s hold threshold. | Strong attack plays; charged attack does not. | [ ] Pass  [ ] Fail | |
| Charged attack (R2 hold) | Hold attack (`Gamepad_RightTrigger`, Xbox RT) for at least 0.35 s, then release. | Charged attack plays. | [ ] Pass  [ ] Fail | |
| Jump light — **After owner review + AirLightMontage assignment** | Jump (`Gamepad_FaceButton_Bottom`, Xbox A); while falling, press R1 (`Gamepad_RightShoulder`, Xbox RB). | Optional air-light montage plays; empty field retains pack falling route. Verify grounded R1 works after montage completion. | [ ] Pass  [ ] Fail | |
| Jump heavy — **After owner review + AirHeavyMontage assignment** | Jump (`Gamepad_FaceButton_Bottom`, Xbox A); while falling, use the R2 strong-tap route. | Optional air-heavy montage plays; empty field retains pack strong route. Verify grounded R2 works after montage completion. | [ ] Pass  [ ] Fail | |
| Guard (L1) | Confirm health and stamina are above zero. Face the boss and hold guard (`Gamepad_LeftShoulder`, Xbox LB) through an incoming attack. | Guard stance is active; a front-facing contact produces the block response and its expected health/stamina outcome. Record the player animation and health/stamina before and after contact. | [ ] Pass  [ ] Fail | |
| Parry (L2) | Tap parry (`Gamepad_LeftTrigger`, Xbox LT) as a boss strike is about to connect. Try a few timings around impact. | A correctly timed input produces the parry response; early/late attempts are not passes. | [ ] Pass  [ ] Fail | |
| Guard counter — **After owner review, field assignment, and Lead build** | Confirm health/stamina above zero. Hold L1 (`Gamepad_LeftShoulder`, Xbox LB) through a front-facing strike that visibly blocks, then tap R2 (`Gamepad_RightTrigger`, Xbox RT) promptly after contact. | The assigned counter montage plays and its hit registers. A held guard without successful blocked contact is not a valid setup. Use the integrated window; 0.60 s is a proposal, not an owner-approved target. | [ ] Pass  [ ] Fail | |

## Recording

- Test build / ID: ______________________________
- Controller and connection: _____________________
- Tester / date: _________________________________
- Unexpected behavior or reproduction steps: ______________________________________________

The project input dump maps dodge to `Gamepad_FaceButton_Right`, jump to `Gamepad_FaceButton_Bottom`, guard to `Gamepad_LeftShoulder`, and parry to `Gamepad_LeftTrigger` (`Docs/BossCombatReview/Execution/Claude/ER_INPUT_DUMP/run1/editor_raw.log:1281-1307`). The ER mapping dump records R1 light on `Gamepad_RightShoulder`, R2 tap on `Gamepad_RightTrigger`, and R2 hold for charged attack (`Docs/BossCombatReview/Execution/Claude/ER_INPUT_DUMP/update2/editor_raw.log:1309-1311`). C-977 sends all four delivered clips to owner review; import/montage presence does not close owner approval or saved-field assignment gates.

## v2 block-probe note

Owner C-953 confirmed L1 guard works in normal play; the old probes are invalid, not evidence of a guard defect (see `Documentation/Boss/AA_C06_BLOCK_PROBE_CLASSIFICATION.md`). Before recording guard or counter results, verify positive health/stamina and observe the player-side animation plus guard-state tags at actual contact. C-977 sends ER-A4 to owner review; A-589 reports the montage trimmed to 0.8000 s. Owner approval, field assignment, and Lead build remain prerequisites.

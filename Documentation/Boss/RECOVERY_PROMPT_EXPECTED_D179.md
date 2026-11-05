# Opt-in player recovery prompt expected sheet (Queue D179)

Status: protocol only. No prompt or feature is implemented/enabled. Review default-off behavior, wording and trigger before implementation. Live Editor/packaged proof remains Lead-owned. This protocol makes no claim that player input is automated or that a prompt improves input timing.

## Claim and recovery-state boundary

The proposed prompt appears only when the player reaches the exact approved recovery state and clears when that state ends. Display must not change recovery duration, input binding, input acceptance, attack/parry state, resources, or gameplay. A prompt is informational; the player acts through the existing input route. No recovery label, input timing target, or product wording is approved here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, logs/screens/video and hashes | **Expected:** unique ID and immutable evidence hash. **Observed:** pending. |
| Build/map/player/input | **Expected:** exact build, `/Game/OneBossFight/Levels/L_SevarogArena`, possessed player/controller and real input binding. **Observed:** pending. |
| Recovery state | **Expected:** exact source state/transition event, entry/exit timestamps, generation and recovery configuration read back. **Observed:** pending. |
| Feature state | **Expected:** prompt toggle read back off by default; enabled only in paired run. **Observed:** pending. |
| Input behavior | **Expected:** record existing manual input sequence and accepted action. Do not inject/automate input or claim an automation test. **Observed:** pending. |

## Paired cases

Repeat the same recovery scenario with prompt hidden/enabled. The only change is the reviewed prompt toggle; use manual input through the ordinary binding in both runs.

| Row | Required evidence | Pass condition |
|---|---|---|
| Hidden control | Capture exact recovery state transitions, input and screen with prompt off. | Prompt absent; recovery/input behavior establishes baseline. |
| Enabled recovery prompt | Repeat; record state entry, text/visibility timestamps and the same manual input result. | Prompt appears only after exact recovery-state entry and clears on exit; input acceptance and recovery timing match control. |
| Outside recovery | Exercise a state before recovery, after recovery, and an abort/reset route. | No prompt appears outside the approved state; stale prompt clears on abort/restart. |
| Input guard | Capture player input binding/action and accepted action under both conditions. | Prompt neither triggers nor consumes input, and no input automation is inferred from visual/log evidence. |

## Evidence interpretation and limits

- **Measured:** state, generation, timestamps, real input event/result and relevant gameplay values with raw references; prompt visibility from screenshot/video.
- **Inferred:** prompt-state correctness only when source state identity is independently recorded; a visible prompt does not prove the underlying recovery state.
- **Manual:** wording clarity, legibility, timing usefulness and whether it obscures combat.
- This sheet does not establish an automated input test, player response time, or usability outcome. No source-state mapping or player-facing text is approved yet.

## Failure and stop conditions

Fail if default-on, prompt appears outside recovery, persists after exit/reset, changes input/recovery behavior, or consumes/automates input. Stop if the exact recovery state cannot be identified, input route differs between pairs, or copy/trigger choices need review. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No prompt/source/UI changes, tests/build/Editor run, input automation, or runtime claims. Implementation is not authorized before review.

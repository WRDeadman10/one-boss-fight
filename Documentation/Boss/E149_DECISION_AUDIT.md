# E149 decision audit: cooldown clock regression policy

Queue E incorrectly tags this selector-clock question as D17; D17 is the parry timing-boundary audit. The matching selector source/test scope is D5 and the route regression fixture E75. Queue E is corrected to point there.

`FRPGBossMoveSelector::Select` refuses a model-ineligible stale snapshot before cooldown scoring (`MoveModel.StaleDecision`). When a snapshot clock regresses without a stale model refusal, the cooldown expression is `S.ClockSeconds - LastStartClock[I] < CooldownSeconds`; the selector has no independent monotonic-clock token. Encounter route tests prove a regressed snapshot is refused by the model, with no chosen card. The existing policy is therefore fail closed at the model route boundary; no additional product decision is needed for that behavior.

Decision owner for changing clock ownership or allowing recovery after a regression: project owner, with Lead review. Static inspection only; no tests/build/Editor run.

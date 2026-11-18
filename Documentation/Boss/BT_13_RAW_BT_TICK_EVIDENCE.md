# BT-13 — Raw BehaviorTree attack-task tick evidence

Date: 2026-11-16
Status: false telemetry removed; raw attack-task tick count remains blocked.

## Lead review

Antigravity's A-1009 implementation logged `bt_attack_ticks=0` from a local integer initialized to zero. The value was not connected to a BehaviorTree task callback or runtime counter. The PIE driver parsed that literal and treated it as measured zero, which could incorrectly clear the acceptance blocker. Suppression before BeginPlay is useful lifecycle evidence for placed actors, and `StopMovement`/`StopLogic` are useful safeguards, but neither is a raw attack-task execution counter. Runtime-spawn callback timing also cannot be promoted to a measured task count without evidence from the actual task execution path.

Codex removed the hard-coded field from suppression logs and removed the driver's optional numeric capture. The receipt now retains `BLOCKED_NOT_INSTRUMENTED` unless a real count is observed; suppression still stops controller movement/brain logic before destruction. Static contract assertions were updated to prevent a hard-coded zero from returning. The contract was not run. Antigravity's reported 22/22 result predates this correction and is not independent evidence.

## Why the criterion remains blocked

The project source does not contain the pack's attack-task implementation or an existing task-execution counter. A `UBrainComponent::StopLogic` call cannot count task ticks that already occurred. A valid counter must observe the actual BehaviorTree attack task's execution/tick callback (or an approved equivalent) and be included in the route receipt. Adding telemetry only at actor suppression would repeat the false-positive failure.

Safe path: identify the actual pack attack-task class and an allowed project-owned instrumentation seam, or obtain approval for an equivalent instrumented project-owned task. Do not edit vendor pack assets or claim zero based only on `began_play=0`, montage state, or stopping the brain. Until then route Smoke must preserve the raw tick criterion as blocked.

No tests, build, Editor, PIE, asset write, commit or push were performed for this correction.

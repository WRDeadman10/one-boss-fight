# Animation Notify Contracts (UE 5.5 reference)

## `AN_BossCommit`

**Parent:** AnimNotify. Reads owning mesh actor; resolves `BPC_AttackExecutor` and calls `OnAttackCommit(CurrentInstanceID)`. Sets/adjusts turn lock. The instance ID should be validated against currently playing montage and expected attack section. Do not call `SetActorRotation` here.

## `ANS_BossHitWindow`

**Parent:** AnimNotifyState. `Begin`: open named window via executor; trace component caches weapon socket transforms and initializes hit victim set. `Tick`: request weapon-path sample (or allow the executor's own Tick to do this while active). `End`: close named window. **If montage ends or blends out unexpectedly, the executor closes all windows regardless of whether Notify End fired.**

## `AN_BossComboGate`

**Parent:** AnimNotify. Call `Executor.OnComboGate(GateName)` once; executor builds context, scores only allowed graph outgoing edges; then requests Montage Next Section or next montage. Never pick an arbitrary move from the full pool at a combo gate.

## `ANS_BossTrackingWindow`

**Parent:** AnimNotifyState. Enables capped early facing or Motion Warping updates; when ending commits attack heading or reduces turn cap. Do not continue warping the target throughout active damage.

## `AN_BossRecoveryBegin`

Starts recovery lock if defined by executor/section; do not use a naive `Delay` node to end recovery while also letting Montage end events unlock, as duplicate unlocks result.

## `ANS_BossArmorWindow`

Applies/removes interruption resistance tags. If interruption or death occurs, executor forcibly clears them to avoid permanent hyperarmor.

## Key implementation principle

**Editor-friendly notifies initiate events, but gameplay authoritativeness lives in the executor.** All notifies should be idempotent or safely rejected if stale, duplicated, wrong state, or wrong montage.

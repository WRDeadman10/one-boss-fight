# Queue D126 — move-model refusal precedence audit

Date: 2026-11-03  
Method: static review of `FRPGBossMoveModel::IsEligible` and current automation assertions; no tests run.

## Stable first-refusal order

`IsEligible` resets `Error`, then returns the first matching refusal in this order:

1. uninitialized or encounter/generation mismatch → `MoveModel.Generation`;
2. missing or invalid compiled card → `MoveModel.Card`;
3. invalid/zero target → `MoveModel.Target`;
4. non-neutral snapshot or model not Idle → `MoveModel.State`;
5. invalid clock/range/yaw/vertical snapshot domain → `MoveModel.SnapshotDomain`;
6. phase mismatch → `MoveModel.Phase`;
7. outside card range → `MoveModel.Range`;
8. cone/hysteresis rejection → `MoveModel.Cone`;
9. above a configured nonzero vertical limit → `MoveModel.Vertical`;
10. reused/non-increasing frame or backwards decision clock → `MoveModel.StaleDecision`.

Start adds `MoveModel.InstanceExhausted` after eligibility succeeds. `Start` clears output token and events before validation. These are distinct lifecycle effects rather than additional eligibility precedence.

## Coverage / gap

`RPGBossMoveModelTests.cpp` exercises individual valid/invalid eligibility paths and several stale/state cases. I found no focused multi-invalid-input test pinning two competing refusals to the earlier token. Current behavior is deterministic from the source sequence, but reordering checks could silently change diagnostics. A minimal test proposal should pair generation/card, card/target, target/state, state/domain, domain/phase, phase/range, range/cone, cone/vertical, and vertical/stale, asserting the earlier listed token. Keep each fixture otherwise valid enough to reach the intended competing checks.

## Limits

No behavior change proposed. This is a diagnostic-contract audit only; automation was not run.

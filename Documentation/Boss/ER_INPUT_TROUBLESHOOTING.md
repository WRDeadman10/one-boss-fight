# QA input troubleshooting: ER-style controls

Use a Lead-built test build in `L_SevarovArena`. Capture the build ID, route (legacy/data), player pawn, input device, current montage, and relevant log lines. This guide identifies evidence to collect; it is not a substitute for PIE acceptance.

```text
Start
  |
  +-- Is the expected local player possessed and alive, with positive health/stamina?
  |     No -> fix the test setup; don't classify an input or guard result.
  |     Yes
  |
  +-- Is the log present: "Elden Ring input context ... active"?
  |     No -> inspect local PlayerController/Enhanced Input subsystem, context asset load,
  |           and component retry/bind state. Context load failure leaves pack attacks active.
  |     Yes
  |
  +-- Does R1 / R2 produce its action count and expected route?
  |     R1 = Gamepad_RightShoulder -> light.
  |     R2 tap = Gamepad_RightTrigger -> strong; R2 hold -> charged.
  |     No -> inspect mapping/action bind and retain the input log plus active montage.
  |     Yes
  |
  +-- Was the player falling when R1/R2 was pressed?
  |     Yes -> with optional AirLight/AirHeavy assigned, expect its montage;
  |            when empty, pack route is expected. After montage ends and landing,
  |            test grounded R1/R2 to check array restoration (Lead probe).
  |     No -> expect the equipped pack ground montage.
  |
  +-- Did a counter attempt follow a successful guarded contact?
  |     No -> it is not a guard-counter test. L1 hold alone or a parry is insufficient.
  |     Yes -> tap R2; record elapsed game time, counter/fallback montage, and hit result.
  |            The configured 0.60 s value is proposal-level until owner tuning approval.
  |
  +-- Was dodge tapped with neutral movement?
        Empty BackstepMontage -> pack standing-dodge behavior is expected.
        Assigned and owner-reviewed BackstepMontage -> expect backstep; verify facing.
        Direction held -> expect the ordinary directional roll; dodge hold is sprint.
```

If death/reset happens while an attack montage is active, record it as an open lifecycle observation: current Source does not prove montage cancellation for that path. Do not mark the scenario passed based only on boss-side death/reset behavior.

## Canonical controls

- Dodge/sprint: `Gamepad_FaceButton_Right` (Xbox B), tap / hold.
- Jump: `Gamepad_FaceButton_Bottom` (Xbox A).
- Guard: L1 `Gamepad_LeftShoulder` (Xbox LB); parry: L2 `Gamepad_LeftTrigger` (Xbox LT).
- Light: R1 `Gamepad_RightShoulder` (Xbox RB); strong tap / charged hold: R2 `Gamepad_RightTrigger` (Xbox RT).
- See [`AB_C36_C39_CONTROL_ANIMATION_RECONCILIATION.md`](AB_C36_C39_CONTROL_ANIMATION_RECONCILIATION.md) for guard/parry/counter distinctions and [`ER_HAND_TEST_SHEET.md`](ER_HAND_TEST_SHEET.md) for acceptance rows.

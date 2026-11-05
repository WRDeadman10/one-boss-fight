# Parry recovery live proof

## Setup

For grade amounts, run `make_parry_recovery_no_posture.py` from Claude's `B_PARRY_RECOVERY` setup. It copies the PARRY profile, sets `parry_recovery_scale=1`, `parry_posture_amount=0`, and `parry_grade_scale=False`, then saves the source map under a new name. The posture cost is zero so the parry does not break posture and abort the card before recovery can be observed. Compare against a matched PARRY control with recovery scale 0. Have the player parry the same boss card at Perfect, Good, and Late offsets; keep card and play rate identical.

For next-card gating, run `make_parry_recovery_gating_profile.py`. It uses the same PARRY/no-posture setup, sets `attack_count=4`, and sets every candidate `cooldown_seconds` to 0 s so the two-card phase pool satisfies `PhasePoolCannotStarve` and the next-card gate can be observed. The earlier two-attack setup ended at its attack budget and could not witness the gate.

## PASS

- Each successful parry emits `[FrameworkProof] parry_recovery grade=<n> extra=<seconds>` (`RPGFrameworkBossCharacter.cpp:593`).
- Grade encoding from `RPGParryGrade::EGrade` is Perfect=1, Good=2, Late=3. With profile scale 1, extra recovery is clamped from the card's remaining recovery duration times 0.65, 0.45, and 0.25 respectively (`RPGBossRecoveryWindowRules.h:19–45`). Thus Perfect ≥ Good ≥ Late, and values are positive.
- Control map has no positive `parry_recovery` extra; scale zero is explicitly off.
- In the four-attack gating profile, compare engine log timestamps: the next `[FrameworkProof] decision attack=3` must be at or after the `[FrameworkProof] parry_recovery` line timestamp plus its `extra` value. The recovery token is emitted when the post-card delay begins (`RPGFrameworkBossCharacter.cpp:590–597`); this gives a conservative observable gate check without assuming a logged contact timestamp.

## Control

Use the matched recovery-scale-zero profile; it should report no positive `parry_recovery` extension for the same card and parry grades.

## FAIL

- Missing grade line for a confirmed parry, nonpositive enabled duration, ordering violation, enabled/control mismatch, or attack 3 decision before the logged recovery interval ends.
- A late contact outside the parry window or a different card/play rate is not a valid comparison.

## Validator

`python -I Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py <editor_raw.log>`

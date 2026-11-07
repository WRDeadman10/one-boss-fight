# Lead PIE: ER control latency (pie_er_control_latency.py), 2026-11-07

The editor ran PIE with -nosound and a Lead ENGINE_LOCK, at about 35 fps (tick 25-32 ms). The values below are key-down to first observed player montage, bounded by the game tick. They are not device latency.

| Case | Legacy montage / ms | Data (DA_Sevarog_G044) montage / ms |
|---|---|---|
| R1 tap | Attack_PrimaryA / 87 | Attack_PrimaryA / 87 |
| R2 tap | Ability_E / 172 | Ability_E / 172 |
| R2 hold 0.34 s | Ability_E / 373 | Ability_E / 395 |
| R2 hold 0.35 s | Ability_E / 401 | Ability_E / 393 |
| R2 hold 0.36 s | ChargedAttack / 357 | Ability_E / 393 |
| R2 hold 0.70 s | ChargedAttack / 382 | ChargedAttack / 367 |
| jump + R1 | Attack_PrimaryA / 84 | Attack_PrimaryA / 85 |
| jump + R2 | Ability_E / 171 | Ability_E / 165 |
| dodge standing | Dodge_Small_Forward_Roll / 153 | Dodge_Small_Forward_Roll / 141 |
| dodge moving | Dodge_Small_Forward_Roll / 142 | Dodge_Small_Forward_Roll / 138 |
| dodge double tap | Dodge_Small_Forward_Roll / 84, no long roll | Dodge_Small_Forward_Roll / 80, no long roll |

Reading:
- The routes match. The 0.36 s hold differs because the hold threshold is quantized to one tick (about 28 ms), so 0.35-0.37 s is a coin flip in a 35 fps editor.
- R2 tap and dodge fire on release, so their delay is the 0.12 s hold plus one or two ticks. This is expected: tap/hold disambiguation, and the Elden Ring dodge also triggers on release.
- The air attacks play the ground clips: no air montage fields exist yet.
- The standing dodge plays the roll because BackstepMontage is empty by default.
- The double tap gives the quick roll (bDoubleTapLongRoll=false).

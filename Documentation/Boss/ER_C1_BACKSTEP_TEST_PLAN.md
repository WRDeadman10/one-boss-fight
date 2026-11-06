# ER-C1 backstep integration test plan

**Status:** planned runtime checks; the optional `Backstep_Back` clip has not yet been imported. BUILD-235 passed 478/478 before the ER-C2 rule test was added. The new automation registration needs to be included in the next Lead build; Codex has not built or run Unreal.

## Preconditions

- Import the approved ER-A1 `Backstep_Back` montage through the Lead-owned Editor workflow and assign it to `URPGDodgeTiming.BackstepMontage` on the player.
- Record the montage asset path, configured `BackstepPlayRate`, and the player's starting yaw and dodge counters for each case.
- Run the existing 478-test baseline plus `OneBossFight.Player.DodgeInputRules`; record the actual automation totals and build identity.

## Cases

| Case | Setup and input | Expected result |
|---|---|---|
| Legacy fallback | Leave `BackstepMontage` empty; tap dodge while standing | Existing roll/turn path remains in use; `GetBackstepCount` does not increase. |
| Standing tap | Assign the clip; tap once with last movement-input magnitude below `NoInputThreshold` | Stage becomes `Backstep`; backstep count increases by one; actor facing and backward-turn count stay unchanged. |
| Repeated standing taps | With the clip assigned, tap standing three times, including taps inside `DoubleTapWindow` | Every tap selects a backstep; the second standing tap does not become a full roll. Count increases once per tap. |
| Moving tap | With the clip assigned, provide direction input at or above `NoInputThreshold`, then tap | Existing directional quick-roll behavior remains; no backstep count or standing turn is added. |
| Moving double tap | Repeat the moving tap inside `DoubleTapWindow` | Existing full-roll selection and interruption behavior remain unchanged. |
| Full roll already active | Start a moving double-tap full roll, then press dodge while the roll is active | The full roll is not interrupted by a standing backstep selection. |
| Hold | Hold dodge through the pack sprint threshold | Existing sprint behavior remains unchanged. |
| Stamina | Compare the same dodge ability's cost path for a roll and a backstep | Both choices continue through the pack ability's existing stamina cost; no second cost or Codex-authored override is introduced. |

## Evidence to retain

For each runtime case, retain the build/run ID, configured montage path and rate, input direction magnitude, before/after yaw, `GetStageName`, backstep/turn/press counters, and relevant ability/stamina log lines. Verify facing after the backstep montage completes as well as at activation. Any montage timing or stamina interpretation not directly observable in the retained evidence stays labeled **PROPOSAL**.

# C-1651 SFX-36..40 Combat UI and Feedback Trigger Audit

**Status:** Source-only lead audit. Candidate selection and serialized pack Blueprint behavior remain unverified; no wiring or runtime validation.

| SFX | Proposed event | Native seam and evidence | Lead assessment |
|---|---|---|---|
| 36 | Target lock acquire | `Source/OneBossFight/Player/RPGCameraRig.cpp:327-393` implements optional camera framing around a discovered pack boss and loads a look input; no native `IA_LockOn` acquire dispatcher appears in this component. | Native camera framing is not evidence of a user-driven acquire edge. Need the selected pack input/target-lock Blueprint path before attaching a one-shot UI cue. |
| 37 | Target retarget | The same camera code tracks `LockOnTarget` (`RPGCameraRig.cpp:387-390`) and eases camera yaw (`:406-419`); the actor is the discovered pack boss, rather than a native target-cycle callback. | No confirmed target-switch event was located in project C++. Avoid triggering on camera updates, which could repeat during every tick. |
| 38 | Player low-stamina panting | `Source/OneBossFight/Player/RPGSwingTracker.cpp:218-225,265-278` writes stamina for swing costs/refunds; `Source/OneBossFight/Player/RPGPlayerParry.cpp:80-112,202-230` applies or refunds parry costs. | These are discrete cost operations, not a shared threshold crossing signal. Low-stamina loop needs a de-duplicated threshold edge plus recovery/death cleanup and a confirmed chosen-player voice profile. |
| 39 | Player critical-health pulse | `Source/OneBossFight/Player/RPGDamageResolver.cpp:151-178,212-222` reads before/after health and records accepted damage, but does not dispatch audio. | Accepted player damage is a potential transition seam; it must distinguish crossing below the threshold from repeated damage while already low, and stop/reset on heal, death, or encounter restart. Pack effects remain unverified. |
| 40 | Player defeat stinger | `Source/OneBossFight/Player/RPGBuildLoadout.cpp:573-576` can query whether player health is <= 0 for build validation; `RPGDamageResolver.cpp:178` records lethal outcome. Native `RPGBossDeath` handles the boss and is not the player's `GA_PlayerDeath` callback. | No native player-death audio dispatcher was found. The candidate trigger is pack ability-owned unless Blueprint evidence confirms otherwise; use exactly one terminal edge and coordinate music duck/one-shot behavior only after selected-route review. |

## Cross-cutting notes

- No sound playback dispatch was found in the inspected camera, stamina-cost/refund, health resolver, or player death-related C++ paths. This is a bounded source review; it does not rule out pack Blueprint or montage-notify audio.
- Lock acquire and target retarget must be separate events; camera framing alone should not synthesize either one.
- Low-stamina/critical-health loops require start/stop state edges, not repeated threshold polling or repeated damage/cost callbacks.
- No project source/assets/config changed. No audio export, tests, Editor/build/PIE, or cue wiring was performed.

## Next

Antigravity owns BT-145..BT-149 package-only candidate verification and should continue without waiting for this audit. Owner-pick/export and wiring holds remain in force.

# C-1651 SFX-21..25 Player Defense Trigger Audit

**Date:** 2026-11-18
**Scope:** Read-only source audit. No project/source/assets/config changes, tests, Editor, build, or PIE.

| Item | Source evidence | Lead finding / safe seam after Owner pick |
|---|---|---|
| SFX-21 Shield block | `RPGDodgeTiming.cpp:85-133` observes the pack `GA_BlockReaction` and `Status.Blocking` edge for guard-counter timing; it does not dispatch sound. `RPGPlayerParry.cpp` owns the native parry window and visuals, not standard block audio. | The actual standard block animation/audio remains pack Blueprint behavior and is not read back here. Avoid overlaying a new thud until the active pack block reaction and any baked cue are inspected. |
| SFX-22 Glancing deflect | `RPGPlayerParry.cpp:145-170` accepts parry rewards, counts the event, and spawns a configured parry spark. No SoundCue dispatch appears in that reward path. | This is a verified native perfect/good/late parry event seam, not proof of a distinct glancing/partial block event. Confirm the intended grade and active pack response before tying the candidate to it. |
| SFX-23 Flask recovery | `RPGBossHealPunish.cpp:247-259` detects the rising edge of `DrinkingPotion_Montage` as heal start. No player recovery sound dispatch is shown. | Montage start is a source-level signal but may precede the actual heal effect. Prefer the confirmed flask-consume/recovery event if available; inspect notifies/Blueprint behavior under approved readback before integration. |
| SFX-24 Dodge-roll foley | `RPGDodgeTiming.cpp:560-568` applies the backstep montage; the normal pack dodge remains a separate route. `RPGFootsteps.cpp:69-76` already plays `LandSound` on character landing. | The candidate “boots land” can duplicate the current landing sound. Determine if Owner wants a roll-start rustle, landing replacement, or additive armor foley, then gate against existing `LandSound`. |
| SFX-25 Draw/sheath | No native draw/sheath montage trigger or sound dispatch was found in reviewed project C++ search; pack weapon/stance behavior is data/Blueprint-driven. | Exact stance transition and weapon montage are unverified. Do not infer a runtime seam from the candidate names; inspect the selected pack animation/Blueprint and any existing notify audio before wiring. |

## Limits

These are source-only findings. Pack Blueprint and animation notify assignments, actual player pawn route, and baked audio were not read back. Candidate package metadata does not establish playback. Preserve current behavior and silence for these new options until Owner selection and a route-specific readback.

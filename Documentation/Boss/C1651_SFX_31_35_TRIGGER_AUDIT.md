# C-1651 SFX-31..35 Movement and Ambience Trigger Audit

**Status:** Source-only lead audit. Candidate packages and Owner selection remain separate; no cue wiring or runtime verification.

| SFX | Proposed event | Native seam and evidence | Lead assessment |
|---|---|---|---|
| 31 | Boss heavy armor footsteps | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:1405-1431` attaches `URPGFootsteps` to bosses with concrete walk/jog/run/land cues and a deeper/louder/farther boss profile; `:1435-1439` invokes it in `AttachLegacyBossPrelude`. `Source/OneBossFight/Audio/RPGFootsteps.cpp:69-76,79-112` already plays landing audio and animation-following footstep sounds. | Footfalls already have an active native path. Reusing a different candidate without replacing the configured boss sounds can double-play. Confirm selected route and skeletal foot bones before changing the profile. |
| 32 | Boss dash/teleport whoosh | `Source/OneBossFight/Player/RPGBossGapCloserRules.h:5-12` explicitly labels the gap-closer range rule “Unwired by design.” No boss dash/teleport or corresponding audio dispatch was located in the inspected native source. | Candidate hook appears animation/pack-owned or prospective. Need selected route and montage notify readback; do not infer a teleport event from the candidate spec alone. |
| 33 | Cape/cloth flutter | No cloth simulation, cape movement notify, or cloth sound dispatch was found in the inspected native movement/audio sources. | No confirmed native seam. Requires evidence of a cape/cloth component on the chosen boss and a reliable animation event before a cue can be safely attached. |
| 34 | Boss idle subterranean rumble | `Source/OneBossFight/Audio/RPGArenaAmbience.cpp:8-18,27-45` provides an existing non-spatial wind bed with fade-in and replay-on-finish. | This is a global ambience actor, not a boss-torso emitter. A close-range boss loop would require a separate spatial, lifecycle-bound component; candidate metadata does not prove loop suitability. |
| 35 | Boss ground skid deceleration | `RPGFootsteps.cpp:69-76` covers landed impacts; `:79-112` covers foot-bone steps only. No grounded skid/deceleration sound callback was found in the inspected native source. | Landing and skid are distinct triggers. Avoid reusing `LandSound` as skid without a real movement/animation event and guard against landing duplication. |

## Scope and limits

- Existing player and boss footsteps are native and spatialized; boss setup changes pitch, volume, audible range and speed thresholds (`RPGPlayerMovesSubsystem.cpp:1422-1429`).
- The ambience actor currently owns one non-spatial wind loop; it does not establish the proposed arena wind, rumble, fire, or fog assets are configured in `L_SevarogArena`.
- Source inspection cannot establish serialized montage notifies, cape components, selected runtime boss route, or candidate Sound Cue internals.
- No project source/assets/config changed. No audio was exported, no Editor/build/test/runtime command was run, and no wiring was added.

## Next

Antigravity owns BT-139..BT-143 package-only candidate verification and should continue without awaiting this lead audit. Export/reel work and cue wiring remain gated on Owner selections and the documented C-1155 process.

# C-1651 SFX-41..45 Arena Ambience and Collision Trigger Audit

**Status:** Source-only lead audit. Candidate choice and level-instance readback remain unverified; no wiring or runtime validation.

| SFX | Proposed event | Native seam and evidence | Lead assessment |
|---|---|---|---|
| 41 | Arena ruin wind bed | `Source/OneBossFight/Audio/RPGArenaAmbience.h:12-15,28-37` defines one level-placeable non-spatial wind bed with `Wind` and `WindVolume`; `RPGArenaAmbience.cpp:8-18,27-45` sets sound/fades in and restarts on finish. | Component supports this use, but C++ alone does not prove an instance is placed in `L_SevarogArena` or a candidate assigned. Existing specification is not evidence of runtime configuration. |
| 42 | Brazier ember crackle | No native generic positional ambience/brazier emitter was found. The existing `ARPGArenaAmbience` uses non-spatial audio (`RPGArenaAmbience.cpp:14-18`). | Needs map emitter instances, location/attenuation and lifecycle readback; package presence does not establish emitter placement. |
| 43 | Subterranean drone | The existing ambience actor exposes only a single `Wind` source (`RPGArenaAmbience.h:28-37`); no separate drone channel or runtime mix dispatcher was found. | Could be added as a separate approved map layer, but avoid silently reusing/overwriting the wind bed. Loop suitability and mix headroom need audition. |
| 44 | Arena boundary wall impact | `Source/OneBossFight/Player/RPGBossArenaEdgeRules.h:5-15` labels arena-edge pressure “Unwired by design” and only computes pressure/inward direction. `Source/OneBossFight/Player/RPGHitIntake.cpp:133-148,348-380` binds pack melee collision `OnHit(FHitResult)`, not perimeter-wall contacts. | No confirmed perimeter collision callback or player/boss wall audio seam in the inspected native source. A collision/audio event must be confirmed per actor before use. |
| 45 | Dynamic fog/mist wash | No phase-linked fog audio control was found. The existing ambience actor restarts its single wind source on completion (`RPGArenaAmbience.cpp:27-45`) but has no combat-phase modulation input. | Not implemented by the current ambience actor; fog/phase state and a separate wash layer need a verified level/runtime hook and lifecycle design. |

## Cross-cutting notes

- Current native arena ambience is an explicitly placed 2D wind component, not proof of the proposed environmental actor setup in the selected map.
- The specified mix routing, attenuation, ducking and concurrency values are recommendations only; no SoundClass or SoundConcurrency asset readback was performed.
- No project source/assets/config changed. No audio was exported, tests run, Editor/build/PIE launched, or cues wired.

## Next

Antigravity owns BT-151..BT-155 package-only candidate verification and should proceed without awaiting this lead audit. Owner-pick/export and wiring gates remain active.

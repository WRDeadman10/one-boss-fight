# C-1651 SFX-46..50 Routing and Cook Evidence Audit

**Status:** Source/docs-only lead audit. Serialized audio asset contents and a sound-enabled Shipping cook were not inspected or run.

| Task | Available evidence | Audit result / limit |
|---|---|---|
| 46 SoundClass buses | The inspected native audio code assigns per-call volume/fades but no `USoundClass` or submix routes. `RPGBossMusic.cpp:56-64` creates 2D audio components from configured SoundBase references; `RPGArenaAmbience.cpp:30-36` sets sound/volume; `RPGFootsteps.cpp:26-32,61-66` creates transient attenuation and plays at location. | The proposed Master/SFX/Foley/UI/Music class hierarchy is a spec, not proven routing. Binary `.uasset` package internals need readback to establish actual SoundClass assignments. |
| 47 SoundConcurrency | No `USoundConcurrency` reference or runtime assignment appeared in the inspected project audio code (`RPGFootsteps`, `RPGArenaAmbience`, `RPGBossMusic`). | Cannot claim concurrency limits/voice-stealing policy without serialized asset inspection or engine readback. No concurrency edits were made. |
| 48 Spatial attenuation | `RPGFootsteps.cpp:26-32` creates a transient spherical attenuation object with configured local values; `:61-66` supplies it to `PlaySoundAtLocation`. | This proves one footsteps path uses runtime-generated attenuation, not that all candidate sounds or proposed 200/2500 cm curves are set. Other ambience/music paths are 2D. |
| 49 Combat ducking | `RPGLegend.cpp:167-178,286-291` pushes and pops an optional `USoundMix` during the parry feedback pulse; `RPGBossMusic.cpp:78-106` crossfades phase music; `RPGArenaAmbience.cpp:32-45` starts/restarts one wind sound. | A specific parry-pulse SoundMix hook exists, with a null-safe no-change path. It does not prove that a SoundMix is assigned in assets or that generic attack, execution, stagger, or defeat ducking is wired. Phase crossfade is separate. |
| 50 package/cook | `Documentation/Boss/C1650_WINDOWS_DEVELOPMENT_PLAYTEST_PACKAGE.md` records a successful Win64 Development BuildCookRun using `-nosound`, archive listing and package hashes, plus material fallback warnings. It explicitly says the package was not launched, benchmarked, or accepted as a playable build. | This is existing Development package evidence, not a fresh sound-enabled Shipping cook, missing-audio-reference audit, or voice-starvation test. No such new claim is made. |

## Boundaries

- The source inventory is not a substitute for Unreal's serialized SoundClass, SoundConcurrency, SoundAttenuation, SoundMix, or SoundSubmix readback.
- No assets/config/source changed; no export, test, build/cook, Editor/PIE, or runtime verification was performed.
- Antigravity's parallel BT-157..161 work should preserve the distinction between inspectable code/report evidence and data requiring engine asset readback.

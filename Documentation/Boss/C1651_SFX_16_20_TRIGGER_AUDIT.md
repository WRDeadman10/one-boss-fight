# C-1651 SFX-16..20 Trigger Seam Audit

**Date:** 2026-11-18
**Scope:** Lead source-only review of phase transition/ambience sound seams. No C++/asset/config edits, Unreal Editor, build, tests, or PIE.

| Item | Source evidence | Lead finding / safe seam after Owner approval |
|---|---|---|
| SFX-16 Phase 2 roar | `RPGBossPhases.cpp:293-316` loads/plays the configured roar sequence or transition montage and logs a silent fallback; `RPGSevarogDirector.cpp:170-192` has a separate director-side roar montage path. | Neither reviewed C++ path dispatches a SoundCue. There are two phase-flow paths; confirm which is active before adding a one-shot. Animation assets may contain authored audio not visible in this source-only pass; inspect only under approved locked readback. |
| SFX-17 Aura ignite | `RPGSevarogDirector.cpp:195-210` optionally spawns `PhaseTwoAuraEffect` as Niagara when tier presentation is enabled. | No sound dispatch at this spawn. This is the direct burst seam only if this director path is active. An optional sound must remain unassigned by default. |
| SFX-18 Aura loop | The same Niagara component is retained in `PhaseTwoAuraComponent`, destroyed by `ClearPhaseTwoVisuals` (`RPGSevarogDirector.cpp:224-242`). | No audio component/loop exists in this path. A loop would need matching start/stop/reset lifetime rather than a one-shot on every tick; confirm director activation and owner selection first. |
| SFX-19 Transition rupture | `RPGBossShockwave.cpp:42-75` launches the gameplay shockwave and spawns `NS_Boss_ShockwaveRing`; this code does not dispatch sound. | The code evidence is for the shockwave attack, not proof of a phase-transition crack event. Do not wire the transition cue here unless route evidence confirms it is the intended phase event. Find/confirm the actual transition crack or decal seam under locked readback. |
| SFX-20 Transition stinger | `RPGBossMusic.cpp:94-112,163-179` optionally crossfades Phase 1 to Phase 2 music when the relevant phase/legend gates are active. | A new one-shot could overlap the existing PhaseTwoMusic crossfade. Confirm current music assignment and whether a separate stinger is wanted; keep a new field null/unassigned until the Owner selects it. |

## Route and validation boundary

The source contains both `URPGBossPhases` and `URPGSevarogDirector` phase flow. This audit cannot establish which path or asset assignments are in the packaged map. Candidate SoundCue package presence alone does not prove trigger timing, audible playback, or absence of baked montage audio. Batch 3 remains spec-only; the Owner-pick policy still blocks raw WAV export and any wiring. No runtime or audio playback claim is made.

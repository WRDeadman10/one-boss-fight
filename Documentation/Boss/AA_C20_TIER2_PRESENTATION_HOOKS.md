# Tier 2 presentation hooks — parry distortion, phase aura, recoil

Owner-approved scope: C-953 Option A. All references remain unset by default; presentation is gated by the Development-only `rpg.Art.Tier2` switch.

## Hooks

- **Parry post-process:** when the Development Tier 2 switch is enabled at play start, `URPGBossLegend::BeginPlay` resolves the optional soft `ParryDistortionMaterial` before combat. A confirmed parry passes its actor to the Legend subsystem, which adds the loaded material to that actor's camera at weight 1 for the existing slow-motion scope. The parry path does not synchronously load the asset. If the switch is enabled only after `BeginPlay`, the material remains unloaded until the next play start. Restore, cancellation, encounter reset, expiry, and world teardown remove it. If that material was already in the camera blendables, its previous weight is restored. The optional `ParryFeedbackCollection` still pulses the MPC scalar; the optional SoundMix scope is unchanged.
- **Phase-two aura:** existing `URPGSevarogDirector` optional soft Niagara reference and MPC glow remain empty by default and clean up on death, reset, and teardown.
- **Boss parry recoil:** existing optional montage remains null by default and only plays through the confirmed-parry hook while Tier 2 preview is enabled.

## Cook coverage

The Tier 2 assets are assigned through optional properties, with no hard-coded `/Game` load path in Source. `Config/DefaultGame.ini` already cooks `/Game/OneBossFight/VFX` for the parry post-process material and `/Game/OneBossFight/Boss` for the aura and recoil content. The existing native `OneBossFight.Content.CookCoverage` check scans Source path literals and remains the Lead build gate; no asset was created, imported, or assigned by this change.

## Verification boundary

Focused offline source contracts cover optional defaults, Development gating, camera blendable restoration, MPC/SoundMix scope, aura/recoil lifecycle, and the existing cook roots. Lead still owns C++ compilation, native automation/CookCoverage, and PIE confirmation with the authored assets. No Unreal build or Editor session was run by Codex.

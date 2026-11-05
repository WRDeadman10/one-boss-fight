# V-C037: Tier 1 Visual Preview Switch

The Tier 1 preview is a Development-only convenience for optional shockwave-ring and parry-spark effects. The switch is `rpg.Art.Tier1` and its default is `0`.

## Use

1. Run a Development build in the editor.
2. In the editor console, enter `rpg.Art.Tier1 1` to enable the built-in preview fallback, or `rpg.Art.Tier1 0` to disable it.
3. Trigger a boss shockwave or a confirmed parry and inspect the optional ring/spark.
4. Restore `rpg.Art.Tier1 0` before capturing a baseline or parity run.

Authored per-component Niagara overrides keep priority regardless of the preview switch. When the override is empty and the switch is 0, the helper selects no preview effect; the gameplay event and hit/trace logic continue unchanged. The preview switch compiles out of non-Development configurations. Optional VFX are covered by the `/Game/OneBossFight/VFX` cook root; later owner-approved Tier 2 assets remain unassigned until their own cook check passes.

## Related switches

- `rpg.AttackTracker.A2PreviewClip` defaults to `0` and selects `AM_Boss01_A2` only through `PlayMoveMontageForTest`; the live `StartMove("A2")` pack ability remains the default.
- `rpg.Art.Tier2` defaults to `0` and gates the optional parry post-process/audio, phase-two aura, and recoil presentation hooks. The corresponding assets/references are unset in the current project.

See `V_C031_C035_OPTIONAL_PRESENTATION_HOOKS.md` for the Tier 2 wiring and paired A2 test plan.

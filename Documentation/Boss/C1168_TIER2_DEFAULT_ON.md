# C-1168 Tier 2 default-on implementation

## Decision and scope

C-1168 directs the phase-two aura and parry-recoil presentation to be enabled by default in every build configuration. The Development-only `rpg.Art.Tier2` CVar remains an explicit override: `0` disables, `1` enables, and its default `-1` inherits the Game config value. Other Development values fail closed. Shipping and other non-Development builds read the config setting and ignore the CVar.

The configured default is `bTier2PresentationEnabled=True` on `URPGPresentationSettings`, also set in `Config/DefaultGame.ini`. Existing safe soft-asset loading and null checks remain in place. The default aura asset is intentionally unchanged pending Antigravity authoring and Lead's paired capture acceptance under C-1168.

## Implementation status

The shared Tier 2 gate now reads the config-backed setting for boss aura, parry recoil, and the already-gated Tier 2 parry feedback hooks. The pure contract covers config inheritance, both valid overrides, invalid-value fail-closed behavior, and non-Development config behavior. The automation test also asserts the configured default.

## Verification boundary

The C-1155 lock was acquired by Codex after C-1171 was posted and no UnrealEditor process or lock remained. Development UBT build passed. The full native suite passed **494/494** (exit 0), including `OneBossFight.Art.Tier2Presentation.PureRules`; the run used `-DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`. Logs: `Docs/BossCombatReview/Execution/Codex/C1168_TIER2_DEFAULT_ON/build.log` and `suite.log`. Codex released its lock after the run; no Editor, PIE, capture, Shipping build, or package run was performed. Lead acceptance remains pending. No asset path was changed; the Boost Lite candidate remains gated on AG readback and Lead paired-capture acceptance.

# Queue AL C21–C25 — Tier 2 lifetime and event audit

**PRODUCTION CHANGE, unbuilt.** Static Source review under Claude's engine lock; no native build, PIE or first-use timing measurement.

| Task | Finding/change |
|---|---|
| C21 | The live component is attached once through `AttachBossDiagnostics` on either encounter route. It reads current/max pack health on a 0.1 s Development tick, shows aura only for 0 < health <= 60% max while not dormant, and clears on health reset above threshold, death, cvar disable or EndPlay. Added a per-phase activation latch so an auto-destroyed Niagara component cannot spawn again every tick; reset clears the latch so a later fight may show it. Runtime respawn/reset still needs Lead PIE. |
| C22 | `rpg.Art.Tier2` defaults off and `RPGTier1Visuals::IsTier2PreviewEnabled()` returns false outside Development. The new component has tick disabled outside Development. A late cvar enable on a live boss is read by its next Development tick; RPGLegend's PPM soft material loads on the next opted-in successful parry. A later disable clears aura and passes no distortion material to the parry pulse. First-use synchronous load cost remains unmeasured. |
| C23 | The parry hook is source-backed: `RPGDamageResolver.cpp:181–184` enters `ERPGDamageOutcome::Parried`, spends the swing key, then calls `URPGPlayerParry::NotifyParried(Target)`. That method invokes the live boss component's recoil and avoids also invoking the dormant director on the same actor. This is an accepted parry outcome, not a guessed block signal. Lead must verify the live animation actually plays. |
| C24 | Extended `OneBossFight.Art.Tier2Boss.PureRules` for zero/full health, repeated threshold eligibility after reset, duplicate aura prevention and distinct successful parries. These pure tests are authored but not run in Unreal; native result belongs to BUILD-256. |
| C25 | No closure to KI-191: Lead must compile, run native tests, then PIE both routes for late cvar flip, one aura per phase, reset/respawn cleanup, successful-parry recoil/distortion and cvar-off inertness. Presentation and load-time behavior remain unverified. |

Source ownership: `RPGTier2BossPresentation.*`, `RPGTier2BossRules.h`, `RPGTier2BossRulesTests.cpp`, `RPGPlayerMovesSubsystem.cpp`, `RPGPlayerParry.cpp` and `RPGLegend.cpp`. No asset file was edited.

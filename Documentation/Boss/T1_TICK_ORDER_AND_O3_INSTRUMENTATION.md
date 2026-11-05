# C-862 T1 tick order and O3 start-state instrumentation

Status: test and source changes are authored for Lead build/automation and paired A4/P06 reruns. Codex did not build, launch Unreal, or run PIE.

## T1 source audit

The proposed cause is confirmed as a real ordering hazard, though it is not yet proven to cause the observed parity deltas. `URPGBossLowSweep::TickComponent` reads the attacker's current move, active window, instance, committed yaw, timing and montage position (`Source/OneBossFight/Player/RPGBossLowSweep.cpp:197-212,227`). Both tracker and low sweep tick in the inherited `TG_PrePhysics` default (`RPGAttackTracker.cpp:104-106`, `RPGBossLowSweep.cpp:21-24`). A4 D2's S9 diagnostic reports legacy order `RPGAttackTracker#26` before `RPGBossLowSweep#29` at `.../legacy/editor_raw.log:2931`; data reports `RPGBossLowSweep#22` before `RPGAttackTracker#28` at `.../data/editor_raw.log:2945`. Thus LowSweep can read prior-frame tracker state on data when no explicit dependency exists.

The other direct tracker consumers inside `TickComponent` were checked:

| Consumer | Tracker state read during tick | Tick group | Legacy/data order evidence |
|---|---|---|---|
| `RPGBossLowSweep` | move/window/instance/yaw/timing/position/phase | inherited `TG_PrePhysics` | Legacy tracker first; data sweep first, cited above |
| `RPGBossShockwave` | move/window/instance (`RPGBossShockwave.cpp:173-175`) | inherited `TG_PrePhysics` | Legacy attach creates tracker first (`RPGPlayerMovesSubsystem.cpp:702-713`); data order not captured in O2 |
| `RPGBossHealPunish` | move/window/instance (`RPGBossHealPunish.cpp:271-274`) | inherited `TG_PrePhysics` | Legacy tracker first (`:702`) before component (`:721-723`); data order not captured in O2 |
| `RPGTraceGuard` | move/instance while processing trace (`RPGTraceGuard.cpp:136`) | explicit `TG_PrePhysics` (`:17-20`) | Legacy tracker first (`:702`) before component (`:729-731`); data order not captured in O2 |
| `RPGCombatDebug` | move/phase/instance/yaw for overlay (`RPGCombatDebug.cpp:140-141`) | inherited `TG_PrePhysics`; disabled in Shipping | Legacy tracker first (`:702`) before component (`:783-786`); data order not captured in O2 |
| `RPGBossLegend` | move/active/instance (`RPGLegend.cpp:470-473`) | explicit `TG_PostUpdateWork` (`:256-259`) | Legacy tracker first (`:702`) before component (`:739-742`); data order not captured in O2 |
| `RPGTraceAudit` | move/instance for trace-window labeling (`RPGTraceAudit.cpp:201-202`) | explicit `TG_PostUpdateWork` (`:24-31`) | Legacy tracker first (`:702`) before component (`:779-781`); data order not captured in O2 |

`URPGBossCloseClipSwap::TickComponent` and `URPGBossHud::TickComponent` do not read `URPGAttackTracker`; their names were checked rather than assumed to be consumers. O2 only emitted registration order for the tracker, LowSweep, and i-frame monitor, so this report does not invent order values for other consumers.

The legacy attach path creates the tracker before the seven tick consumers (`RPGPlayerMovesSubsystem.cpp:702-786`), so the explicit edge preserves its established order. Added `RPGBossTrackerTickPrerequisite::Add` (`Source/OneBossFight/Player/RPGBossTrackerTickPrerequisite.h`) and call it from BeginPlay and again when a late-registered tracker is first found in TickComponent for all seven actual tick consumers. A weak bound-tracker reference avoids adding the same edge every frame. This corrects the captured data LowSweep reversal without changing BossCore plan order. Added a transient-world automation test whose consumer is registered before its tracker and asserts it sees the tracker value advanced in the same frame (`Source/OneBossFight/Tests/RPGBossTrackerTickOrderTests.cpp:50-94`). The test has not been built or run. O2 did not emit selected-route registration positions for the other six consumers.

## O3 logging

The A4 and A5 drivers now log `[A4/A5] PIE_START monotonic=...` immediately before their existing `editor_request_begin_play()` call, then emit a structured `START_STATE` JSON row after the A4 trial placement and each P06 placement. Each row records scenario/trial, elapsed monotonic seconds from the begin-play request, boss/player location and rotation, capsule radius/half-height, mesh relative transform, and selected CharacterMovement settings. Missing/unavailable values serialize as null; diagnostic exceptions are caught and reported once so they cannot abort a scenario.

The calls use APIs already present in drivers: `time.perf_counter` (`Scripts/Editor/pie_legend.py:10,92`), actor transforms and placement (`Scripts/Editor/pie_a4_low_sweep.py:111-116,189`), skeletal-mesh/capsule queries (`Scripts/Editor/pie_boss_death_states.py:83,174`), CharacterMovement discovery (`Scripts/Editor/pie_air_attack.py:74`), and property reads (`Scripts/Editor/air_jump_tuning.py:11,16`). The marker is the driver's begin-play request timestamp, not an engine callback for the first PIE frame; the paired logs can now bound startup through first placement, with that small request-to-world-start offset retained as a limitation.

Only Python AST parsing was run: both changed drivers parsed. Lead build, automation, and A4/P06 paired captures remain pending; no combat values were changed.

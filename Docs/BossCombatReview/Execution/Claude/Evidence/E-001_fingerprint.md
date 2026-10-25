# E-001 Provenance fingerprint (CI-P0-C-01 step a)

Captured 2026-10-25 ~10:40 IST by Claude. Read-only. Probe source: probes/p0_cvar_state.py (changes nothing).

## Build / editor
- git HEAD: 5500600d0310aac874928aa8aacc8338e6d5535d (branch main); dirty entries: 20 (preserved, untouched)
- Editor module: Binaries/Win64/UnrealEditor-OneBossFight.dll, 2026-10-25 00:57:04 +0530, sha256 8d15cd52ee1e77fc19295b96c2c123c413cc3883224192fa6152ed97882f951f
- Running editor PID 31160 started 2026-10-25 00:57:31 (27 s after the DLL), RDP session #9, map L_SevarogArena, PIE not running (pie_state.py: game world None), bridge http://localhost:3000 answers.
- Files under Source/ and Config/ newer than the DLL: 0 (none), so the running binary matches the working-tree source as of this capture.

## Live console variables (running editor, not code defaults)
| cvar | live value | code default |
|---|---|---|
| rpg.WakeClip | 0 | 1 (RPGBossDormantWake.cpp:96) |
| rpg.CloseTelegraph | 0 | 0.4 (RPGAttackTracker.cpp:19) |
| rpg.Legend / LegendShakeScale | 1 / 1 | 1 / 1 |
| rpg.Debug | 0 | 0 |
| rpg.Build | empty | empty |
| t.MaxFPS / t.FixedFrameRate / r.VSync | 0 / 0 / 0 | engine |
| global time dilation | 1.0 | 1.0 |

**Consequence:** the live editor holds the DRIVER warm-up state (wake clip off, close telegraph stretch off = pack raw pacing), NOT the shipping/default configuration (wake on, telegraph 0.4). Every P0 timing observation must state which configuration it ran in; natural-default runs must set rpg.WakeClip 1 and rpg.CloseTelegraph 0.4 explicitly and say so.

## Source hashes (sha256, working tree)
```
f2d2615f1b938aa8bf1f4ad9d7574b1876446823d83b87cd69521ca9d1153f0c *Source/OneBossFight/Player/RPGAttackTracker.cpp
df74131faeb6a0c2d19dac19b66509a366353beb6437ec03f9490d52bcd8ca48 *Source/OneBossFight/Player/RPGAttackTracker.h
dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d *Source/OneBossFight/Player/RPGBossEncounter.cpp
d372922674851c1d17e601c0ebb2cd92e8023a53ae08dff243135c354d89ca19 *Source/OneBossFight/Player/RPGBossClips.h
9632381f60e92d3f2d7cc7362883cbc03c3b258191abbbb4755a4bc9591cf3a4 *Source/OneBossFight/Player/RPGBossShockwave.cpp
bea63c889b32af847d69a65f0b144fe4219eca7c55e15877a6695681976c0e81 *Source/OneBossFight/Player/RPGBossLowSweep.cpp
1e63046d9c215fd0d7a5f894ee1b4539d64ddbefd9c80812cecbbae89c476906 *Source/OneBossFight/Player/RPGBossHealPunish.cpp
6438e6bb76122fae5193bff9a1d55c88211dfb1edf90c4704236c1500a744bdb *Source/OneBossFight/Player/RPGBossJavelin.cpp
82da0dd3400a049d92bd96409f90db58a319fd7db73e44f7b46b766e938a6bca *Source/OneBossFight/Player/RPGDamageResolver.cpp
68c544741faf219d61bd25b84e6de0bec9b7ac8cdc8984cf89455a580f427410 *Source/OneBossFight/Player/RPGBossDormantWake.cpp
-- whole Source tree digest:
ebac62b22226c466ec03b251a80d692dd8466db139f17563a9d74a6cf108f4e3 *-
-- Config digest:
cbb4de9792e8de4cf666b6fd2fdb05631381bb38cf88e32607172ca30225895d *-
```

## Dirty tree at capture (git status --short)
```
 M Content/OneBossFight/Levels/L_SevarogArena.umap
 M Documentation/BENCHKIT_README.md
 M Documentation/KNOWN_ISSUES.md
 M Documentation/PERFORMANCE_LOG.md
 M Documentation/TEAM_MAILBOX.md
 M Scripts/BenchKit_Collect.ps1
 M Scripts/Editor/pie_close_attacks.py
 M Scripts/Editor/pie_close_reach.py
 M Scripts/Editor/pie_dormant_wake.py
 M Scripts/MakeBenchKit.ps1
 M Scripts/RunBenchmark.ps1
 M Scripts/RunDrivers.ps1
 M Scripts/RunPerfExperiments.ps1
 M Source/OneBossFight/Arena/RPGFireSource.cpp
 M Source/OneBossFight/Arena/RPGPerfSwitches.cpp
 M Source/OneBossFight/Arena/RPGPerfSwitches.h
 M Source/OneBossFight/Player/RPGBossDormantWake.cpp
?? Docs/
?? Scripts/Editor/wake_clip_off.py
?? Unreal_Boss_Combat_Engineering_Kit/
```

## Side effect disclosure
run_in_editor.py writes a numbered helper script into Content/UnrealClaude/Scripts/ (run_file____016.py and the probe run); that is the standard bridge mechanism and changes no asset.

## Raw probe output (added per X-96)

Source: `Saved/Logs/OneBossFight.log` (mutable editor log), lines with prefixes `[PieState]` and `[P0Cvar]` from this session, copied verbatim (UTC timestamps, IST = UTC+5:30). Probe sources: `Scripts/Editor/pie_state.py` (existing, unchanged), `probes/p0_cvar_state.py`.
```
[2026.10.25-05.08.08:796][798]LogPython: [PieState] game world: None
[2026.10.25-05.08.30:846][863]LogPython: [P0Cvar] rpg.WakeClip = 0.0
[2026.10.25-05.08.30:846][863]LogPython: [P0Cvar] rpg.CloseTelegraph = 0.0
[2026.10.25-05.08.30:846][863]LogPython: [P0Cvar] rpg.Legend = 1.0
[2026.10.25-05.08.30:846][863]LogPython: [P0Cvar] rpg.LegendShakeScale = 1.0
[2026.10.25-05.08.30:846][863]LogPython: [P0Cvar] rpg.Debug = 0.0
[2026.10.25-05.08.30:846][863]LogPython: [P0Cvar] t.MaxFPS = 0.0
[2026.10.25-05.08.30:846][863]LogPython: [P0Cvar] t.FixedFrameRate = 0.0
[2026.10.25-05.08.30:846][863]LogPython: [P0Cvar] r.VSync = 0.0
[2026.10.25-05.08.30:847][863]LogPython: [P0Cvar] rpg.Build = ''
[2026.10.25-05.08.30:850][863]LogPython: [P0Cvar] editor world = L_SevarogArena; global time dilation = 1.0
```

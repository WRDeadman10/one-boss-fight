# One Boss Fight: agent onboarding

## Read in this order

1. `AGENTS.md` at the repository root for project constraints.
2. `Documentation/PROJECT_STATE.md` for current project state, gotchas, and the team protocol. The team protocol is near its end.
3. `Documentation/TASKS.md` for accepted work, backlog, and current assignments.
4. Read `Documentation/Boss/QUEUE_V.md` for active tasks across both lanes (Codex V-C001..V-C100 and Antigravity V-A001..V-A100). Queue V supersedes all prior Queue 200/B snapshots.
5. `Documentation/Archive/HANDOFF_NEXT_CHAT.md` for historical handoff context.
6. `Documentation/TEST_PLAN.md`, `Documentation/KNOWN_ISSUES.md`, and `Documentation/DECISIONS.md` as the task requires.
7. For framework boss work, read `Documentation/Boss/ARCHITECTURE_OVERVIEW.md` and the topic reference/data-flow page before editing.

## Team workflow

Claude is technical lead and owns Unreal Editor, builds, PIE, integration and review. Codex handles bounded source, scripts, docs, or read-only audits. The owner makes product decisions, performs hand tests, and commits. Messages are relayed through append-only `Documentation/TEAM_MAILBOX.md`; make every report self-contained and use `TASK / STATUS / FINDINGS / DECISION NEEDED / NEXT ACTION / VALIDATION`. Check its tail at the beginning of each work cycle, claim files before editing, and report line citations and actual validation evidence.

Never commit or push, discard another agent's work, run two editor/driver chains, edit pack assets, or rebuild/delete an asset other assets reference. Close the editor before a build; launch with `-nosound`. Never call `set_editor_property` on components during PIE. Do not call a test or build passed unless it was run and the result was observed. See `PROJECT_STATE.md`'s team protocol for full rules.

## Useful commands

```powershell
# Build (editor closes first and relaunches with -nosound by default)
powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1

# Build and run the automation suite when the editor owner has authorized the run
powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1 -Tests

# Run a selected PIE regression driver set in the open editor
powershell -ExecutionPolicy Bypass -File Scripts\RunDrivers.ps1 -Only pie_boss_death,pie_remains

# Offline tools have their usage summarized here
Get-Content Documentation\Boss\TOOLS.md
```

## Engine Plugin Prerequisites (NVIDIA DLSS 4.5 & Streamline)

As of `BUILD-223` (C-895 / C-896), NVIDIA DLSS 4.5 (plugin v8.9.0-NGX310.9.16) is enabled in `OneBossFight.uproject`.
The plugin and its required runtime dependencies are installed at the **ENGINE level** and are kept **OUT OF GIT**:
- `Engine/Plugins/Marketplace/DLSS`
- `Engine/Plugins/Marketplace/StreamlineNGXCommon`

### Fresh Machine Setup Steps:
1. Obtain the plugin distribution from `C:\UnrealProject\2026.10.16_UE5.5_DLSS4.5Plugin_v8.9.0` or Epic Games Marketplace.
2. Copy the `DLSS` and `StreamlineNGXCommon` folders into your engine marketplace plugins directory:
   `C:\Program Files\Epic Games\UE_5.5\Engine\Plugins\Marketplace\`
3. Verify `nvngx_dlss.dll` exists at:
   `C:\Program Files\Epic Games\UE_5.5\Engine\Plugins\Marketplace\DLSS\Binaries\ThirdParty\Win64\nvngx_dlss.dll`
4. Packaging & Staging Gate:
   - Packaging automatically copies the runtime DLLs to:
     `Saved/StagedBuilds/Windows/OneBossFight/Plugins/Marketplace/DLSS/Binaries/ThirdParty/Win64/nvngx_dlss.dll`
   - Staging scripts verify this dependency via `Scripts/Tools/test_make_bench_kit_dependencies.py`.
   - Native cook coverage enforces that any path literals in Source/ are listed in `Config/DefaultGame.ini` under `DirectoriesToAlwaysCook`.

## Development Preview CVars (Strict Parity Contract)

All new art and presentation features default to empty/`nullptr` to preserve the D5 parity baseline. They are previewed in Development builds using explicit console switches:
- `rpg.Art.Tier1 1`: Previews Tier 1 Niagara effects (`NS_Boss_ShockwaveRing`, `NS_Combat_ParrySpark`).
- `rpg.Art.Tier2 1`: Previews Tier 2 hooks (parry slow-motion post-process MPC pulse, Phase 2 aura, boss recoil montage).
- `rpg.AttackTracker.A2PreviewClip 1`: Previews authored composite `AM_Boss01_A2` in `PlayMoveMontageForTest`.
- `rpg.Perf.FireShadows 4`: Evaluates cardinal shadow reduction for GPU performance optimization.

Use `Documentation/TEST_PLAN.md` for current evidence. The full PIE driver gate can take around 100 minutes; run selected rows in chunks. Do not launch an editor/build/driver run unless you own the editor handoff.

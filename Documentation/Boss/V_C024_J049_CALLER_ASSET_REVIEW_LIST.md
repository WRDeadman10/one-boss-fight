# V-C024 — J049-A caller design and asset review list

J049 Option A approves the existing Blueprint-callable `SetSelectedDefinition` route for Shipping, but C-876 found no current content caller. This is a caller design and review inventory only: no test-only caller, menu, map, or asset is created. A7-B remains gated; current legacy startup is unchanged.

## Candidate caller shape

The caller must choose the encounter before the world subsystem resolves startup selection. A GameInstance-owned choice is the leading design because `URPGEncounterSelectionSubsystem` stores the object per game instance; a Level Blueprint `BeginPlay` call may be too late and must not be assumed safe without a timing proof. Proposed flow: choose the authored G044 asset, pass the loaded definition object to `SetSelectedDefinition`, verify the accepted identity/diagnostic, then let the world startup activate it. A null/invalid choice must surface recovery and must not silently look like a successful selected run.

## Files/assets for owner and Lead review

| Candidate | Why inspect it | Change proposed now? |
|---|---|---|
| `Content/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_AdvancedGameInstance.uasset` | Current configured GameInstance; determine whether extending it would alter vendor-owned content | No; prefer a project-owned subclass if a real caller is approved |
| `Config/DefaultEngine.ini:6-7` | Configured default GameMode and GameInstance paths | No |
| `Content/OneBossFight/Levels/L_SevarogArena.umap` | Current arena level; inspect Level Blueprint and GameMode overrides before proposing a map caller | No |
| `Content/OneBossFight/Data/DA_Sevarog_G044_Encounter.uasset` | Current encounter definition candidate; validate it and its complete cook closure | No |
| `Source/OneBossFight/Player/RPGEncounterSelectionSubsystem.h:30-31` | Existing `SetSelectedDefinition` / `ClearSelectedDefinition` API | No source change |
| `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:115-135` | World selection timing and selected/legacy route split | No source change |
| `Documentation/Boss/A7_RELEASE_GATE_CHECKLIST.json`, `J049_OWNER_DECISION_PACKET.md`, `T025_G2_PACKAGED_RECOVERY_MATRIX.md` | Caller, package, and recovery gates | Update only when reviewed evidence exists |

Inventory limitation: source/config paths are known; this read-only pass did not inspect Blueprint graphs. The earlier Lead package byte search reported zero setter references in 11,738 content packages, while graph scan was inconclusive. Before choosing an asset, Lead must inspect current graph references and validate exact object timing. New project assets, a modified map, or any look-changing UI require the relevant owner approval first.

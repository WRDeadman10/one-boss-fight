# AA-C26–C29 — data-default route, nightly parity, and Shipping caller

## AA-C26 — remaining legacy paths

`Config/DefaultGame.ini` sets `bDefaultToDataStartup=True`. On `L_SevarogArena`, the default definition is stored before the world startup branch; a successful selection runs the data activation path and returns without calling the legacy `Attach()` route. A requested data route that fails activation reports `HardError` and disables the selected boss path; it does not fall through to legacy attachment.

| Legacy path | Reachability | A7-B disposition |
|---|---|---|
| `OnWorldBeginPlay` → `Attach()` existing pawns | No selected definition and `bUseLegacyStartup=true`: e.g. Development `-RPGLegacyStartup` / `RPG_LEGACY_STARTUP=1`, non-arena map, data-default switch off, or default definition load failure. | Retained as the non-Shipping parity route and as a fail-safe when default data cannot be loaded. Not removed. |
| `OnActorSpawned` → `Attach()` | A newly spawned pack pawn is not in an active/requested selected-data mode and legacy startup is enabled. | Same legacy route; keep paired parity coverage. |
| `AttachLegacyBossPrelude` / `AttachLegacyBossBundle` | Called only by `Attach()` for the legacy boss component set (audio/footsteps plus legacy gameplay components). | A7-B candidate removal only after its separate release gates close. |
| `rpg.EncounterDefinition` and `-RPGBenchmark -H019EncounterDefinition=...` selectors | Development-only selection inputs in `RPGEncounterSelectionSubsystem.cpp`; they request the data route and are not the legacy parity control. | Remain non-Shipping. |
| `SetSelectedDefinition` / `ClearSelectedDefinition` | Blueprint-callable `UGameInstanceSubsystem` API remains available in Shipping under J049-A. No real content caller has been found. | Keep API; packaged setter proof waits for the first real caller. |

The legacy route is not literally reachable *only* through the parity flag: the current no-selection fallback also preserves legacy startup when the default data asset cannot load. That distinction is intentional in the current code and should be kept visible until an owner/Lead changes the A7-B policy. Relevant code: `RPGPlayerMovesSubsystem.cpp` (`ApplyDefaultDataSelection`, `OnWorldBeginPlay`, `OnActorSpawned`, `Attach`) and `RPGEncounterSelectionSubsystem.cpp`.

## AA-C27 — nightly one-command dry run

Ran `Scripts/RunA5ParityNightly.ps1` with no `-Execute` switch and an absent output path under `Saved/A5ParityNightly`. The script printed 31 unique pair commands and created no output directory. It uses fresh legacy/data editor processes only when executed; this dry run launched no Editor/PIE. Existing schedule and no-overwrite tests are in `Scripts/Tools/test_a5_nightly_runner.py`.

## AA-C28 — default-route regression coverage

Added `Scripts/Tools/test_default_route_contract.py`. The four static contract cases assert the shipped arena config selects data by default before world startup, parity-only legacy overrides are Development-gated, explicit data activation failures do not fall through to legacy attachment, and the existing native regression cases cover default-data / legacy startup branches. Focused tests passed 4/4. The existing native cases still need Lead build/automation execution.

## AA-C29 — first Shipping caller design (J049-A)

Design only; no Blueprint, widget, map, or asset changed. Preferred flow: a project-owned front-end encounter-choice screen obtains `URPGEncounterSelectionSubsystem` from the persistent GameInstance, calls `SetSelectedDefinition` with a validated authored definition, then opens `L_SevarogArena`. This happens before the arena world's startup selection runs and survives map travel in the GameInstance. A normal “default encounter” choice calls `ClearSelectedDefinition` so the arena's configured G044 default is applied. Avoid a Level Blueprint `BeginPlay` caller, which risks arriving after selection has been resolved.

The first real caller must surface invalid/missing definition errors, record the chosen definition identity, and prove cooked asset closure and packaged selected-route recovery. Current content has no known setter caller (C-876); do not add a test-only caller. Owner/Lead review is still needed before UI/content work, and A7-B stays open.

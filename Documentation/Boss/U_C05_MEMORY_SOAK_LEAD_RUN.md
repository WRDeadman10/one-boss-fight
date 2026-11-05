# U-C05 memory/lifetime soak — Lead run sheet

`Scripts/Editor/pie_memory_soak.py` runs one 20-reset PIE arm for the route selected when the Editor starts. Run it twice in separate Editor processes: once with `H019_ENCOUNTER_DEFINITION` unset (legacy), then once set to the selected encounter asset path below. The driver warms the PIE world for 9 seconds, keeps the player near the boss for 10 seconds per cycle, invokes `RPGBossEncounter.reset_for_test()`, and waits for both participant generation and reset count to advance before recording the next sample.

## Commands

Run the existing project Editor with `-nosound`. Before launching the Editor for the first arm, use a PowerShell session with the variable cleared:

```powershell
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
```

In the Editor session, run the driver using the project's usual bridge command:

```powershell
python -I Scripts/run_in_editor.py Scripts/Editor/pie_memory_soak.py
```

Wait for `[MemorySoak] RESULT route=legacy resets=20/20 status=PASS`. Close the Editor, then launch it again with `-nosound` after setting the selected route in the launch PowerShell session:

```powershell
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
```

Run the same bridge command and wait for `[MemorySoak] RESULT route=selected resets=20/20 status=PASS`. Do not change assets or project settings between arms. Preserve the Editor log containing all `[MemorySoak] sample` lines.

## Measurements and interpretation

Every baseline, pre-reset, and post-reset sample records route, cycle, encounter generation/reset count, world actor total, boss/javelin/wave-projectile counts, Editor working set, and Editor private bytes. Memory uses Win32 `GetProcessMemoryInfo`; if unavailable, the log states that fact and the arm is incomplete for memory comparison. The driver stops on missing actors/components, a failed reset, a reset timeout, a tick error, or the overall watchdog.

Compare post-reset rows 1–20 within each route. A strictly monotonic rise in actor/object counts or private bytes is a leak candidate requiring diagnosis; allocator and asset-cache retention can keep memory elevated, so this signal alone does not prove a leak. Compare legacy versus selected only after both arms complete with 20/20 resets. The driver is authored but has not been run by Codex; the Lead owns both Editor runs.

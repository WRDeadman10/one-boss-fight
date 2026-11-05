# U-C05 memory/lifetime soak — Lead run sheet

`Scripts/Editor/pie_memory_soak.py` runs one 50-reset PIE arm for the route selected when the Editor starts. Run it twice in separate Editor processes: once with `H019_ENCOUNTER_DEFINITION` unset (legacy), then once set to the selected encounter asset path below. The driver warms the PIE world for 9 seconds, keeps the player near the boss for 10 seconds per cycle, invokes `RPGBossEncounter.reset_for_test()`, and waits for both participant generation and reset count to advance before recording the next sample.

## Commands

Run the existing project Editor with `-nosound`. Before launching the Editor for the first arm, use a PowerShell session with the variable cleared:

```powershell
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
```

In the Editor session, run the driver using the project's usual bridge command:

```powershell
python -I Scripts/run_in_editor.py Scripts/Editor/pie_memory_soak.py
```

Wait for `[MemorySoak] RESULT route=legacy resets=50/50 status=PASS`. Close the Editor, then launch it again with `-nosound` after setting the selected route in the launch PowerShell session:

```powershell
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
```

Run the same bridge command and wait for `[MemorySoak] RESULT route=selected resets=50/50 status=PASS`. Do not change assets or project settings between arms. Preserve the Editor log containing all `[MemorySoak] sample` lines.

## Measurements and interpretation

Every baseline, pre-reset, and post-reset sample first executes Unreal's `obj gc` console command and logs both the request and return, then records route, cycle, encounter generation/reset count, world actor total, boss/javelin/wave-projectile counts, Editor working set, and Editor private bytes. This yields 101 post-GC samples per route (one baseline plus 50 pre-reset and 50 post-reset). Memory uses Win32 `GetProcessMemoryInfo`; if unavailable, the log states that fact and the arm is incomplete for memory comparison. The driver stops on missing actors/components, a failed reset, a reset timeout, a tick error, or the overall watchdog (30 minutes).

Compare post-reset rows 1–50 within each route, and inspect both pre/post-reset values around each GC. A strictly monotonic rise in actor/object counts or post-GC private bytes is a leak candidate requiring diagnosis; allocator and asset-cache retention can keep memory elevated, so this signal alone does not prove a leak. Compare legacy versus selected only after both arms complete with 50/50 resets. The driver is authored but has not been run by Codex; the Lead owns both Editor runs.

### Prior 20-reset result (C-915)

Claude reports actor counts stable at 88–90 (legacy) and 90–91 (selected), while Editor private bytes rose about 150 MB and 110 MB respectively over the 20 resets. This is a watch item, not a leak finding: Unreal's Editor caches can retain allocations. The next run uses 50 resets with a full `obj gc` immediately before every sample to separate unreachable garbage from retained memory; compare the post-GC samples and preserve raw Editor logs.

Queue V-C029 adds the offline `Scripts/Tools/summarize_memory_soak.py` interpreter for the paired 50-reset logs. It validates the `PASS 50/50` terminal, 101 GC-marked samples, stage/cycle identities and required post-GC actor/private-memory fields, then reports endpoint delta and actor range without classifying a leak. It does not replace either Lead-run Editor arm.

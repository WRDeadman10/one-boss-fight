# P06–P10 A5 parity capture plan

Status: P06–P09 tooling prepared; P10 real pair is Lead-run and remains pending. C-834 accepted P01–P05, with P02 proven live and BUILD-218 green at 460/460.

| ID | Work prepared | Lead-run acceptance still needed |
|---|---|---|
| P06 | `pie_player_death_reset.py` accepts the same optional `H019_ENCOUNTER_DEFINITION` variable before PIE. | Run legacy then selected; compare death/respawn, reset broadcast and rebind checks. |
| P07 | `pie_telegraph.py` accepts the optional selector before PIE. | Run both arms; compare timing, cancel window and player outcomes. |
| P08 | `pie_boss_hud.py` accepts the optional selector before PIE. | Run both arms; compare the existing HUD assertions and final state. |
| P09 | A4 emits a `PARITY_CAPTURE_JSON` record containing the end-of-run snapshot, check totals and per-scenario observations. `Scripts/Tools/encounter_parity_receipt.py` joins the runtime snapshot with explicit run facts; `write_a4_parity_receipt.py` adds run identity and the hash of the closed raw log, refuses an existing output, then validates/writes v2. Its generic mode uses runner-captured snapshots and individual PASS/FAIL lines from the other registered parity drivers. The comparator ignores expected route-specific selection/binding fields while requiring stable boss/player identity. | Lead builds the accessor and confirms the Editor driver emits a capture; finalize receipts only after each log is closed. Supply real build/content/settings/input identity hashes and distinct run IDs. |
| P10 | The exact paired-run procedure follows. | Lead performs both arms, writes receipts and gets comparator PASS or records the mismatches. |

## P10 Lead run

Use the same project/build and default map `L_SevarogArena`. Run one fresh windowed editor process per arm through `Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1`; the new `Scripts/Editor/run_a4_parity_and_quit.py` wrapper applies the `RunDrivers.ps1` preconditions (`no_throttle`, `wake_clip_off`, `legend_off`, `build_off`, first-PIE `pie_debug_overlay` warm-up plus its 40 second settle), runs A4, waits for shutdown, and quits the editor. This keeps process-wide CVar state isolated and produces one complete raw log per arm. Run the legacy arm first. Do not reuse output paths.

```powershell
$repo = 'C:\UnrealProject\OneBossFight'
$editorRunner = Join-Path $repo 'Docs\BossCombatReview\Execution\Claude\run_editor_script.ps1'
$driver = Join-Path $repo 'Scripts\Editor\run_a4_parity_and_quit.py'
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
& $editorRunner -Script $driver -OutDir (Join-Path $repo 'Saved\A5Parity\P10_legacy') -Task 'P10-A4-legacy' -NullRhi 0 -PyCmd 1 -TimeoutSeconds 900
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
& $editorRunner -Script $driver -OutDir (Join-Path $repo 'Saved\A5Parity\P10_selected') -Task 'P10-A4-selected' -NullRhi 0 -PyCmd 1 -TimeoutSeconds 900
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
```

For each arm, write an identity JSON with the eight required `identity` fields (including SHA-256 values from the actual run/setup). Finalize receipts only after the editor log has stopped changing:

```powershell
python -I Scripts/Tools/write_a4_parity_receipt.py --log <legacy-log> --identity <legacy-identity.json> --run-id <unique-legacy-id> --out <legacy-receipt.json>
python -I Scripts/Tools/write_a4_parity_receipt.py --log <selected-log> --identity <selected-identity.json> --run-id <unique-selected-id> --out <selected-receipt.json>
python -I Scripts/Tools/compare_encounter_parity.py <legacy-receipt.json> <selected-receipt.json> --verify-source-logs --report-json <new-report.json>
```

The comparator must report PASS only when the declared A4 observations, trial set, build/map/settings/input identity, check totals, and terminal result agree. Activation, selected definition, participant generation and component census are retained for diagnosis and are allowed to differ by route. A differing combat observable is a mismatch for P13 triage, not a reason to edit the expected values.

Codex has not run Python tests, compiled C++, opened Unreal, or run PIE. Static Python AST and `git diff --check` have passed for the edited scripts/tooling; the Lead owns build, offline suite, and live evidence verification.

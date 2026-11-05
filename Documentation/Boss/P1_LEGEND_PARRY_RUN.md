# C-916 P1: perfect-parry slow-motion witness

Status: offline driver and checks authored; both live route arms remain Lead-run. The run is not yet accepted.

`Scripts/Editor/pie_legend.py` now has opt-in group `l8`. It calls the player's reflected `URPGPlayerParry::Press()` API, then uses a real A4 low-sweep contact. `URPGDamageResolver::Resolve()` calls `URPGPlayerParry::NotifyParried()` for that contact, so the observed grade and slow motion pass through the production contact path. The driver records global time dilation on the existing real-time frame sampler, contact-to-onset latency, 0.30 scale, real duration, restoration, and an `rpg.Legend 0` contact control.

H9 ordering fix: in a full-group run, L8 runs before L7 because L7 kills and the pack destroys the boss. L8 re-finds the current boss after its reset and reports a clear failure if it is missing before looking up boss components.

## Lead run

Run a fresh editor process per route, same `L_SevarovArena`, build, and input setup. Set `Saved/legend_groups.txt` to the single line `l8`. Legacy arm:

```powershell
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
Set-Content Saved/legend_groups.txt 'l8'
powershell -ExecutionPolicy Bypass -File Scripts/RunDrivers.ps1 -Only pie_legend -TimeoutSeconds 900
```

Selected arm:

```powershell
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
Set-Content Saved/legend_groups.txt 'l8'
powershell -ExecutionPolicy Bypass -File Scripts/RunDrivers.ps1 -Only pie_legend -TimeoutSeconds 900
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
```

Retain raw logs and verify: actual A4 parry count increments; first contact occurs within the first 40% of the 0.25 s parry window; global dilation onset is within two sampled frames of contact; scale is 0.30 ±0.02; duration is 0.35 s real time ±2 sampled frames; and prior global dilation is restored. The gate-off control must still register a real parry contact and remain at normal dilation. A5 receipts use the updated `pie_legend` minimum of 25 checks when the full group set runs; for the `l8`-only rerun, compare the specific `[Legend]` checks and retain the raw logs rather than treating the full-run minimum as an L8 check count.

## Acceptance constraint found

The requested second **perfect** parry during the slow-motion policy's 0.60 s cooldown cannot be produced through the current player API: `RPGParry::DefaultCooldownSeconds` is 0.70 s (`Source/OneBossFight/Player/RPGParryRules.h`), while the participant slow-motion policy cooldown is 0.60 s (`RPGEncounterBinding.h`). The second `Press()` is therefore correctly refused before another contact can receive a perfect grade. L8 records this refusal/no-new-scope, but that is not evidence of a second perfect parry. Existing native coverage also checks an immediate chained slow-motion request. A true second-perfect-contact live assertion needs a revised policy relationship or a separately approved test seam; neither was introduced here.

Offline validation: `python -m unittest Scripts.Tools.test_legend_parry_slow_motion_driver Scripts.Tools.test_a5_parity_driver_registration -v` and `python -m py_compile Scripts/Editor/pie_legend.py`. No Unreal, editor, PIE, or C++ build was run by Codex.

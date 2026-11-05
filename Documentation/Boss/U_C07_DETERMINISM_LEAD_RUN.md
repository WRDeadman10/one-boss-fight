# U-C07 — Determinism Lead-run sheet

Status: driver and offline comparator authored; all six PIE arms per capture and the comparison are **LEAD-RUN**. Codex has not launched Unreal or built the project.

## Preconditions

- Use the same Development Editor build, PC/session, map (`L_SevarovArena`), graphics settings, and driver for both captures.
- Set `H019_ENCOUNTER_DEFINITION` to the current selected encounter asset path. The legacy arms clear selection; data arms use this value.
- Use the same seed (default `20261105`, or an explicit uint32 in `OBF_DETERMINISM_SEED`) and unchanged fixed schedule embedded in `Scripts/Editor/pie_determinism.py`.
- Give each capture a separate, empty output directory. Example: `Saved/U-C07/capture_a` and `Saved/U-C07/capture_b`. Do not reuse an existing receipt folder.
- In UE Python, run the driver source with `exec(open(r"<project>\Scripts\Editor\pie_determinism.py", encoding="utf-8").read())`. Importing it registers a Slate tick callback; it automatically starts the six sequential PIE arms and writes one receipt as it completes each arm. Each arm runs 35 seconds, plus PIE start/stop overhead.

## Capture sequence

Run the full six-arm driver twice with an identical build, seed, selected-definition path, and settings. Change only `OBF_DETERMINISM_OUT` between captures. Preserve both `determinism_runs.json` receipts and the matching editor/game logs. Each receipt must say `status=complete`, contain exactly legacy repeats 1–3 and data repeats 1–3, and have no fatal reason. A partial capture is invalid; start a fresh, empty output folder for a rerun.

Close the Editor, set environment variables in the shell that will launch it, and start the Editor from that same shell with the project. Set them before launching the Editor process, for example:

```powershell
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
$env:OBF_DETERMINISM_SEED = '20261105'
$env:OBF_DETERMINISM_OUT = (Join-Path (Resolve-Path 'Saved').Path 'U-C07/capture_a')
```

For capture B, close the Editor, change only the output path in the launch shell, restart the Editor from that shell, and execute the same script again.

## Offline comparison

```powershell
python Scripts/Tools/compare_determinism_runs.py Saved/U-C07/capture_a/determinism_runs.json Saved/U-C07/capture_b/determinism_runs.json
```

The comparator fails closed on an unsupported/partial receipt, missing or duplicate arm, seed/schedule mismatch, mismatched per-arm inputs, or any event-trace difference. It also compares every route/repeat against the first arm so legacy/data parity and all three repeats are checked. Preserve comparator output with the receipts. A PASS means the captured tracker decisions, counters/refusals, player montage transitions, and injected-input traces matched under this driver; it is not evidence of bitwise determinism outside these observed signals.

## Interpretation limits

The driver uses the Development-only `rpg.DeterminismSeed` hook to reset the `FMath` random stream before each PIE arm. It observes the attack tracker's current move/instance and commit/refusal counters plus player montage transitions. It does not capture all internal AI state, random streams owned by other systems, platform scheduling, or network behavior. A mismatch is diagnostic and should be retained with logs; do not weaken the comparator to turn a failure green.

Queue V-C028 added a regression for a non-object `runs[]` entry: the comparator now reports a structured error and missing arm instead of raising while indexing the malformed row. The comparator still requires a full receipt, and equality remains scoped to the observed tracker/input signals above.

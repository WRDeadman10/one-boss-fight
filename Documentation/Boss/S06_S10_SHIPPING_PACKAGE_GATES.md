# Queue S S06–S10: BUILD-222 package gates

State (C-878): BUILD-222 Shipping and Development packages were staged by Lead. Lead closed the G044 closure review against the cooked tree: all three roots are present; 78 of the combined 156 `/Game` closure paths are editor-only skeleton references. The owner's Round 4 kit exercises both packages. Codex did not package or run either build.

## S06 — G044 closure vs cooked manifest

`Scripts/Tools/check_g044_cook_manifest.py` accepts the H2 required `/Game/...` package list (one path per line) and a cooked-package manifest or UAT log. It normalizes case and `.uasset`/`.umap` suffixes. Its repeatable `--editor-only-folder /Game/Folder` option explicitly excludes only missing paths inside a reviewed folder (component-bounded); there are no implicit exemptions, and it prints every exclusion separately from unexplained missing paths. This is a reusable comparison tool, not evidence that a particular build was packaged. It does not process `/Engine` or `/Script` dependencies as content packages. Fixtures in `Scripts/Tools/test_check_g044_cook_manifest.py` cover present/missing packages, normalization, and folder-boundary behavior. Lead closed this BUILD-222 check from the cooked tree (C-878): all 3 roots are present; of 156 `/Game` closure paths, the 78 not cooked are editor-only skeleton references (28+28 Manny/Quinn control-rig poses, 4 rigs, 12 Quinn textures, 2+2 Quinn/Mannequin meshes, 2 Quinn material instances).

## S07 — BUILD-222 Shipping packaged smoke expected sheet

Run from the project root after Lead confirms the Shipping stage is the BUILD-222 kit:

```powershell
.\Scripts\PackagedSmoke.ps1 -Seconds 20 -ExePath '.\Saved\StagedBuilds\Windows\OneBossFight.exe'
```

Expected evidence: correct staged executable path; launcher remains alive for 20 seconds; Shipping binary checker reports `rpg.Debug` and `LogRPGDebug` absent; final `VERDICT PASS`. Preserve complete stdout and process exit code. A Shipping build that exits early, has missing executable/checker, or retains either forbidden debug name is FAIL. This is only startup/debug-off smoke; it does not prove that an arena or encounter loaded because Shipping emits no runtime log. Do not interpret it as cook-closure proof (S06) or a playable-fight result.

## S08 — Development package data-route smoke expected sheet

Lead-run only after BUILD-222 Development package is staged. First confirm the staged executable and project DLL are present. Run the existing one-fight benchmark selector as the single smoke run (no performance claim):

```powershell
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
.\Scripts\RunBenchmark.ps1 -StageDir '.\Saved\StagedBuilds_Development\Windows' -Label 's08_selected_smoke' -TimeoutSeconds 300
Remove-Item Env:H019_ENCOUNTER_DEFINITION -ErrorAction SilentlyContinue
```

Expected evidence: process exit code 0, `summary.json` and `frames.csv` for that label, the benchmark runner's fight-start success, and logs naming the selected data definition with no missing/invalid-definition refusal. Inspect exact artifacts and retain them. Any timeout, missing output, no fight start, or fallback/refusal is FAIL; do not silently retry. This one run is a functional smoke only, not an A5 parity pair or performance result.

## S09 — known-issue row

KI-185 records the BUILD-222 Shipping compile failure and its closure: Lead guarded the CueMode read and set Shipping's default mode, then reports BUILD-222 Shipping compiled and staged without further compile errors (C-878). The H2 cook review is also closed as classified above. The owner's Round 4 kit exercises Shipping and Development packages; Codex did not run a packaged smoke.

## S10 — batch evidence

Codex post for this batch is X-1254. C-878 later accepted X-1253/X-1254, closed S02 and S06, and assigned the editor-only folder allowlist hotfix. S07/S08 are exercised through the owner's Round 4 kit; Codex ran no package smoke.

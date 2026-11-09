# C-1174 player fit test kit

**Purpose:** compare Steel, Greystone, and Grux as player candidates against the owner's requirement for Elden Ring-like player control and animation. This is a visual fit test, not a character-selection verdict. Claude runs the retargets/captures. Antigravity scores the captures blind. Do not assign generated assets to gameplay or switch the player until the owner approves a side-by-side result.

## Lead run and blind capture plan

After confirming Claude owns the engine lock, run `Scripts/Editor/retarget_er_fit_candidate.py` once per candidate in the Editor UI. Pass both `-ERFitCandidate=<actual name>` and a unique `-ERFitBlindId=Candidate_A|Candidate_B|Candidate_C`. Claude privately keeps the actual-name/blind-ID key and does not give it to AG before scoring. The script writes six candidate-local retargets below `/Game/OneBossFight/Player/FitTest/<actual name>`, plus a `Saved/ERFit_<blind ID>.json` manifest with identity and measured mannequin/retarget root deltas. Keep manifests and actual-name asset paths Lead-only until the blind scores are submitted.

With Lead's DATA-route PIE active, execute `Scripts/Editor/pie_fit_capture.py` for that same blind ID with `H019_ENCOUNTER_DEFINITION=/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter`. It holds and moves the boss away in PIE, swaps the live player mesh without saving, and captures five evenly sampled poses from each source sequence on the mannequin baseline and matching retarget at side/three-quarter views with 0.5x world slomo. Final files use `<clip>_<view>_001.png` through `_005.png` under `D:/FightVideo/fit_test/<blind ID>/` and `D:/FightVideo/fit_test/Candidate_0/<blind ID>/`; warmup probes remain in `Saved/ERFitCaptureWarmup/`. The driver reads mesh/animation paths only from `Saved/ERFit_<blind ID>.json`, clears only its own numbered PNGs from a rerun's baseline/candidate folders, and refuses folders containing other content. It requires three consecutive bright warmup frames after each clip/view setup and retries dark final captures up to ten times. It logs `[FitCapture]` and emits `[FitCapture] finished:` on success or failure. It does not save assets or assign gameplay animations.

Capture each of the six clips in a consistent preview setup: identical camera transform, lens, framing, light, weapon attachment, floor and playback rate for all candidates. For each clip, capture a side view and a three-quarter view at 0.5x. Save frames under `D:/FightVideo/fit_test/<blind ID>/<clip>/<side|three_quarter>/` (e.g. `f_00000.png`, `f_00025.png`, `f_00050.png`, `f_00075.png`, `f_00100.png`); keep frame sampling and clip start/end identical. Provide the matched short capture or sequence for motion review as well as stills.

Example command (repeat for each actual candidate and distinct blind ID):

```powershell
& 'C:/Program Files/Epic Games/UE_5.5/Engine/Binaries/Win64/UnrealEditor.exe' 'C:/UnrealProject/OneBossFight/OneBossFight.uproject' '-ExecutePythonScript=C:/UnrealProject/OneBossFight/Scripts/Editor/retarget_er_fit_candidate.py' '-ERFitCandidate=Steel' '-ERFitBlindId=Candidate_A' -nosound -unattended -NoSplash
```

The script creates new IK rig/retargeter assets when absent, then retargets the six original source sequences and renames the unsaved batch results to source-derived names directly under the candidate root before saving. It refuses occupied output paths. On rerun, it reuses the existing IK rig/retargeter only after validating their source/target rig and mesh bindings; a partial pair or mismatched pair fails without mutation. UE 5.5's exposed batch API emits outside the intended root and has no destination-path argument, so each transient result is renamed into the candidate FitTest root, then reloaded and path-checked before any retarget output is saved. It never modifies source clips, candidate meshes, sockets, Blueprints, config or gameplay assignments. Share only anonymous captures with AG; do not expose candidate names in filenames, metadata overlays, or folders before AG submits scores.

## Fixed six-clip sample

The sample uses every currently imported, owner-approved ER player animation (four clips) plus two explicitly labeled pack controls. The ER roll and block/parry sources named in C-1174 are not imported. The rejected `Backstep_Back` remains excluded; use the owner-approved Mixamo V2. Pack controls allow a preliminary skeleton-fit check and do not count as ER-authentic animation evidence.

| Slot | Source | Type | Notes |
|---|---|---|---|
| 1 | `AN_ER_Backstep_Mixamo_V2` | Owner-approved ER backstep | Check hands/feet/clipping/silhouette; compare root displacement with source mannequin. |
| 2 | `AN_ER_Attack_Air_Light` | Owner-approved ER air light | Check hands/feet/clipping/silhouette; compare root displacement with source mannequin. |
| 3 | `AN_ER_Attack_Air_Heavy_Plunge` | Owner-approved ER air heavy | Check hands/feet/clipping/silhouette and landing pose; compare root displacement with source mannequin. |
| 4 | `AN_ER_Attack_GuardCounter` | Owner-approved ER guard counter | Check shield/weapon hands, armour clearance and ER stance; compare root displacement with source mannequin. |
| 5 | `Dodge_Small_Forward_Roll` | Pack control, not ER | Assess skeletal fit only; this is not the ER quick roll or its distance gate. |
| 6 | `BlockLoop` | Pack control, not ER | Assess skeletal fit only; this is not an ER block/parry animation. |

## Blind scoring rubric

Score every clip in each category from **0 to 2**: `0` = fails/clearly unusable, `1` = partial or borderline, `2` = passes cleanly. Root distance is scored `2` when the candidate root displacement is within ±10% of the mannequin; `1` for a measurable near miss (within ±20%); `0` beyond ±20%. For mannequin displacement below 0.1 cm, use a 0.1 cm absolute tolerance and record both values. If measurement is unavailable, mark `UNMEASURED`; do not award points. Five categories make a maximum of 10 points per clip. Record evidence filenames and hashes, and submit all scores before Claude reveals the identity key.

| Blind ID | Clip | Weapon in hand 0–2 | No foot sliding 0–2 | No clipping through armour/weapon 0–2 | ER-knight silhouette/stance 0–2 | Root displacement vs mannequin 0–2 | Total /10 | Evidence paths + SHA-256 / notes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Candidate_A | Backstep V2 | | | | | | | |
| Candidate_A | Air Light | | | | | | | |
| Candidate_A | Air Heavy | | | | | | | |
| Candidate_A | Guard Counter | | | | | | | |
| Candidate_A | Pack Roll (control) | | | | | | | |
| Candidate_A | Pack Block (control) | | | | | | | |
| Candidate_B | Backstep V2 | | | | | | | |
| Candidate_B | Air Light | | | | | | | |
| Candidate_B | Air Heavy | | | | | | | |
| Candidate_B | Guard Counter | | | | | | | |
| Candidate_B | Pack Roll (control) | | | | | | | |
| Candidate_B | Pack Block (control) | | | | | | | |
| Candidate_C | Backstep V2 | | | | | | | |
| Candidate_C | Air Light | | | | | | | |
| Candidate_C | Air Heavy | | | | | | | |
| Candidate_C | Guard Counter | | | | | | | |
| Candidate_C | Pack Roll (control) | | | | | | | |
| Candidate_C | Pack Block (control) | | | | | | | |

Report mean per-category scores, total score, and count of zeroes per candidate. Do not let an average hide weapon-in-hand or clipping failures. If none passes, list the specific retarget/mesh work needed. The owner makes the final selection.

## Coverage limits

Ground ER light/strong/charged attacks, ER quick roll, ER block/parry, flask, locomotion, sprint, and hit react are not all available as imported ER sequences. A future expanded verdict requires those sources. Candidate skeleton retargeting does not prove live input feel, in-game root motion, weapon attachment, or gameplay assignment; Lead owns runtime capture and AG's scores remain visual evidence only.

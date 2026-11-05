# F-AG5 BOSS-MOV-001 range-band partition proof

Source row: ledger v3.36 `BOSS-MOV-001`, `observable` values: Melee 0-220 cm, Close 150-350 cm, Medium 200-400 cm, Gap-Closer 400-950 cm. Existing BUILD-148 evidence (`Documentation/TEST_PLAN.md`; `Docs/BossCombatReview/Execution/Claude/B_MOV001/pie_R150`, `pie_R300`, `pie_R700`) authors Medium/Gap cards and shows range refusals, while Melee/Close currently rely on older cards with narrower ranges.

## Setup

Lead runs `create_range_partition_content.py` once in the Editor. It creates only unique `FAG5` card/profile/map assets, refuses any existing destination, and asserts each property readback. Existing content is not modified. The boss spawn is x=580 cm; PlayerStart x positions are 380, 220, 100, and -220 cm, so initial separations are 200, 360, 480, and 800 cm. Each starts at least 80 cm beyond its profile's maximum range to ensure a real approach path rather than starting inside the band. The run's intended live sample distances remain 100, 250, 375, and 700 cm. These ranges intentionally overlap: at 250 cm both Close and Medium should be eligible; do not require exclusive Close selection.

## Control

Use existing BUILD-148 raw logs `pie_R150`, `pie_R300`, and `pie_R700` as historical controls for the already-authored Medium/Gap cards. The new close/melee cards and four new profile/map pairs are isolated additions; preserve the existing source map/card hashes. The 250 cm Close case intentionally overlaps Medium and must not be treated as a failed negative control.

## Runs

Run from `Docs/BossCombatReview/Execution/Claude/F4`:

```powershell
$base = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4'
& "$base\run_pie.ps1" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofFAG5_Melee100 -OutDir 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\F_AG5_MOV001\melee100' -Task F-AG5_MOV001_melee100
& "$base\run_pie.ps1" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofFAG5_Close250 -OutDir 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\F_AG5_MOV001\close250' -Task F-AG5_MOV001_close250
& "$base\run_pie.ps1" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofFAG5_Medium375 -OutDir 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\F_AG5_MOV001\medium375' -Task F-AG5_MOV001_medium375
& "$base\run_pie.ps1" -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofFAG5_Gap700 -OutDir 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\F_AG5_MOV001\gap700' -Task F-AG5_MOV001_gap700
```

## PASS

- Every raw log validates with `validate_framework_proof_logs.py` and ends in a successful `RESULT`.
- At 100 cm, `Move_Sevarog_Melee_FAG5` is a candidate and Close/Medium/Gap cards have `MoveModel.Range` refusals.
- At 250 cm, Close and Medium cards are both candidates; Melee and Gap cards are refused. This overlap matches the authored intervals.
- At 375 cm, Medium is a candidate and Melee/Close/Gap cards are refused.
- At 700 cm, Gap is a candidate and Melee/Close/Medium cards are refused.
- Candidate/refusal logs, profile/card identity, live range, and each map label establish the four range cases. Report any card range mismatch separately from selector choice.

## Token checks

- `[FrameworkProof] candidate attack=... card=Move_Sevarog_Melee_FAG5` / `Move_Sevarog_Close_FAG5` / `Move_Sevarog_BandMedium_MOV001` / `Move_Sevarog_BandGap_MOV001` at the expected sample ranges.
- `[FrameworkProof] refusal attack=... card=... reason=MoveModel.Range` for out-of-band cards.
- `[FrameworkProof] decision attack=... chosen=... range=...` and successful `[FrameworkProof] RESULT outcome=...` in every run.
- `[FAG5_MOV001]` setup readback lines for each profile/map, plus validator summary.

## FAIL

Fail if a named card's candidate/refusal conflicts with its configured min/max range, the live distance is outside the intended sample tolerance, a new content destination already existed, any asset readback assertion fails, or the validator finds malformed evidence. Overlap at 250 cm is expected.

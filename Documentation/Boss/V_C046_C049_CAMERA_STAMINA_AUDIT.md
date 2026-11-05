# Queue V Codex batch: V-C046–V-C049 camera and stamina/poise

Source audit only. Existing Lead camera runs are cited from archived receipts; no new PIE, build, or editor run was made for this batch. Proposed changes remain proposals.

## V-C046 — camera distance, collision, and framing

| Check | Evidence | Finding |
|---|---|---|
| Boss framing at distance | `Docs/BossCombatReview/Execution/Claude/B_QA006/framing_report.json`: 73 samples; near/300/600/900 cm bands all pass; every band has `any_occluded=false` and minimum boss-height ratios 66.9%, 46.97%, 32.23%, 24.24%. | The archived measured baseline passes its framing threshold (12%). It is a 918×402 viewport dataset, so do not represent it as a packaged 1080p check. |
| Negative control | `control_report.json`: 69 samples; when camera is turned away in the 900 cm band, minimum height is 94.62% and the band fails framing. | Expected off-screen control demonstrates the evaluator rejects a lost target; not a product defect. |
| Spring-arm collision | `RPGCameraRig::Apply` forces collision on, applies a 34 cm probe on `ECC_Camera`, attaches the boom to capsule, and applies bounded lag / pitch. `pie_camera_scenarios.py` covers death/ragdoll, low dodge, wall-facing camera, and jump/land. | Source and driver coverage exist. Current archived run receipt in this audit is the QA006 framing dataset; scenario-driver live results are not asserted here. |
| Lock-on range | QA006 tests staged 300/600/900 cm camera-to-boss bands; these are probe distances, not lock-on acquisition/release thresholds. No authored lock-on distance requirement was identified in the reviewed camera rig. | Lock-on distance acceptance remains unspecified; do not treat camera probe bands as lock-on range. |

## V-C047 — stamina, poise, and posture

Freeze v1.2 section 5 calls out 35 stamina per Strength swing (confirm resource scale), 10 per Dexterity swing, Strength posture 18 light / 38 jumping heavy, and Dexterity posture 6 light / 14 jumping heavy. The same Freeze separates player `PoiseImpact` from boss posture accumulation.

| Attack row | Freeze target | Current `RPGWeaponAttackTable::FillDefaults` | Finding |
|---|---|---|---|
| Strength light | 18 posture; 35 stamina per swing | 18 posture; `StaminaCost=-1` (retain pack base cost 15) | **Confirmed mismatch:** configured light swing charges 15, while Freeze says 35 per swing. `pie_stamina_cost.py` identifies pack base cost 15 and tests 35 only with a test override. Logged as KI-190; no tuning changed. |
| Strength jumping heavy | 38 posture; 35 stamina | 38 posture; 35 stamina | Matches authored row. |
| Dexterity light | 6 posture; 10 stamina | 6 posture; 10 stamina; 20 bleed | Matches authored row. |
| Dexterity jumping heavy | 14 posture; 10 stamina | 14 posture; 10 stamina; 20 bleed | Matches authored row. |
| Boss posture pool | 100 posture, separate from poise | `RPGBossPosture::PostureMax=100`; pack poise is pinned separately | Correctly distinct resource concepts. |

Incoming boss attacks' Freeze fields describe qualitative player poise impact (for example Light Flinch, Medium Stun, Heavy Knockdown) rather than a numeric scale. This source audit does not claim a measured per-move player-poise application result; the existing poise probes need a current Lead receipt for that claim.

## V-C048 — proposals only

1. Resolve whether Strength's 35 stamina target applies to every swing or only heavy swings. Keep current runtime unchanged until the owner/Lead clarifies the Freeze wording.
2. Have Lead attach attack/dodge/parry latency samples for both routes using the new C041 driver, then decide whether measured startup warrants any change.
3. Keep C042/C043 changes gated on live feel/telegraph captures; the current artifacts compare settings and source timing, not player readability.
4. Define lock-on acquisition/release range acceptance before proposing a camera distance change. Existing 300/600/900 cm samples are framing probes only.
5. Retain the 34 cm probe and current camera behavior unless a fresh packaged/target-resolution capture shows clipping or lost framing.

## V-C049 — issue ledger

Added KI-190 for the source-confirmed Strength light stamina discrepancy. No further rows were added: the other items are either existing positive camera evidence or still await Lead runtime measurements / owner acceptance.

## Evidence

- Freeze: `Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md` sections 4, 5 and 20.1–20.2.
- Camera: `Source/OneBossFight/Player/RPGCameraRig.h/.cpp`; `Docs/BossCombatReview/Execution/Claude/B_QA006/framing_report.json`, `control_report.json`; `Scripts/Editor/pie_camera_scenarios.py`.
- Attack costs: `Source/OneBossFight/Player/RPGWeaponAttackTable.cpp`, `RPGSwingTracker.cpp`; `Scripts/Editor/pie_stamina_cost.py`.
- Separate poise/posture data: `Source/OneBossFight/Player/RPGBossPosture.h`; `Scripts/Editor/poise_data.py`, `pie_poise_scale.py`.

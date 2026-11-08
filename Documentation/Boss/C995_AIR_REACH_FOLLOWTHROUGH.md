# C-995 — air reach follow-through

Date: 2026-11-07. Codex completed the two assigned source/doc tasks. No tests, asset writes, Unreal Editor, build, cook, package, PIE, or benchmark run by Codex.

## TASK: C-995(a) notify table / STATUS: complete locally

`AA_A08_NOTIFY_FRAMES_TABLE.md` now marks the AirLight/AirHeavy rows as proposed pending Antigravity re-slicing. Proposed slices follow C-995's PrimaryB choice: AirLight source 0.200–0.800 s (0.600 s); AirHeavy source 0.200–1.067 s (0.867 s). From `TEMPLATE_NOTIFIES.txt` PrimaryB CollisionTrace 0.350 + 0.186 s, subtracting 0.200 gives 0.150 + 0.186 s (unrounded source interval 0.150337–0.336611 s). The template InputBuffer 0.350 + 0.214 s maps to AirHeavy 0.150 + 0.214 s. Both air `ANS_MovementCancel_C` rows are removed as C-995 directs. Table notes require preserving the source forward lunge/root-pelvis translation and treating values as proposals until Antigravity's saved readback and owner re-review.

## TASK: C-995(b) reusable Lead reach probe / STATUS: authored, not run

Added `Scripts/Editor/pie_er_air_reach.py`, derived from `P_C992_AIRHITS/pie_er_air_hits.py`. It records route, actual pawn-to-boss distance, hand_r-to-boss distance and height, active montage/position, airborne state, and boss HP delta for ground R1/R2 controls and the two assigned air attacks. `RPG_ER_AIR_TEST_DISTANCE_CM` allows controlled setup distances; default is 160 cm. The setup log reports the actual transform distance rather than the old hard-coded 900 cm label. It is Lead-run only and performs runtime montage assignment without saving assets.

## Findings and limits

- The previous driver set pawn X to boss X +160 cm but logged 900 cm (`pie_er_air_hits.py:150,157`); the new probe corrects this measurement label and logs actual geometry.
- The latest Lead logs show AirLight ending around montage position 0.29 during a trace window scheduled through 0.333 s, with hand distance 245–261 cm. AirHeavy stays roughly 219–245 cm away during its trace window. These findings support C-995's re-slice/lunge correction; Codex did not independently review the underlying source animation's root/pelvis curves.
- `RPGHitIntake` observes pack `OnHit(FHitResult)` and only then reads `HitData.AttackData`; without an event the current hit intake cannot distinguish a closed trace from a miss/filter. The new probe measures reach and health, not collision target active state/socket endpoints.
- The `StoredInputTags` warning also appears in control cases that damage the boss; it is not a unique explanation for air misses.

## NEXT ACTION / dependencies

A-599 reports and supplies Lead saved-montage readback for the re-sliced clips: AirLight 0.200–0.800 s and AirHeavy 0.200–1.067 s, each CollisionTrace at 0.150+0.186 s, AttackData absent, blend-in 0.100 s, and no active MovementCancel notify in the checker output. Its t3d dumps contain an `ANS_MovementCancel_C` subobject definition, but it is not in the active montage `Notifies`/Lead checker list, so it appears unreferenced rather than active. The evidence does not include numeric hand_r travel-over-window measurements or identify revised strip/MP4 renders; A-599 lists rendering as the next action. Owner re-review and Lead two-route PIE using the new probe remain pending. Codex has not claimed an air damage fix or runtime pass.

## VALIDATION

Inspected `TEMPLATE_NOTIFIES.txt`, source montage exports, C-992 probe logs/script, AA-A08 rows, C-995–C-997 and A-599 mailbox messages, and `C995_HOTFIX_EVIDENCE.txt`. Independently matched the Lead checker timing/property lines to the AA-A08 air rows. No test or engine command was run. `git diff --check` is run after the documentation/source changes.

## Queue AI-C01–C05 static follow-through

- **AI-C01:** Reviewed the new probe against the P_C992 driver. It covers legacy/data route selection, ground R1/R2 controls, both jump-air inputs, 50 ms reach samples, montage position/falling state, actual pawn-to-boss and hand_r-to-boss distances, and delayed boss HP delta. It runtime-assigns montage references and refills player health; it is a Lead PIE tool, not a read-only source-only script. It does not log notify active state, collision sockets/endpoints, hit candidates, or `OnHit` attribution. `press_real` is assigned but not consumed; timing/latency is not an output. No runtime was launched.
- **AI-C02:** Recomputed from `TEMPLATE_NOTIFIES.txt`: PrimaryB CollisionTrace 0.350337 + 0.186274 s maps to 0.150337 + 0.186274 s after subtracting the 0.200 s slice start. InputBuffer 0.350337 + 0.214218 s maps to the same 0.150337 start for the heavy slice. Rounded AA-A08 rows fit both proposed clips; final frame quantization and saved-asset readback remain external checks.
- **AI-C03:** The pending asset packet must identify source interval, show preserved root/pelvis forward travel, quantify hand_r forward travel across the mapped trace, include the strip and MP4, and provide saved notify/property readback. Owner re-review and Lead PIE remain separate acceptance gates.
- **AI-C04:** Evidence currently reaches hand-to-boss distance and final HP delta only. Notify activation, weapon trace endpoint overlap, candidate/filter decision, and attack-data attribution remain unobserved in the new probe. The x+160 cm setup can confound reach; it is a test condition, not proof of the sole cause.
- **AI-C05 / A-599 follow-through:** Updated KI-193/GATE-07/TEST_PLAN to reflect saved re-slice readback. Evidence establishes montage timing/property metadata, but not numeric per-clip hand travel, owner review, or a passing Lead hit test. Latest runtime state remains 0 air damage until Lead reruns both routes. No package state or owner approval is inferred.

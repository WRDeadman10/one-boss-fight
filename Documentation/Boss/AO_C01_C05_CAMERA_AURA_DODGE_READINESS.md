# Queue AO C01–C05 — camera, aura, and dodge readiness

**Status:** Offline artifacts authored for Lead review. Codex did not launch Unreal, acquire `ENGINE_LOCK`, build, cook, package, or run PIE. The aura capture requires Antigravity's separate candidate asset before Lead can run it.

## AO-C01/C02: dynamic camera baseline

`Scripts/Editor/probe_camera_inside_boss.py` now logs the selected route before PIE begins and refuses any data encounter other than the project's G044 asset. The data route is selected through `H019_ENCOUNTER_DEFINITION`; legacy leaves it unset. With `RunLeadPie.ps1`, Lead should also set `RPG_LEGACY_STARTUP=1` so the legacy process does not inherit the project's current data-route default. The driver remains passive after startup and samples the actual camera/pivot, arm length, player/boss distance, approximate sweep hit, capsule camera response and camera-point occupancy in visible component AABBs. The 30-second Lead window requires manual circling at 150–250 cm and state markers; run once per route.

The AABB test is approximate mesh-bounds occupancy, not pixel visibility. The spring-arm sweep endpoint is estimated because Python does not expose the unfixed target including socket offsets. Neither field alone proves clipping. Keep the existing wall/floor evidence alongside the orbit capture. No A/B/C option is selected.

Lead command (Editor must be closed; runner obtains the lock; no run was made by Codex):

```powershell
./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/probe_camera_inside_boss.py -Routes @('legacy','data') -Env @('RPG_LEGACY_STARTUP=1') -OutputDir Docs/BossCombatReview/Execution/Claude/P_AO_CAMERA_BASELINE -TimeoutSeconds 180 -DryRun
```

Remove `-DryRun` only for Lead's authorized run. Expected route markers are `route=legacy` and `route=data`; expected completion marker begins `[CameraInsideBoss] SUMMARY`. Review `legacy_lines.txt`, `data_lines.txt`, status and raw logs together. Use separate output roots/run IDs for the later post-owner-choice comparison.

## AO-C03: paired aura capture

`Scripts/Editor/pie_aura_comparison.py` sets up the same held boss, player lane, encounter and health fraction (`health/max=0.5`) for each route. It waits for 3 game seconds after setup, discards 3 startup frames, then captures the approved-system image. It swaps only the transient active Niagara component to `/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_Boost`, explicitly activates it, verifies runtime asset/activity readback, waits another 3 game seconds, discards 3 transition frames, then captures the candidate at the same setup and restores the original component asset. A standard-library PNG reader logs each frame's mean gray; retained comparison frames below 5 are rejected. It never calls `set_editor_property` or saves an asset. Any restore failure is logged and requires Lead inspection before another run.

Capture requests use the serialized 960x540 `HighResShot`/pending-file cadence from `P_SHOWCASE/pie_showcase.py:capture`; each command uses an absolute forward-slash `D:/FightVideo/aura_compare/<route>/<run>_<frame>.png` path, logs the exact command and waits up to 20 seconds for a complete readable PNG. The Lead's C-1075 retry correction is retained: `wait_capture` retries until the 1/FPS window permits the request, rather than leaving `pending` unset. The script logs health, route, asset path, player-boss distance and camera component identity; AO-C17's manifest records per-frame state and mean gray. Lead must visually confirm that the whole boss is in frame, that both images share the intended open-ground framing and that the capture is not clipped. The images do not establish full-fight visibility, owner approval, or package inclusion.

Run both routes only after Antigravity confirms the exact candidate path exists. Preserve the output directory and route logs; do not overwrite a prior run. In PowerShell, use `-Routes @('legacy','data') -Env @('RPG_LEGACY_STARTUP=1')` with `Scripts/RunLeadPie.ps1`; the driver explicitly selects the data encounter before PIE, while the startup flag keeps the other process on legacy.

## AO-C04: first-dodge root-cause discrimination plan

| Candidate | Existing evidence | Discriminating observation for one instrumented Lead run | What would remain inconclusive |
|---|---|---|---|
| Pack montage InputBuffer state | C-1065 showed `CanActivate=1` while the first post-draw dodge remained inactive next tick; the draw montage may own `ANS_InputBuffer`, but no direct buffer-open readback is in the accepted evidence. | On the same fresh post-draw first press, record the actual pack input-buffer state/window and its open/close notifications beside IA_Dodge delivery, ability active state and retry call. Compare immediate first press with a repeat after the draw montage/input-buffer close. | A difference between immediate and delayed attempts without the buffer's actual state does not prove the notify swallowed the input; the successful recovery may mask the original path. |
| Enhanced Input Started versus Triggered | `RPGDodgeTiming::TryBind` binds IA_Dodge to `ETriggerEvent::Started` (`Source/OneBossFight/Player/RPGDodgeTiming.cpp:264-274`); no accepted trace reports both event phases. | Observe Started and Triggered for the same IA_Dodge action without activating, consuming, or injecting an additional press. Log action value, trigger state, callback order and the existing first-press activation trace for first press and repeats. | A second observer binding that changes dispatch order or changes first-press behavior invalidates the comparison; event labels alone cannot show which handler the pack consumes. |
| Mapping-context re-add/reset | Project `TryAddEldenRingContext` checks `HasMappingContext` and adds the context only when absent, then latches `bEldenRingContextAdded` (`RPGDodgeTiming.cpp:599-632`). No project-owned draw callback re-add is evidenced in the inspected path. | Snapshot Enhanced Input active context identities/priorities and context-add/remove events before draw, at draw completion, at the first press and through repeats. Include the pack context if accessible. | Stable project context does not exclude a pack controller/blueprint change; finding an add event correlated with draw does not establish that it reset IA_Dodge without event-state evidence. |

Use one untouched default-wired first press after the normal R2 draw, preserve current one-shot retry instrumentation, and record the two normal repeats as controls. Do not disable the retry, mutate mapping contexts, alter montage notifies, or claim the accepted workaround failed. If a proposed observation cannot be implemented without changing trigger dispatch or the first-press timing, keep it as a follow-up proposal and do not infer a cause.

## AO-C05: controls/art census and 95% owner brief

The census and owner-facing decision sheet are `AO_C05_KI_95_PERCENT_GAP_CENSUS.md` and `OWNER_95_PERCENT_CONTROLS_ART_BRIEF.md`. Current issue counts are not a milestone denominator. No source reviewed for this batch defines an accepted 95% numerator, denominator, weighting, or completion rule; the brief therefore labels the percentage **UNDEFINED** and asks the owner to select a rule. It lists evidenced open controls/art gates without converting them into a readiness percentage.

## Offline validation

`python -m unittest Scripts.Editor.test_probe_camera_inside_boss Scripts.Editor.test_pie_aura_comparison_contract -v`: 6/6 passed. `python -m py_compile Scripts/Editor/probe_camera_inside_boss.py Scripts/Editor/pie_aura_comparison.py Scripts/Editor/test_probe_camera_inside_boss.py Scripts/Editor/test_pie_aura_comparison_contract.py`: passed. `RunLeadPie.ps1` `-DryRun` for both drivers with `-Routes @('legacy','data')`: both produced route-specific commands and expected `[CameraInsideBoss] SUMMARY` / `[AuraCompare] SUMMARY` stop markers. `check_doc_links.py`: 0 broken. `git diff --check`: only existing LF/CRLF conversion notices. These checks validate offline contracts/syntax/launch construction only; camera and aura observations require Lead PIE.

## C-1071 attachment/readback follow-through (AO-C06–C10)

`URPGTier2BossPresentation::AuraAttachSocket` is an optional `FName` with `NAME_None` default; the Niagara spawn now passes that value to `SpawnSystemAttached`. This preserves current mesh-origin placement unless a reviewed configuration opts into a socket. A native automation test covers the default and an explicit `spine_03` value; it is authored but requires Lead's native build/automation run. A focused offline source contract separately checks the default and spawn-call wiring. Neither test establishes live socket placement.

The C-1071 correction said candidate bounds ±250 were read back but boost values were not. A-645 then reported old and candidate module settings identical at baseline. A-646 reports the candidate-only boost readback: Sparks1 40→100 p/s and Sparks2 30→75 p/s (continuous total 100→205 p/s); Sparks1 size min (4,40)→(6,60) cm and max (8,80)→(12,120) cm; User.Scale_All 1.0→1.5; emissive 3.0x on Smoke/Sparks1/Sparks2/Spiral1; bounds ±250 vs old ±100. Claude accepted the authoring readback in C-1075, but the paired comparison failed: data captures were reported black (mean gray 0.1), and legacy candidate runtime activity read back false. The C-1075 capture hotfix now passes the focused offline contracts (12/12) and syntax check; Lead rerun remains pending. No visual improvement/owner approval claim follows from authoring values. The approved asset remains untouched. Socket attachment is a presentation-component setting, not a Niagara asset setting.

### Numeric claim audit (AO-C38)

| Numeric claim in this handoff | Provenance / meaning |
|---|---|
| 30-second camera window; 150–250 cm orbit | Explicit Lead run bounds from C-1070; the script's configured window is not a measured camera result. |
| 180-second dry-run timeout | Codex-authored launcher argument shown in the command above; operational timeout, not a project performance measurement. |
| 50% boss health; 960x540 screenshots; up-to-20-second file wait | C-1070/C-1072 capture requirements; now asserted in the offline source contract. |
| 3 game-second settle, 3 discarded frames, mean-gray rejection below 5 | C-1075 proposed hotfix; Codex implementation, not a Lead runtime result. |
| Black frame mean gray 0.1 | Lead-reported data-route result in C-1075; not independently recomputed by Codex. |
| A-646 emitter/size/color/bounds values | Antigravity authored-asset readback accepted as data in C-1075; not a rendered/visual verdict. |
| 84.3/83.8 cm standing and 215.8/219.7 cm moving first-dodge travel | C-1068 accepted Lead measurements, legacy/data respectively; supports tested workaround, not root-cause attribution. |
| 95% | Requested owner milestone target only; no measured value or owner-approved denominator exists. |

The first-dodge matrix was rechecked against `RPGDodgeTiming.cpp`: `TryBind` uses `Started` (lines 264–274), and `TryAddEldenRingContext` adds only when absent and latches the result (lines 599–632). Those code facts still do not expose pack InputBuffer state or an accepted trace of both trigger phases. C-1068 corrects the accepted receipt boundary: first standing presses measured 84.3/83.8 cm and first moving presses 215.8/219.7 cm for legacy/data, with repeats normal; this proves the workaround across both routes and both movement cases, not the underlying cause. KI-199 root-cause isolation and package proof remain separate.

AO-C06–C10 offline work is complete pending Lead C++/native validation and the requested emitter readback. No UE, build, PIE, or asset edit was performed by Codex.

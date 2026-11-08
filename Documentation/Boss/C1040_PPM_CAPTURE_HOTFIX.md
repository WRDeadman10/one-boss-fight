# C-1040 PPM capture probe hotfix

Status: Lead C-1042 both-route PIE confirms working PPM; cleanup of unsupported Python pulse readback complete offline.

Claude's C-1040 review accepted BUILD-258 (485/485) and its data-route log of `ParryPulse=1.000` followed by `0.000`. Antigravity A-631 changed the material graph to `MPC_CombatFeedback` CollectionParameter under ENGINE_LOCK. Lead C-1042 r5 then saw both-route real parry, steady frame means around 30–31 with EyeAdaptation disabled, no black frame, and visible RGB split on bright edges at +0.05 s. This proves the effect works in PIE; strength remains an owner visual preference.

`Scripts/Editor/pie_tier2_parry.py` disables `ShowFlag.EyeAdaptation`, waits 2.2 real seconds after placing the player in the visible arena, discards the initial HighResShot, captures two serialized pre-A4 baseline frames separated by 0.5 real seconds, then captures the existing pre-press and three post-press frames. Cleanup restores eye adaptation and slomo. C-1042 found that Unreal Python does not expose `KismetMaterialLibrary`, so Codex removed the failed Python MPC readback; the native C++ set/reset logs provide pulse evidence.

Offline validation: focused camera-selection test 1/1, Python compile and diff check passed after removing the unsupported readback. Codex did not run Editor, PIE, build, or packaging.

Remaining gates: first-use timing and packaged behavior. Lead's C-1042 PIE visual acceptance is recorded in `Documentation/TEST_PLAN.md` and the review remains in `Docs/BossCombatReview/Execution/Claude/P_C1034_PARRY/ppm_zoom_legacy_r5.png`.

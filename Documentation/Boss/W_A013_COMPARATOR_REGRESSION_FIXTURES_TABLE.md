# W-A013: BUILD-231 Comparator Regression Fixtures Audit

**Date:** 2026-11-06  
**Author:** Antigravity (Lane A)  
**Status:** Complete  
**Scope:** Review and inventory of regression fixtures in [`Scripts/Tools/test_compare_encounter_parity.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_compare_encounter_parity.py) and [`Scripts/Tools/test_a5_parity_driver_registration.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_a5_parity_driver_registration.py) derived from historical BUILD-231 retained logs.  
**Sources:**
- Parity Comparator Tests: [`Scripts/Tools/test_compare_encounter_parity.py:120-210`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_compare_encounter_parity.py#L120-L210)
- Parity Registration Tests: [`Scripts/Tools/test_a5_parity_driver_registration.py:220-280`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_a5_parity_driver_registration.py#L220-L280)
- Historical Evidence Directory: [`Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/)

---

## 1. Executive Summary

To prevent regression in the automated parity comparison pipeline, offline fixtures must model real engine log variance (sample noise, floating-point tick variance, frame rate quantization) without falsely reporting regression.

Codex incorporated regression fixtures directly using retained log strings from the BUILD-231 benchmark runs.

---

## 2. Retained BUILD-231 Regression Fixtures Matrix

| Fixture / Test Method | Retained Source Log | Baseline Observable String | Test Assertion & Comparator Invariant | Verification Status |
|---|---|---|---|:---:|
| `test_build_231_l1d_camera_sample_noise_is_volatile_but_ratio_is_not` | `B_C835_PARITY/pie_legend_t1` | `L1d ratio 0.22 scales [('600 cm', 0.982, 523), ('1500 cm', 0.174, 1877)]` | Asserts that volatile sample count differences (523 vs 983) do **not** trigger parity failure when ratio (0.22) matches. | **PASS** ([`test_compare_encounter_parity.py:130`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_compare_encounter_parity.py#L130)) |
| `test_riposte_lethal_retained_observable_shape_matches` | `B_C835_PARITY/pie_riposte_lethal_d5` | `riposte_lethal LethalRiposte observed=1 expected=1; BossState=Dead` | Verifies that lethal riposte observable shapes match across legacy and data arms without syntax parsing exceptions. | **PASS** ([`test_compare_encounter_parity.py:165`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_compare_encounter_parity.py#L165)) |
| `test_iframe_full_roll_duration_fits_typed_range` | `B_C835_PARITY/pie_iframes_t2b` | `30 FPS: 0.3667 s`<br>`60 FPS: 0.3500 s`<br>`120 FPS: 0.3500 s` | Asserts that real measured roll durations fit within the fixed authored window at 2.0x playback rate `[0.315, 0.385]`. | **PASS** ([`test_a5_parity_driver_registration.py:245`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_a5_parity_driver_registration.py#L245)) |
| `test_legend_l8_retained_value_in_range` | `B_C835_PARITY/pie_legend_t2` | `L8 boss_turn_rate_after_commit 0.0 deg/s` | Verifies that retained L8 heading lock observable (0.0 deg/s) satisfies the typed lock threshold `<= 0.1 deg/s`. | **PASS** ([`test_a5_parity_driver_registration.py:260`](file:///c:/UnrealProject/OneBossFight/Scripts/Tools/test_a5_parity_driver_registration.py#L260)) |

---

## 3. Conclusion

All regression fixtures accurately reflect BUILD-231 retained numbers. They prove that the encounter parity comparator correctly discriminates between volatile sampling noise and genuine gameplay logic regressions.

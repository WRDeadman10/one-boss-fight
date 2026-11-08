# Queue AM C26–C30: default-wired standing and moving dodge gate

Status: five offline tasks complete; Lead post-wiring PIE pending.

- C26: `P_C980_BACKSTEP/probe_legacy_lines.txt:11-12` reports 486.8 cm/s, nonzero last/pending input and `Dodge_Small_Forward_Roll_Montage` in the moving case. Data `probe_data_lines.txt:11-12` reports 474.2 cm/s, nonzero input and the same quick roll. Standing rows `:9` on both routes report `AM_ER_Backstep_Back`. Both logs `:4` show runtime assignment, so these are corrected movement-input observations but not default-wired proof. Earlier C-971 zero-input moving cases remain invalid. `RPGDodgeTiming.cpp:183-188` classifies no direction from `GetLastInputVector()` vs `NoInputThreshold=0.1` (`RPGDodgeTiming.h:95`); `RPGDodgeTiming.cpp:404-412` picks Backstep only with no direction and an available clip.
- C27: `Scripts/Editor/pie_er_default_wiring_dodge.py` removes the C-980 runtime backstep assignment, logs the Source default, and records speed, last and pending input at the actual key-down for standing and moving taps. Moving input is applied for 0.30 s before press. Observed montage and press-time movement are separate checks; the probe requires standing `AM_ER_Backstep_Back` with input below 0.1, and moving `Dodge_Small_Forward_Roll_Montage` with input >=0.1 and speed >=50 cm/s. It also checks ground R1 remained usable.
- C28: focused offline input/velocity boundary test passed 1/1. Python syntax and two-route runner dry run passed; no UE ran.
- C29: KI-196 remains OPEN but now acknowledges C-980's corrected runtime-assigned movement observations. The new default-wired two-route PIE is still required before classifying the Source default in live play. The owner-facing controls status reflects this distinction.
- C30: Lead run command follows; do not interpret game-tick observed delay as device latency.

```powershell
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_er_default_wiring_dodge.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_AM_C26_C30_DODGE
```

Acceptance for this slice: both route logs show three `CHECK ... pass=True` rows and `RESULT pass=True checks=3/3`, with the raw press-time speed/input and exact montage names. Codex did not run Editor, PIE, build or package.

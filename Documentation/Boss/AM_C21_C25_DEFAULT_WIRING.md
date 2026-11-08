# Queue AM C21–C25: default-wired ER ground/air hit gate

Status: five offline tasks complete; C-1042 Lead post-wiring PIE passed 4/4 per route; packaged runtime remains open.

C-1042 Lead follow-up: no-assignment default-wired PIE passed 4/4 on each route. Ground R1/R2 and AirLight/AirHeavy had exact expected clips and boss HP deltas (`Docs/BossCombatReview/Execution/Claude/P_C1042_DEFHITS/probe_legacy_lines.txt:8,11,66,121-122`, data `:8,11,67,123-124`). KI-193 now remains open for packaged runtime only.

## Evidence map

- C21: `RPGDodgeTiming.cpp:41-44` gives Source soft defaults for `AM_ER_Backstep_Back`, `AM_ER_Attack_GuardCounter`, `AM_ER_Attack_Air_Light` and `AM_ER_Attack_Air_Heavy_Plunge`. `RPGDodgeTiming.cpp:61-67,534-571` loads/uses air clips. BUILD-255 passed 484/484 PackWiring checks (C-1021). C-1004 r5 used *runtime assignment* (`P_C992_AIRHITS/R5_RESULT_probe_legacy_lines.txt:4`, data `:4`), then observed both-route AirLight `AM_ER_Attack_Air_Light` / about -15.99 boss HP (`legacy:17,66`, `data:17,65`) and AirHeavy `AM_ER_Attack_Air_Heavy_Plunge` / about -22.386 HP (`legacy:76,121`, `data:75,120`). Those are not default-wired PIE or packaged proof. `BACKUP_NAMING.txt` says `run5_probe_*` are older backups.
- C22: `Scripts/Editor/pie_er_default_wiring_hits.py` retains the bounded C-992 four-case input setup and two-route runner protocol but removes both runtime montage assignments. It logs all four `RPGDodgeTiming` defaults, each observed montage and the boss HP before/after. Its `RESULT` requires all four ground/air clip names and HP deltas within 1 HP of the C-1004 r5 control; missing montage or health fails.
- C23: focused fake-Unreal test checks accepted air samples and rejects wrong clip, zero damage and missing health (1/1). Python compile and two-route runner dry run pass. The dry run uses `-nosound` and does not run UE.
- C24: KI-193 stays OPEN. The approved reel, Source defaults, native PackWiring and earlier runtime-assigned r5 HP evidence are separate from default-wired PIE and cooked/package runtime. `CONTROLS_STATUS.md` retains this distinction.
- C25: Lead command follows. This probe covers ground R1/R2 and air R1/R2; backstep, guard counter, owner visual, cooked references and package smoke have other gates.

```powershell
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_er_default_wiring_hits.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_AM_C21_C25_DEFAULT
```

Acceptance for this slice: both route logs show four `CHECK ... pass=True` lines and `RESULT pass=True checks=4/4`, with exact default field readback and no Python error. Lead should inspect raw damage and montage records before updating KI-193. Codex did not run Editor, PIE, build or package.

# C-1042 deterministic real A4 guard-counter probe

Status: Codex authored and checked offline; Lead PIE is pending. KI-198 remains open.

`Scripts/Editor/pie_er_a4_guard_counter.py` uses the C-1035 parry probe's held boss and frontal 250 cm A4 blade lane. It draws the player's weapon first, loads the pack `IA_Block`, injects it every frame before and during the forced A4, and polls `RPGDodgeTiming.IsGuardCounterArmed`. It does not call the synthetic arm API or assign a runtime montage. When a real guard arms the window, it stops injecting block on the next frame, taps real R2 for 0.12 game seconds, samples the player montage through 2.5 game seconds, and compares boss HP before/after. The result requires the real arm, observed `AM_ER_Attack_GuardCounter`, and a measurable HP decrease. A no-arm run logs A4 position, sweep count, boss montage and guard state and fails without sending R2.

This isolates a deterministic A4 swing from the open-ended AI guard probe, but it still needs Lead runtime evidence. The Lead should check the native `successful guarded contact armed guard counter window` and `guard counter accepted after successful block` log lines alongside the probe's arm/montage/HP results. A passed offline test or a synthetic arm does not close KI-198.

```powershell
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_er_a4_guard_counter.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1042_A4_GUARD
```

Offline validation: focused evidence gate test passed 1/1; Python compile and two-route RunLeadPie dry run passed with `-nosound`. Codex did not run Editor, PIE, build or package. Claude also has the earlier `pie_camera_melee_occlusion.py` run sheet in `AM_C01_C05_CAMERA_DIAGNOSTIC.md`; its live 105/200/300 cm trace remains pending.

# C-1045 guard-counter reach probe hotfix

Lead accepted X-1473 and built BUILD-259 green 485/485. Both-route live A4 probe observed a real `Blocked` contact at full player HP, `REAL_GUARD_ARMED`, R2 within 0.03 game seconds, strong count +1, and `AM_ER_Attack_GuardCounter` playing. The boss stayed 2000 HP: the player started 250 cm away while the counter clip reaches about 130 cm. The guard-to-counter chain is live proven; the damaging counter remains unproven (KI-198).

`pie_er_a4_guard_counter.py` now places the player 140 cm from the boss before forcing A4. This is inside the authored A4 60–380 cm sweep band and within the clip's observed reach envelope. The probe logs actual actor distance at A4 start and R2 press, plus `hand_r`-to-boss distance and boss HP each tick while the counter montage plays. It retains the real IA_Block contact, no synthetic arm, no montage assignment, and the strict boss HP decrease gate. If the closer A4 does not land, the no-arm result remains an explicit failure rather than a false counter pass.

Offline Python syntax and focused guard test pass 1/1; two-route `RunLeadPie.ps1 -DryRun` shows `-nosound`, route selection and summary marker. No Editor/build/PIE by Codex for this probe change. Lead rerun:

```powershell
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_er_a4_guard_counter.py -Routes @('legacy','data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_C1045_A4_GUARD_REACH
```

Require blocked A4, real arm, accepted R2, `AM_ER_Attack_GuardCounter`, `StrongMeleeAttackData`, and boss HP decrease on each route. If the montage plays but HP stays flat, inspect `COUNTER_REACH` against the collision notify window and trace, rather than closing KI-198.

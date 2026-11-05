# P11–P12 A5 parity expected sheet

Status: commands and expected comparisons prepared; no P11/P12 live receipts exist yet.

All arms use the same build, content revision, input/settings identity, startup map `L_SevarogArena`, and distinct run IDs. `Scripts/RunA5ParityPair.ps1` starts one fresh windowed editor process per arm, runs the `RunDrivers.ps1` session preconditions, logs a runtime snapshot during PIE, checks the driver's registered minimum/terminal result, then quits. Run the legacy arm first. The wrapper refuses an existing evidence root.

## P11: P04 dormant-wake and P05 damage-path pairs

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityPair.ps1 -Driver pie_dormant_wake -OutRoot Saved/A5Parity/P11_dormant_wake
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityPair.ps1 -Driver pie_damage_path -OutRoot Saved/A5Parity/P11_damage_path
```

Expected equalities:

- Dormant wake: stage and montage outcomes, wake completion/cancellation, close-start veto, death state, all driver checks and terminal counts.
- Damage path: accepted/rejected damage outcomes, health changes, audit order, duplicate/stale/dead/lethal behavior, all driver checks and terminal counts.

Expected route differences: `selection.selected`, selected definition/manifest/slots, activation/binding diagnostics, participant generation, and component census/provenance. Stable boss/player role, class, and actor identity must match.

## P12: P06 death-reset, P07 telegraph, P08 boss-HUD pairs

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityPair.ps1 -Driver pie_player_death_reset -OutRoot Saved/A5Parity/P12_death_reset
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityPair.ps1 -Driver pie_telegraph -OutRoot Saved/A5Parity/P12_telegraph
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunA5ParityPair.ps1 -Driver pie_boss_hud -OutRoot Saved/A5Parity/P12_boss_hud
```

Expected equalities: respawn/reset/rebind and terminal state; telegraph phase/rate and attack cancellation; player-visible boss HUD state transitions and terminal result. Route selection, activation/binding diagnostics, and component provenance may differ.

## Receipt finalization

After each process exits and `editor_raw.log` is closed, prepare an identity JSON with the actual map/build/content/settings/seed/driver/driver-args/input values. `identity.driver` must match the selected script name. Use a unique run ID and new output path for each arm:

```powershell
python -I Scripts/Tools/write_a4_parity_receipt.py --log <arm>\editor_raw.log --identity <arm>\identity.json --run-id <unique-id> --out <arm>\receipt.json
python -I Scripts/Tools/compare_encounter_parity.py <legacy-receipt.json> <selected-receipt.json> --verify-source-logs --report-json <new-report.json>
```

PASS means all v2 identity, final marker, terminal and observed assertion outcomes match. FAIL is a real parity mismatch; INCONCLUSIVE means evidence is incomplete or invalid. Do not normalize away a mismatch. Preserve both raw logs, receipts, and comparator report.

## Current dependency

`WAITING ON LEAD: P10/P11/P12 fresh-process parity runs, finalized receipts, and comparator results.`

P13 cannot assign causes before the actual mismatches exist. P14 has no demonstrated production defect to fix. P15 is drafted separately as an explicitly provisional A7 decision summary.

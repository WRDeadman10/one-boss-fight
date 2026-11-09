# AY-C11–C15 driver preparation status

Claude C-1166 assigned C11–C15. Claude C-1170 accepted C12 and C14, resolved C13 as N/A, and ordered C12 rerun before Video 3. C-1171's first C12 PIE attempt was a setup failure (respawn/repossess not observed), not a parry carryover result. Codex's follow-up remains offline and does not include PIE.

| Task | Result | Lead state |
|---|---|---|
| AY-C11 Mid01 distance | Targeted dodge probe now begins at 120 cm and holds the existing 115–125 cm parry-close band. Existing generic dodge mode remains separate. Contract/unittest passed 42/42. | READY X-1667; Lead may run before C12. |
| AY-C12 parry lifecycle | First scenario opens a real old-pawn window, requests death, reports health/class and possession each five seconds, waits up to 45 seconds for a different expected-class pawn to be possessed, then checks fresh window/tag/counters/cooldown. Offline contracts 3/3. | Hotfix READY for Lead rerun; C-1171's earlier 0/1 was a setup failure only. |
| AY-C13 stagger recovery | `RPGCombatDebug` component hook targets pack posture, not KI-177's framework-owned posture/recovery scalars. C-1170 confirms the F5 framework-boss PIE fixture is unavailable in `L_SevarogArena`. | N/A per C-1170; no invalid pack-only KI-177 test. |
| AY-C14 owner Video 3 | Prepared 150-second normal full-fight run with all action types, C-1132 montage-position parry schedule, Tier 2 enabled and unique output paths. | READY as a capture plan; no run or visual claim. |
| AY-C15 receipts/contracts | C13 is closed N/A; refreshed C12 wait/diagnostic contract and C12/C14 receipts. `test_pie_ay_lead_drivers`: 3/3; py_compile and scoped diff check pass. | Batch receipt ready for Lead's ordered C12 rerun, then C14 video run. |

Reports: `AY_C11_MID01_DODGE_RANGE.md`, `AY_C12_PARRY_RESPAWN_PROBE.md`, `AY_C13_POSTURE_DEBUG_SCOPE.md`, and `AY_C14_OWNER_VIDEO3_PREP.md`. C13 is resolved N/A; Lead's next order is C12 rerun, then C14 video 3. This batch receipt records preparation only, not successful PIE/capture evidence.

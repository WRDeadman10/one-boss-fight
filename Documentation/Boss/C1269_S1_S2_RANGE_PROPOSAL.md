# C-1269 X04: provisional S1/S2 range proposal

Date: 2026-11-10. This is a data recommendation only; no card asset or source range was changed.

## Evidence

- F5 source card `Move_Sevarog_SwingMedium_F5` currently proposes `MinRangeCm=90`, `MaxRangeCm=180`, active window `0.1917–0.2667 s` (`Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json:56–76`). The C1247 draft uses that analogue for S1/S2.
- In the Lead live run at 140 cm, isolated S1 and S2 each finished with zero card hits (`Docs/BossCombatReview/Execution/Claude/P_C1265_SEVAROGLIVE4/data.log:2032,2084`). A separate S4→S5 combo hit for 25 damage at 120 cm (`data.log:2319`); that is positive S1 evidence in a combo context, not an isolated S1/S2 test.
- The corrected C-1269 PIE trace at 140 cm spans both clips. For S1 its sampled active-window frame at 0.21140 s puts `root_weapon_end_r` 106.114 cm from the player capsule surface (`C1269_X03_TRACE/pie_clip_trace.log:1567`); S2 samples 0.20635 and 0.22903 s inside the current active window, with closest endpoint 45.422 cm and closest `weapon_r` 37.022 cm (`:1713,1717`). Both exceed the move's 15 cm trace radius. The trace supports the 140 cm miss but cannot establish an exact hit threshold or prove that changing range alone fixes S2.

## Recommendation and punish math

Use **90–120 cm as a provisional shared S1/S2 band**, retaining the current `0.1917–0.2667 s` active window pending an isolated S2 hit check at 120 cm. The 120 cm upper bound is the only available positive S1 gameplay point; 140 cm is a repeated miss. S2 remains unconfirmed at 120 cm, so treat the shared value as a test candidate, not an accepted final value. Do not raise the range based on the endpoint geometry alone.

The live C++ profile bridge baseline at `MaxRangeCm=180` reports recovery `0.703333 s`, light startup `0.350337 s`, heavy startup `0.502704 s`, travel `0.050000 s`, light margin `0.302996 s`, heavy margin `0.150629 s`, required light margin `0.300000 s`, and `heavyFinisher=0` (`C1269_X03_TRACE/pie_clip_trace.log:1422–1423`). Applying the same production `RPGBossPunish::TravelSeconds` / `MarginSeconds` equations (`Source/OneBossFight/Player/RPGBossPunishRules.h:24–35`) to the proposed 120 cm ceiling gives travel `max(0,120−150)/600=0`, light margin `0.703333−0.350337=0.352996 s` (0.052996 s over the required margin), and heavy margin `0.703333−0.502704=0.200629 s`. Heavy margin is not a gate here because both cards report `heavyFinisher=0`.

**Disposition:** X04 proposal is ready for Lead decision. X05 is blocked on that decision; no card was authored or saved.

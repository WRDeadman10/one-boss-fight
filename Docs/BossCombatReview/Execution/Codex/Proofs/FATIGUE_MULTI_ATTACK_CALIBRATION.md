# Fatigue multi-attack calibration plan

Static timing review of `B_FATIGUE/pie_run2_six_shifts/editor_raw.log`; no Unreal execution. Attack start is measured from the first `playback_start` timestamp, and active-window timing comes from the logged Open/Close events. Shifts use game-clock seconds since the first attack (`rpg.BossProofTargetShift`).

| Attack | Card; start offset | Active window (local) | Approximate global active window | Shift schedule and feasibility |
|---|---:|---:|---:|---|
| 1 | `SwingSlow`; 0.000 s (`:1586`) | 0.3500–0.4917 (`:1627, :1658`) | 0.3500–0.4917 | Move away at 0.25 and return at 0.55: 0.100 s before open, 0.0583 s after close. Feasible, but return margin is about 3.5 frames at 60 Hz. |
| 2 | `AntiGreed_FastJab`; 1.681 s (`:1801`) | 0.2500–0.3083 (`:1832, :1843`) | 1.9310–1.9893 | Away at 1.74, return at 2.17: 0.191 s before open, 0.181 s after close. Feasible. |
| 3 | `SwingMedium`; 2.195 s (`:1879`) | 0.1917–0.2667 (`:1904, :1923`) | 2.3867–2.4617 | Away at 2.25, return at 3.25: 0.137 s before open, 0.788 s after close. Feasible, though the long displacement should be checked against the next selection's range. |
| 4 | `SwingSlow`; 3.388 s (`:2035`) | 0.3500–0.4917 (`:2082, :2132`) | 3.7380–3.8797 | Away at 3.58; scheduled return at 3.88 is only 0.0003 s after the computed close. This is not a robust margin; in the log the target-shift event occurs before the Close event (`:2100` before `:2132`). Move the return to at least 4.05 s (about 0.17 s after close) in the next calibration. |

The first four attacks are the chosen candidates because their starts and active windows are explicitly logged, and alternating ±300 cm target shifts can bracket the windows. A counted whiff must still be confirmed by absence of accepted, guarded, or parried `hit`/`CARD_HIT` outcomes for that instance; a sweep line alone does not establish a whiff. The observed run reports `fatigue whiffs=1,2,3` at `:1791, :1869, :2025`, with selected playback rates 1.00, 0.95, and 0.90 at `:1801, :1879, :2035`. A later contact reset appears at `:2269`; it is a control, not a fourth whiff.

For a clean rerun, retain the first three pairs, change only the fourth return from 3.88 to at least 4.05, and verify the target-shift event precedes each Open and follows each Close by a visible margin. Record the complete `hit`, `guard_state`, and `CARD_HIT` lines for each instance before accepting the consecutive-whiff count. The 6.5-second return pair in the current schedule is a separate range-recovery/control candidate and is not needed to establish the first three whiffs.

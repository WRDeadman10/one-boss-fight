# V-C085 — post-performance parity spot-check

**Status: Lead-run pending.** Run only after a performance setting is explicitly approved, applied, built and identified. Pair legacy and selected/data arms on the same binary, map, settings, resolution, driver and session; retain both raw logs, receipts, source hashes and comparator output. Do not run this sheet as evidence before the setting change.

| Driver | Regression protected | Minimum checks | Why included |
|---|---|---:|---|
| `pie_iframes` | Full-roll timing / invulnerability boundaries | 19 | Frame-sensitive dodge timing; uses fixed rate 2.0 and authored-window-derived bounds. |
| `pie_phase_reset` | Phase and reset lifecycle | 14 | Confirms reset/state recovery under changed frame pacing. |
| `pie_boss_death` | Death and terminal cleanup | 11 | Checks end-of-fight cleanup and state restoration. |
| `pie_authored_close_clips` | Authored telegraph and active-window timing | 14 | Catches animation/tracker timing drift. |
| `pie_legend` | Hit-stop, slow motion, restoration and L8 | 25 | Checks time-dilation lifecycle and the typed perfect-parry duration. |

Use the current registered A5 pair wrapper so receipt paths, driver arguments, selection identity, logs and hashes are recorded consistently. Run refusal/recovery tests separately if the performance change touches packaging or selection; they are not substituted for these five parity pairs. Acceptance requires both arms to meet each driver's minimum and the source-verified comparator to produce no unexplained mismatch. A passing spot-check does not itself establish the absolute frame-rate target.

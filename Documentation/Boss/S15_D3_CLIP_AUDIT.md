# Queue S15 — D3 priority 2–5 clip audit

Date: 2026-11-05. This audit reviewed the canonical 3840×2160, 59.9401 fps WebM already registered by the D3 ledger. The companion MP4 is 29.97 fps and was not used for canonical frame IDs. The ledger's combat-zero convention is 105.0 s.

## Review and disposition

Priority 2 (`REF_DaggerFlurry_TapClose`) was already withdrawn because the earlier 116–118.8 s candidate did not establish clip identity. A focused review at 0.5 s intervals across 115–125 s confirms close multi-weapon combat, but does not isolate a dagger flurry or establish the requested trigger distance, active arc, or summon cue. Keep it withdrawn.

Priorities 3–5 were reviewed against the full-combat sparse survey and a focused 2 fps frame survey of 105.0–170.0 s. The phase-two survey recorded for S11 also did not yield a positively identified candidate for these rows. The review found no suitable sequence to label as:

| Priority | Reference | Disposition | Evidence limitation |
|---:|---|---|---|
| 3 | `REF_SpearCharge_Full` | Withdrawn; unmeasured | No distinct spear throw followed by a charge with defensible windup, contact, active, end, recovery, and recovery-end boundaries. The Gemini-described 129–135 s interval overlaps the already measured priority-9 mace clip and does not establish a spear charge. |
| 4 | `REF_HammerSpin_Finisher` | Withdrawn; unmeasured | No distinct hammer jump/spin finisher with an identifiable rotation, ground-slam, and recovery sequence. |
| 5 | `REF_TailSweep_RearCamp` | Withdrawn; unmeasured | No clear rear-camped tail-sweep instance that establishes the rear trigger, windup, and punish opportunity. |

The focused Phase 1 survey used 131 frames sampled at 2 fps from 105.0 through 170.0 s. It is a candidate-identification survey, not frame-accurate attack timing evidence. The earlier full-combat sparse survey and S11 phase-two review were also consulted. No W/C/A/E/R/RE times, frame IDs, confidence values, or derived gameplay claims were added. Priorities 2–5 retain null measurement fields; priorities 3–5 now have explicit withdrawal reasons in `Docs/BossCombatReview/Execution/Claude/D3/D3_MEASURED_LEDGER.json`.

This disposition means the available recording did not provide a defensible sample for these rows; it does not assert that the moves never occur. Re-open only with a suitable, clearly identified clip. No Unreal, build, package, commit, or push was performed.

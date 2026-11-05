# Queue Q21–Q25 — D3 measurement status

Date: 2026-11-05

## Q021 — source-template reconciliation

Read-only comparison of `Docs/BossCombatReview/Execution/Claude/D3/D3_MEASURED_LEDGER.json` against `Docs/BossCombatReview/Execution/Antigravity/Reviews/D2_MEASUREMENT_LEDGER.json` found 10 entries on each side. Priorities 1–10 have identical `ref_id` and `ref_to_original` values in identical order. No ledger fields were changed, so existing measurements were not overwritten.

| Priority | Reference ID | Current state from the existing measurement report |
|---:|---|---|
| 1 | `REF_CurvedSwordCombo_Chain1` | measured |
| 2 | `REF_DaggerFlurry_TapClose` | unmeasured; previous candidate withdrawn for uncertain clip identity |
| 3 | `REF_SpearCharge_Full` | unmeasured |
| 4 | `REF_HammerSpin_Finisher` | unmeasured |
| 5 | `REF_TailSweep_RearCamp` | unmeasured |
| 6 | `REF_HolySwordRain_Setup` | measured |
| 7 | `REF_BloodflameGrab_Skewer` | unmeasured |
| 8 | `REF_OmenCurseBurst_Phase2` | timing fields present; canonical frame evidence incomplete |
| 9 | `REF_MaceSlam_Sweep` | timing fields present; canonical frame evidence incomplete |
| 10 | `REF_GapPounce_Close` | timing fields present; canonical frame evidence incomplete |

Q021 is complete as a read-only reconciliation. The prior P36–P40 audit reports five measured rows overall, five null rows, and 30 missing canonical frame PNGs; this report does not promote incomplete timing rows to evidence-complete measurements.

## Q022–Q025 — priority clips 2–5

No new measurements are entered. A local-only balanced scene scan covered the 335.5 s source and selected 32 frames at 512 px; the frames were visually reviewed. A focused 115–125 s pass selected 20 frames at 0.5 s intervals. That interval shows close multi-weapon combat, but does not establish the prior candidate as the dagger-flurry clip. Keep the withdrawn 116–118.8 s measurement withdrawn. The sparse scan did not identify defensible priority-3/4/5 source windows either. No W/C/A/E/R/RE timing, identity, confidence, or gameplay claim was added. The reviewed frames remain disposable temp files and are not counted as accepted, labeled evidence.

## Evidence and boundary

Q021 used only the two JSON ledgers and P36–P40 status. Q022–Q025 used local video frames with transcription disabled; the footage was not uploaded. The `D3_MEASURED_LEDGER.json` was not edited. Q022–Q025 remain open pending correctly identified source intervals and retained/labeled frame evidence. No Unreal, asset write, test run, commit, or push was performed.

## Owner-provided Gemini summary cross-check (2026-11-05)

The owner supplied Gemini's broad fight summary after the original scan. It
describes a curved-sword/holy-dagger spinning sequence at 00:07–00:12 and a
dagger spread followed by a spear thrust at 00:24–00:30. Treat those as
candidate descriptions only: Gemini did not identify D3's W/C/A/E/R/RE
boundaries or provide retained milestone frames. Under the ledger's
`combat_zero_seconds = 105.0` assumption, the second interval maps to source
129–135 s. A focused local frame review of 132.8–135.2 s shows the bright mace
summon/swing already recorded for priority 9 (`REF_MaceSlam_Sweep`, W at
combat 28.395 s); it does not establish the separate priority-3
`REF_SpearCharge_Full` identity. The 00:07–00:12 description overlaps the
existing priority-1 measurement window (combat 7.441–8.325 s) and does not
isolate priority 2. Because the timebase and attack identities are not
resolved to labeled source frames, no ledger fields or confidence were
changed. Q022–Q025 stay unmeasured; Queue Q remains closed per C-851.

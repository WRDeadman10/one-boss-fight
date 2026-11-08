# AF-C01–C05 — Hotfix progress audit

Date: 2026-11-07. Static source, file and mailbox review. No asset edit, test, Editor, build, cook, package, PIE, or benchmark run by Codex.

## AF-C01 — post-C-992 asset return (partially verified; full criterion remains open)

The latest C-994 return supersedes the earlier failed export. The timestamped full text exports in `Docs/BossCombatReview/Execution/Claude/P_C992_AIRHITS/t3d_a598/` show the GuardCounter trace instance at `AM_ER_Attack_GuardCounter.t3d:28–29` and AirLight at `AM_ER_Attack_Air_Light.t3d:14–15` with empty instance property blocks, like the pack template instances at `Attack_PrimaryA_Montage.t3d:32–33` and `Attack_PrimaryB_Montage.t3d:32–33`; no `AttackData` override is serialized in either full file. The same directory contains no AirHeavyPlunge export, and the export script `export_montages_text_a598.py` does not include that asset in its list. The short excerpt in `C992_HOTFIX_EVIDENCE.txt` states AttackData is unset for AirHeavy but is not a full serialized export. Therefore GuardCounter/AirLight AttackData absence is supported, while the three-asset acceptance is incomplete pending full AirHeavy t3d evidence and property-parity review.

Lead's refreshed readback in `C992_HOTFIX_EVIDENCE.txt` confirms 0.100 s blend-in on all four ER montages; AirLight trace 0.200 + 0.133 s then MovementCancel 0.333 + 0.233 s; AirHeavy trace 0.367 + 0.166 s then MovementCancel 0.533 + 0.333 s; GuardCounter trace 0.168 + 0.089 s and MovementCancel start 0.351 s. These satisfy the listed timing/blend constraints. Backstep has blend-in only as assigned. The Lead asset-check script prints montage/readback metadata but does not inspect `AttackData` (`P_C985_ASSETCHECK/check_tier2_er_assets.py:17–19`), so its 5/5 readback cannot fill the missing AirHeavy property proof.

## AF-C02 — Lead hit-test rerun (complete; both ER attacks still fail)

The latest Lead logs now contain completed probes for both routes. Controls damage the held boss on both routes: R1 -15.99 HP and R2 -22.386 HP. Assigned ER AirLight and AirHeavy each deal 0 HP on both routes. Data route evidence is `probe_data.log:1432,1598,1646–1650,1651–1653`; legacy evidence is `probe_legacy.log:1435,1602,1650–1653,1655–1660`. Each log records setup at 900 cm and assigned ER montage names; each probe reaches `finished: all control samples recorded`. Runtime behavior therefore remains failed despite the improved saved-property evidence. The AirHeavy `StoredInputTags` empty-array warning appears during its attempt (legacy line 1656; data line 1653); this is a correlated warning, not established as the cause. The run does not log ER hit-intake attribution because no hit was recorded.

## AF-C03 — corrected timing logic (static review complete)

AA-A08 now gives AirLight trace 0.200–0.333 s and MovementCancel 0.333–0.567 s; AirHeavy trace 0.367–0.533 s and MovementCancel 0.533–0.867 s. C-994 approves 0.100 s blend-in across all four ER montages, so AirLight's hit window begins after blend-in. These are table constraints, not post-authoring saved values or runtime proof.

## AF-C04 — current evidence registry (refreshed to new failed readback)

AA-A08, GATE-07, KI-193, TEST_PLAN and DECISIONS must distinguish the 11:50 Lead values from the failed AttackData proof. Owner clip review, optional-field assignment, cook/package evidence and the parked Round 6 Phase 2 decision remain separate. The asset-check/t3d export establishes a saved-value mismatch only; it is not a live PIE result.

## AF-C05 — next-lane handoff

Queue AF has five unique IDs in one batch. AF-C01's fresh readback is reconciled and fails AttackData absence; AF-C02 is explicitly externally pending. Queue AG is staged as the next five-task lane; it preserves the two external dependencies and does not close release gates.

Current AF status: AF-C01 partially verified (AirHeavy raw t3d/property parity missing); AF-C02 complete with ER-air damage failure on both routes; AF-C03 static timing audit complete; AF-C04 evidence registry refreshed; AF-C05 next lane staged. Continue Queue AG and recheck new hotfix/runtime evidence on each mailbox cycle.

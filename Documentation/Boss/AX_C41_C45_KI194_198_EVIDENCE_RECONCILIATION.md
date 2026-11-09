# Queue AX-C41–C45 — KI-194–198 evidence reconciliation

Date: 2026-11-09. Offline source/document review only. No tests, Unreal, build, PIE, cook, package, commit, or push were performed.

## AX-C41 — KI-194 post-air restoration scope

`Documentation/Boss/AB_C41_C45_MILESTONE_AND_HANDOFF.md` records C-978 as the Lead receipt for AirLight/AirHeavy followed by grounded R1/R2 on the tested routes; `Documentation/Boss/AD_C06_C10_PLAYER_LIFECYCLE_AND_RERUN_AUDIT.md:26-30` narrows the result to those completed post-air sequences. It explicitly excludes death, reset during montage, pawn replacement, and general teardown. `Documentation/KNOWN_ISSUES.md:356` correctly resolves only the tested C-978 routes and leaves the post-wiring/default configuration under KI-193. No broader lifecycle or default-wiring claim is supported by that receipt.

## AX-C42 — KI-195 subprocess boundedness

`Documentation/Boss/AD_C16_C20_SUBPROCESS_TIMEOUT_HARDENING.md` reports seven calls moved to the timeout helper, three remaining direct calls bounded at 45/30/10 seconds, a separate 20-second suite wrapper, and 35 focused tests passed. Source confirms the helper requires `timeout` and converts `TimeoutExpired` into a diagnostic assertion (`Scripts/Tools/process_test_support.py:8-19`); the remaining bounded calls are at `test_gate_script.py:64-66`, `test_queue_w_workflows.py:44-47`, and `test_round6_phase2_intake.py:102-103`. `KNOWN_ISSUES.md:357` accurately marks this offline boundedness issue closed. It does not claim a full-suite run or general process-tree termination guarantee.

## AX-C43 — KI-196 DATA-default PIE and package boundary

`Documentation/Boss/AM_C26_C30_DODGE_GATE.md` supersedes its earlier pending wording with the C-1076 disposition: the two no-runtime-assignment nominal arms were DATA-default per C-1099, and prove the tested moving-dodge cases only. `KNOWN_ISSUES.md:358` preserves that scope and leaves package proof open; no legacy parity or packaged behavior is inferred. The project’s C-1104 constraint also rules out parity-only true-legacy reruns.

## AX-C44 — KI-197 source fix versus Lead verification; stale TEST_PLAN claims

`Scripts/Package.ps1:6-8,34-56` now selects separate Development and Shipping defaults and rejects a default-root collision. `Scripts/MakeBenchKit.ps1:16-21` uses those project roots and fails when the default Shipping stage is absent. `Documentation/Boss/AR_C16_C20_KI197_STAGE_ROOT_FIX.md:20-38` describes the offline contracts and keeps same-build dual-package/identity verification with Lead; source correction does not establish package contents or no-contamination.

Two TEST_PLAN statements are stale against this later source change and accepted handoff: `Documentation/TEST_PLAN.md:118` says Package.ps1 still uses one root, and `:140` says package/kit defaults remain ambiguous/shared. Both should be corrected under the TEST_PLAN authorization gate; this audit does not edit TEST_PLAN. The open KI-197 package/identity gate remains valid.

## AX-C45 — KI-198 DATA-default counter proof; stale pending rows

The accepted receipt at `Documentation/TEST_PLAN.md:1932` records C-1047’s DATA-default blocked A4 → real arm → R2 → GuardCounter montage → Strong damage, with a -22.386 HP boss delta; `Documentation/KNOWN_ISSUES.md:360` correctly limits the proof to the tested DATA-default PIE case and keeps packaged proof open. This supports neither legacy parity nor package acceptance.

Older unchecked rows are stale if read as current status: `Documentation/TEST_PLAN.md:120` says KI-198 still awaits Lead PIE, contradicting the later accepted C-1047 row; `:124` still lists KI-198 real-contact counter-hit proof as outstanding. The full-fight owner video review in that same row remains a separate open gate. This audit leaves the historical rows untouched because their owning TEST_PLAN gate requires renewed Lead authorization before edits.

## Validation and handoff

The five issue boundaries above were checked against the current KNOWN_ISSUES entries, queue handoffs, recorded receipts, and the package-stage source. Found four stale TEST_PLAN claims: two for KI-197 source defaults and two for KI-198 PIE status. No runtime/package evidence was created. Reported for Lead review; TEST_PLAN edits remain gated.

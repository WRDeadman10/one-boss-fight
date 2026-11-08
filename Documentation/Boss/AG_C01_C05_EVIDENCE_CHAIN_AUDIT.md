# Queue AG-C01–C05 — evidence chain audit

Date: 2026-11-07. Static mailbox/file review only. Codex did not author assets or run Unreal, build, cook, package, PIE, or benchmarks.

## AG-C01 — saved-property return

Current artifacts were refreshed after A-598. The Lead readback confirms blend-in 0.10 s for GuardCounter, Backstep, AirLight, AirHeavyPlunge; AirLight trace/cancel 0.200 + 0.133 / 0.333 + 0.233 s; AirHeavy trace/cancel 0.367 + 0.166 / 0.533 + 0.333 s; GuardCounter trace at 0.168 + 0.089 s with cancel starting 0.351 s. These satisfy C-994 timing/blend constraints.

Full t3d files for GuardCounter and AirLight in `Docs/BossCombatReview/Execution/Claude/P_C992_AIRHITS/t3d_a598/` contain one CollisionTrace instance each, with empty instance property blocks and no serialized AttackData override; the two pack control trace blocks are also empty. However, the export script's asset list omits AirHeavyPlunge, and the folder has no AirHeavy t3d. The short evidence excerpt asserts AttackData unset there but does not provide its full property block. Thus the three-montage property gate is only partially evidenced. The prior C992_HOTFIX_EVIDENCE export asserting AttackData present is stale and superseded for GuardCounter/AirLight; do not apply it to the newer t3d_a598 files.

## AG-C02 — PIE result

The latest P_C992_AIRHITS reruns are complete for both routes. Data and legacy controls damage the held boss: R1 -15.99 HP, R2 -22.386 HP. Assigned ER AirLight and AirHeavy each deal 0 HP on both routes (`probe_data.log` and `probe_legacy.log`, case/hit entries cited in AF report). This is a current runtime failure, not a pending test. AirHeavy attempts also emit `Attempted to swap elements in empty array StoredInputTags!`; correlation is observed but causation is unknown. The logs don't attribute ER hit data because neither attack produced a hit.

## AG-C03 — evidence-chain consistency

The refreshed Lead asset readback and t3d exports supersede the earlier failed C992 export for GuardCounter/AirLight; the full AirHeavy serialized proof is missing. The 5/5 check script validates montage/notifies but does not inspect AttackData. The new PIE reruns postdate the re-authoring and still show 0 air damage on both routes, while controls work. Keep saved-property status partial and runtime status failed. Do not conflate a Lead readback pass with runtime hit success.

## AG-C04 — registry update

GATE-07, KI-193, TEST_PLAN, DECISIONS, PROJECT_STATE and TASKS record the partial saved-property evidence, failed two-route hit test, and separate owner/cook/package gates.

## AG-C05 — lane close and next lane

Five task IDs are unique in Queue AG. AG-C01 is partially evidenced (no AirHeavy t3d); AG-C02 is complete with a two-route runtime failure; AG-C03 and AG-C04 are complete on current evidence. AG-C05 closes the audit lane with the missing AirHeavy export and zero-damage fix/rerun recorded as external dependencies. Queue AH is staged for independent source-level diagnosis. No release gate is inferred from an absent artifact.

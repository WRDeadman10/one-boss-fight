# AR-C46–C50 — offline closeout and Lead/owner handoff

## Current disposition by issue

| Gate | Current status | Evidence / next action |
|---|---|---|
| KI-190 stamina policy | OPEN; no values tuned; owner decision pending. | Freeze v1.2 §20.1's 35 value is specifically JumpHeavy. The audited table mixes `-1`/pack-base and 35 rows; test-override evidence is separate from real Strength-loadout cases. Owner must choose the category policy in `AR_C26_C30_KI190_STAMINA_SCOPE.md`; Lead then collects real-loadout rows without overrides. |
| KI-192 charge boundary | CLOSED for PIE by Lead C-1100; package open. | Valid BUILD-269 set is DATA x10 and true LEGACY x5 (explicit startup flag and same-run route witness); both show a tick-quantised boundary near 0.36 s. Pre-fix sheathed trials remain excluded. Threshold unchanged; observations remain game-tick-bounded, not device latency. See `AR_C31_C35_KI192_RERUN.md`. |
| KI-193 ER/Tier 2 cook/package | PARTIAL; checker and owner-approved defaults exist, but current same-build cook/package/runtime proof is open. | For Development and Shipping separately, Lead returns source and normalized manifests, explicit build/config identity, eight-package checker JSON, distinct stage identity/stamps, executable hash, and packaged route smoke/capture as listed in `AR_C21_C25_KI193_COOK_GATE.md`. |
| KI-197 stage roots | OPEN pending Lead dual-package verification; offline path fix accepted in C-1096. | Lead packages Development to `Saved/StagedBuilds` and Shipping to `Saved/StagedBuilds_Shipping`; returns both Build IDs, stage stamps/manifests, executables/hashes, and bench-kit identity checks. Codex performed no package run or stage cleanup. |
| KI-199 first dodge | Workaround proven in the scoped C-1067 both-route standing/moving PIE cases; root cause unisolated and package proof open. | Keep InputBuffer/Enhanced Input/context attribution open. The C36–C40 snapshot helper and contract are offline only. A new Lead run must provide BUILD/source identity, both routes, standing/moving first press plus same-process repeats, raw logs/hashes, and route/case labels before interpreting its observations. |
| KI-037 / KI-066 camera | OPEN; owner choice and broader case/package coverage pending. | The current C-1088 brief requests B, C, or B+C; C-1090 remains one bounded B+C attack case. No option or default is selected. Do not change `RPGCameraRig` or config without a recorded owner decision. |

## Five-batch record

- **AR-C01–C05:** static KI-192 callback/threshold audit; Antigravity A-649 accepted the audit. C-1099 corrects C-971's nominal legacy arm to DATA-default, and C-1100 closes the tick-quantised boundary for PIE with true legacy evidence. No tuning.
- **AR-C06–C10:** fail-closed receipt parser and Lead runner spec; route identity comes from the same-run activation witness, with probe-label disagreement rejected and filtered input requiring an explicit witness file. C-971 historical build identity remains unknown.
- **AR-C11–C15:** static KI-199 input/retry path audit; no root cause assigned.
- **AR-C16–C20:** Development/Shipping stage-root separation and aligned consumers; C-1096 accepted offline contracts; Lead package remains parked.
- **AR-C21–C25:** read-only eight-package cook-manifest checker; C-1097 accepted; no actual cook/package claim.
- **AR-C26–C30:** KI-190 policy/scope audit; C-1097 accepted as analysis; owner decision pending, no tuning.
- **AR-C31–C35:** repeat-run stamp/aggregate wrapper, schedule and stop/return contract; C-1098 contracts pass. C-1100 reports DATA x10 and true LEGACY x5; KI-192 is closed for PIE and package remains open. Codex did not process raw runs.
- **AR-C36–C40:** first-dodge post-press observation snapshot, four AST contracts and Lead matrix; 4/4. The containing PIE driver remains state-changing; no Codex runtime run or root-cause claim.
- **AR-C41–C45:** no-write camera-default plan and stdout-only planner; 3/3. C-1088 B/C/B+C only; nonempty reference is not authenticated. No camera Source/config change.

## Closeout verification

The AR queue has ten five-task batches, IDs AR-C01 through AR-C50 in order, unique IDs, and a nonempty task/acceptance and external-gate column for each row. C-1101 hotfix tests prove C-971 nominal legacy route mismatch is rejected while true-legacy and DATA activation witnesses are accepted. Historical suite results 42/42 and 46/46 predate this route hotfix; the current route/runner/repeat-receipt focused set includes 32 tests, with stage-root checks making the combined AS validation set 44. Claude C-1103 accepted X-1556/X-1557 after independently checking all three retained route fixtures and the filtered-input refusal; Claude reports that Antigravity regenerated all 10 P_C1095 receipts from full logs with activation-witnessed routes. Codex did not inspect or edit those raw logs. No Codex Unreal/Editor/PIE/build/cook/package/commit/push was performed.

## Latest mailbox review and file boundary

C-1096 accepted AR-C16–C20 offline work and kept package execution with the bench. C-1097 accepted AR-C21–C25 and the KI-190 analysis; it says the KI-192 rerun remains in progress and instructs Codex to ask before further `TEST_PLAN.md` edits. Codex notified Claude in X-1546 that two AR-C36/C41 offline checklist entries had already been added before seeing that instruction and will make no additional edits to `TEST_PLAN.md` this sprint. X-1544 and X-1545 report C31–C40 completion; X-1547 reports C41–C45 completion. These latest batches have not yet received a Claude verdict; no rejection is known.

## C-1098 hotfix follow-through

Claude accepted X-1544/X-1545 offline and reported the KI-192 probe fixes and invalid pre-fix trials. Codex added offline contracts for `.length()`, the three-attempt draw-ready/no-montage warmup and canonical summary marker; the receipt wrapper now rejects missing draw readiness or completion. The AR-C35 handoff notes that the watcher must match `[ERControlLatency] SUMMARY finished:`. The full focused AR suite now passes 46/46 (the earlier 42/42 was the C46–C50 closeout baseline). The prior sheathed/no-montage trials remain invalid and unprocessed; Claude's corrected 5x2 run is in progress. No raw run evidence was read, and no TEST_PLAN, Unreal, PIE, build, cook, package, commit or push action was taken for this follow-through.

## C-1100 KI-192 disposition

Lead reports 15 valid BUILD-269 fresh-process receipts. DATA x10: Ability_E on tap and 0.34/0.35 s in 10/10; 0.36 s Ability_E 9/10 and ChargedAttack 1/10; 0.70 s ChargedAttack 10/10. Confirmed LEGACY x5 (`RPG_LEGACY_STARTUP=1`, same-run `route=legacy`): Ability_E on tap and 0.34/0.35 s in 5/5; 0.36 s ChargedAttack 3/5; 0.70 s ChargedAttack 5/5. Lead closes KI-192 for PIE: the boundary is tick-quantised near 0.36 s on both routes; the small rate difference is descriptive, not actionable. No threshold change; package remains open. Codex did not read or process run artifacts.

## C-1099 route-provenance correction

The nominal post-retirement legacy arms that only unset `H019_ENCOUNTER_DEFINITION` are DATA-default, not parity evidence. `C1099_ROUTE_PROVENANCE_CORRECTION.md` inventories affected Lead claims. The generic PIE runner now sets the legacy startup flag and fails closed unless the raw log confirms the requested activation route. No run artifacts were changed.

## Next authorized actions

1. Lead reviews X-1555 / the C-1101 route-witness parser hotfix; no commit or raw-log edit by Codex.
2. Lead supplies the outstanding Development/Shipping package, cook manifest, stage identity, and packaged route receipts for KI-193/KI-197.
3. Owner records stamina policy and camera option; no implementation/default change is authorized before those decisions. QUEUE_AS outlines the next bounded offline work through AS-C45.
4. Lead supplies any requested KI-199 build/PIE/package evidence; root-cause attribution remains a separate reviewed task.

Claude and the owner may choose the sequencing of those external gates. This offline queue closeout does not mark them complete.

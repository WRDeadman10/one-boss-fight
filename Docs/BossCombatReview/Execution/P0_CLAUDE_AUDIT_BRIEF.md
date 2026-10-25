# CI-P0-C-01 — Claude technical/runtime baseline

FROM / TO: Codex technical lead -> Claude, accountable technical investigator.
STATUS: IN PROGRESS after C-85 acknowledgment and exclusive output claim. Claude must verify bridge/PIE idle and binary provenance before live diagnostics. Read-only P0 only.

## Objective and references

Establish CURRENT active execution, not asset presence. Reconcile prior audit U01–U12 and G01–G08 with all 83 BOSS-* requirements and Master Freeze sections 10–22, 30–36. Existing architecture, matrix and exact package list: [prior audit](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/BOSS_AUDIT_SUMMARY.md), [U register](C:/UnrealProject/OneBossFight/Docs/BossCombatReview/ExistingBossAudit/11_UNVERIFIED_ASSETS_AND_TESTS.md).

Prior source fingerprints remain equal for tracker, wave, heal punish and resolver. This supports reuse of source observations, not current compiled/runtime equivalence. Saved GA_EnemyMeleeAttack T3D is historical; inspect current graphs and runtime instances.

## Allowed scope and claims

Read current Source, Config, existing test scripts and live map/controller/BT/BB/ability/AnimBP/montage/notify/trace/damage/data assets identified by U01–U09. Use legitimate read-only editor queries/graph exports and existing diagnostic hooks. Claim only NEW Docs/BossCombatReview/Execution/Claude/P0_REPORT.md and Evidence/ before writing. New standalone read-only export/probe scripts may be placed there if existing tools cannot answer; include their source for review.

Claude retains editor/build ownership. Coordinate around existing performance work. Existing diagnostic PIE runs and captures are permitted after acknowledgment of this bounded task; do not assume editor/binary matches source. If a fresh baseline build is needed, disclose source/dirty-tree fingerprint and exact standard build/test plan first; no implementation edits or asset authoring. Close editor before approved build and relaunch -nosound. Do not launch expensive full regression by default.

## Required investigation

1. **Runtime route:** placed L_SevarogArena boss EnemyInfoRef override, actual pawn/controller, mesh/AnimBP, attached native components and live ability objects. Distinguish pack custom Blueprint abilities from GAS and retired C++/StateTree.
2. **Complete attack inventory:** all natural damaging abilities, not only tracker A1–A6. Include MidRange/Sprint/Retaliation and their actual resolved assets or prove inactive. For each: selector/tag/eligibility, phase, cooldown start/reset, current animation/fallback, geometry, defense/outcome owner, test-only vs natural activation.
3. **Decision graph:** BT root-to-task connections, decorators/abort modes, services and frequency, BB key reads/writes, target validity/LOS/memory, waits/move goals, random/history/weights and empty-pool behavior. Show actual CanActivate -> commit -> play -> follow-up -> end path, with graph/node/pin evidence and current defaults.
4. **Timing/motion matrix:** accepted request, identity creation, montage section/time origin, notify intervals, commitment/yaw lock, translation owner, release/contact, follow-up gates, earliest legal next attack, blending and recovery. Record montage-local and real time separately, phase/rate/test-switch values, actual runtime replacement vs fallback.
5. **Production damage:** trace source sockets/query/tick order/hitset, central A2/A6 hit, A4/A5/wave outcomes, alive/generation/iframe/block/parry/guard/posture/HP/death order. Observer sweeps do not prove production algorithm. Attribute direct and wave contacts explicitly in evidence; HP deltas alone cannot establish common identity.
6. **Cross-state lifecycle:** stagger/phase/riposte/death/reset and lingering projectile/window cleanup; deterministic priority; phase buffs once/reversed; ordinary tracker recovery enforcement versus pack owner.
7. **Candidate verification:** G01 shipping wave cue, G02 narrow-window/ring crossing, G03 fallback timing, G04 split outcomes, G05 late identity/default recovery, G06 A4 natural integration. Classify reproduced, source-confirmed mechanism, contradicted, configuration-only, design proposal or unverified. No silent fix.
8. **Regression baseline:** relevant current existing automation/PIE evidence with exact coverage/limitations, natural fight sample, current known flakes, wake bypass, human/performance gaps. Preserve KI-106 as setup discrepancy unless new evidence establishes product failure.

## Evidence contract

Per observation: evidence ID; build/source/asset fingerprint; date/config; exact package and graph/function/node/pin; setup/coordinates/target state/rate/FPS; commands/probe revision; raw export/log/capture path and bounded line/time range; expected/actual; PASS/FAIL/NOT RUN; limitations and linked requirement/audit ID.

Record runtime cvars including rpg.WakeClip, rpg.CloseTelegraph, build choice and fixed-FPS/time-dilation settings. Older RunDrivers disables wake; Shipping does not. Preserve dirty state and state whether probe changes only temporary PIE actors. Do not equate filename or blueprint load success with graph inspection.

## Minimal test plan

Inspect graphs first; then choose focused existing drivers that answer remaining questions: close attacks/reach, A4, A5, leap/wave, trace/damage/iframes, phase/reset/riposte/transition. Read their current assertions; do not weaken them or call forced moves natural selection. Log counts of eligible opportunities and actual selections. Lack of selection in a short random run does not prove impossibility.

For timing risks use supported rates plus bounded hitch scenarios if existing tooling supports them. If instrumentation would require gameplay code or asset change, report blocker with minimal proposal instead. No speculative hook implementation in P0. Full soak/build fights only when existing evidence is stale for the relevant claim; avoid indiscriminate reruns.

## Deliverables and acceptance

Report must contain: architecture map; exhaustive live attack inventory; decision graph; timing/motion/damage matrix; confirmed-defect list with reproduction or source-proof scope; current-vs-approved-target comparison; baseline regression evidence; minimal prioritized P1–P8 proposals.

Every claimed active edge has current graph/runtime evidence; every uninspected asset remains UNVERIFIED with exact path and reason. Include every 83 requirement ID as evidenced or unresolved, with links rather than duplicating the whole reference. Separate working behavior, partial behavior, confirmed defect, unknown, design improvement and optional addition.

## Restrictions and review

No Source/Config/existing script/Blueprint/Data Asset/animation/level edits, import/save/compile of assets, pack modifications, tuning, deletion, commit or push. No new gameplay framework. No changes to reference/audit or Codex control files. Preserve 60% phase, 3.2 m roll, current HP/bleed/riposte, approved reskin and owner-kept iframe windows. AG's visual outputs belong to AG.

Report location: Docs/BossCombatReview/Execution/Claude/P0_REPORT.md; Evidence/ for raw exports/probes/log excerpts with original run provenance.
NEXT ACTION: acknowledge X-91/X-92 and claim output paths; confirm editor occupancy and conflicts. When ready, post C-n review-requested with exact artifacts, tests actually run, failures and unresolveds. Codex independently reviews. This task cannot approve P1.


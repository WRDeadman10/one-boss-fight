# D04 — Independent review of Claude P0 evidence E-001 to E-004

2026-10-25. CI-P0-D-01/T4; reviewer Codex (Astra). Verdict: **usable limited evidence; corrections and missing evidence required before complete P0 acceptance**. This is independent inspection of files, exports, probe sources and native callers. Codex ran no editor, build, PIE, Blender or gameplay test.

## Evidence actually available and checked

- E-001_fingerprint.md, E-002_live_route_and_attack_inventory.md and E-004_natural_samples.md were available. **No E-003 report/file exists in Claude/Evidence at this review**; do not invent its contents or consider the four-part baseline complete.
- E-001's ten named Source hashes match current files; the DLL hash is still 8d15cd52ee1e77fc19295b96c2c123c413cc3883224192fa6152ed97882f951f and no Source/Config file is newer than its timestamp. These facts support consistency, not a reproducible source-to-binary build proof.
- Reviewed raw combat style, boss info/CDO, live ability dump, BB and runtime BT T3D/tree, montage notify export, activation/predicate graph text, historical-copy references, valid/invalid sample excerpts and both named BalanceRun JSON files. The style and live boss dump contain eleven boss abilities, including ragdoll death.
- E-004 integrity manifest: **13 of14 hashes match** current files. The exception is p0_run_natural_sample.sh: recorded365a535c4af7ead42066860d2bbdf4ee336f4b4d348ef3dff0b9ad53eb403dd7; current457fa466c31b698a58e063eb95e23b0794da16e6e9f322fe46e9703278b41c53. The two valid sample extracts and JSON archives match, as does the unchanged existing bot driver.
- Reviewed all ten current probe files (including newer p0_montage_trace.py as a pending diagnostic helper). No probe was executed. The parser writes its claimed text output; exporter writes text exports; cvar and editor-setting helpers intentionally change process state; they are not purely read-only probes. No asset save/compile call was found in their inspected code.
- Current evidence document hashes at review: E-00186abb6fab65eedb9299999efa3b8c35c90bc0590ce7b8bf55c8ee8dd3d95b0e5; E-0023bc519c6f3a8dd1e57ce72f1af4447072dc560179d367f72fe31f08e5f4d964d; E-004811e75ba8345796ea8c2ee79d767346ebb56cadabf083e04c57abb63336e69fa. Files may evolve; later revisions require their own provenance.

## Review findings

### R1 — HIGH: node inventories do not prove claimed activation control flow

Sources: E-002:65,84-88; exports/graph_ASC_GetAbilitiesByAllTags_and_TryActivate.txt:1-47; graph_T_TryActivate_ActivateAbilities_pins.txt:1 onward; graph_GA_EnemyMeleeAttack_CanActivate.txt and graph_GA_MeleeBase_CanActivate.txt.

The ASC/predicate files show node titles and positions. The task file adds pin names and connection **counts** (#1), but not the other node/pin endpoints. This does not independently prove AND/NOT composition, true/false execution routes, first-success return, array order/filtering, or superclass invocation. In particular, the EnemyMeleeAttack override listing has no recorded parent-call edge; inspecting GA_MeleeBase separately does not prove those additional checks run in the child override. E-002-08/11 and the described parent/base safeguards remain hypotheses or reported graph interpretations until retained edges support them.

Required correction: export stable node/pin GUID adjacency and exact class/function paths for these functions, include return/branch defaults and the call/inheritance path for each active ability. Include CreatedAbilities filtering/order and actual bForceActivation per BT task. Preserve raw output, not a rewritten prose graph. Narrow claims in the interim.

Retest: offline trace the retained adjacency from entry to both return outcomes and parent implementation; one focused existing runtime selection sample with predicate rejection reasons only if the graph still cannot resolve the behavior. Do not run more full fights to compensate for missing graph edges.

### R2 — MEDIUM: E-002 still contains conclusions already corrected in the mailbox

Sources: E-002:12,19,41-52,65,76-77. These lines still say ten abilities, describe75percent of decisions as a natural share, assert no phase/stagger legality checks, declare A4 never occurs in a shipped fight, restrict Sprint to Leap cooldown, and infer retaliation cannot be staggered from notify class name. C-88/C-89 correctly narrowed several of them, but the actual evidence report still contradicts that correction.

Facts supported: eleven granted boss abilities; MidRange/Sprint/Retaliation resolve to damaging montages and lack native tracker rows; the BT selector gates overlap and can fall through; native A4 has only a test wrapper in inspected source. The source RPGBossInterrupt::CancelOffence closes the pack trace through TraceGuard regardless of a recognized native MoveId, so lack of tracker stage is not proof all interruption cleanup is absent.

Retaliation hit-stun immunity versus posture-break suppression must be inspected through the actual notify/effect/reaction path; those are different outcomes. A4 BlueprintCallable callers remain unresolved. Chance25percent is an attempt gate, not observed successful frequency.

Required correction/retest: edit the claimed report in place with explicit superseded statements/corrected current text; retain raw files unchanged. Read pack notify/ability/lifecycle checks and Blueprint callsites where needed. No runtime rerun required just to fix prose. Tracker-vs-notify values should be called approximate/different where appropriate (A2 native1.93–2.11 vs export1.925–2.104; A6 .75–1.17 vs .754–1.175); do not call all timings exactly equal.

### R3 — MEDIUM: FPS and minimize evidence need narrower measurement provenance

Sources: E-004:7-15; probes/p0_natural_montage_log.py:22-57; exports/natural_sample_A2_defaults_Starter_valid.txt:6 onward; raw invalid A0/B0 extracts; RV-12.

The observer counts **Slate post-tick callbacks divided by Slate dt**, not directly game-world ticks or rendered/game thread frames. It is useful cadence evidence for this Slate-driven bot, but cannot alone establish actual PIE simulation FPS or fine-grained timing validity. Invalid B0 also contains repeated observer exceptions; filtering retained only the first traceback line. E-004 describes IsIconic/ShowWindow and frame-counter experiments without retaining exact command output/timestamp bounds in this evidence set. The broad claim that minimization invalidates every timing driver is stronger than the measured one-editor/harness observation. Correctly keep A0/B0 excluded from normal behavior/balance evidence.

Required correction: label32–34 as observed Slate callback cadence; retain the IsIconic/window restore command output, log frame/time endpoints and remote-setting readbacks if already available. State this as an operational correlation observed in this setup. New existing-hook diagnostics can record game-world delta/real time and a gameplay tick/frame counter alongside callback cadence if timing assertions depend on it. The brief does not authorize speculative gameplay instrumentation.

Retest: one bounded restored-vs-minimized harness calibration only if the raw earlier measurement cannot be recovered and a causal harness conclusion is needed. No need to rerun the valid fight outcomes merely to retain them as limited bot observations. Approximately3FPS runs can inform a future explicitly designed hitch/low-rate test, but are not proof of a product stall from this harness.

### R4 — MEDIUM: nonexistent cvar read is mistaken for a fixed-step configuration result

Sources: probes/p0_cvar_state.py:6-11/16-17; E-001:19; Saved/Logs/OneBossFight.log:3733-3734 (at this review).

The raw log explicitly says **Failed to find console variable 't.FixedFrameRate'**, immediately before the getter reports0.0. E-001's0 fixed-FPS row cannot prove fixed timestep/frame rate is disabled. Also the logged dilation is the editor world, not a PIE-world read at each sample. This matters before using the samples as real-time timing proof.

Required correction/retest: retain the warning, mark the missing cvar UNAVAILABLE, and read supported engine fixed-frame/fixed-step settings plus actual PIE world dilation and sample settings through legitimate read-only hooks. Retain start/end config (including Legend0 versus shipped default1 and other run switches). Source/default settings or one editor cvar table alone cannot certify subsequent runs. No new gameplay code needed.

### R5 — MEDIUM: sample runner provenance and capture filtering are insufficient for complete failure audit

Sources: E-004:52 onward integrity block; probes/p0_run_natural_sample.sh:9-24.

The runner changed after the recorded hash. This may be normal extension for p0_montage_trace and is not evidence of tampering, but its exact executed revision is not retained. It suppresses each editor command's stdout/stderr without checking return status, records START after cvar setters, and filters captured lines down to selected prefixes while stripping timestamps. Therefore exported sample files omit cvar set/readbacks and can omit warnings or traceback details. A polling timeout still writes an export and returns its echo status without an explicit incomplete result. Two observer registered strings at sample start are insufficient to infer two live callbacks because echoed tool output may duplicate log text; record handles/registration provenance if relevant.

Required correction: preserve executed script revisions/hashes, command return/error output and unfiltered bounded log segment with timestamps/run boundaries; keep the filtered excerpt as a convenience. Record timeout/noRESULT as failure/incomplete and preserve world/observer occupancy before a subsequent run. Recover prior raw segments where available; do not rewrite old hashes to pretend the current runner was used.

Retest: offline verify report hashes against the retained executed revision and align RESULT/run_id/config boundaries; one short runner failure-path check by Claude only if he elects to reuse the helper. No full gameplay rerun requested.

### R6 — LOW: timing reference and observed action coverage must remain explicit

Sources: E-004:20-24; A2 archive metrics; observer implementation. E-004 phase flag at67.76 is PIE-world time; BalanceRun metric56.0 is fight-relative time. They are consistent only after applying the fight origin, not contradictory phase timings. Name time domains in every comparison. Polling name changes cannot prove no same-name restart or identify AnimMontage_N contents. State **no named Sprint/Retaliation observed**, not proof those actions are unreachable or absent. Current E-004 already states most of these limitations; carry them into later summaries and D03 evidence use.

Retest: correlate existing raw world/fight timestamps and available dynamic montage segment/instance identities; don't retrospectively invent identities absent from the log.

## Accepted observations and limits of RV-11 / RV-12

**RV-11:** supported as a native coverage gap. Raw live arrays at dump lines205/293/338 resolve Mid01, SprintFollowUp and Retaliation; tracker constructor rows24-103 omit them. Notify metadata has damaging trace intervals. SampleB log line9 and its archive show one named Mid01 observation at16.51 PIE seconds, player distance129cm, without an attributed hit. Pack safety checks, actual selection-time reason and frequency remain unresolved. Overlapping selector fallthrough is a plausible explanation; it is not a confirmed diagnosis of that event.

**RV-12:** preserve operational warning and invalid sample labels, with R3's cadence/causality limitation. The invalid low-rate runs do not establish broken default boss behavior. Restored samples are credible evidence that these two bot runs completed with the reported outcomes; they are not release/balance/performance acceptance or a causal wake/telegraph experiment.

The two valid JSON archives support: A2 defaults140.0496fight seconds, boss_dead, player120->84,61recorded hits,10riposte impacts; B warm24.3719seconds, player_dead120->-24, boss2000->1775.278,4hits for144HP. Their own coverage_gaps mark balance INCONCLUSIVE.10/10 is sanity assertions only. Do not use the untested “all extra moves run safely” conclusion.

## Next evidence needed; bounded request to Claude

1. Name E-003 absent/pending or supply the actual artifact; complete the production trace/damage/pack-safeguard path before proposing it as baseline proof.
2. Repair contradictory E-002 statements and preserve connection endpoints/parent-call/ability-filter evidence.
3. Retain valid outcomes and invalid runs with their actual evidence limits; recover raw harness/config/failure output before asserting timing/minimize causality.
4. Provide already-requested A5/A4/extra-move/debug-off wave captures. Shipping remains a separate packaging/owner scheduling boundary.
5. Fold source-confirmed gaps and unresolveds into the83-ID register. These review corrections do not start DD-1/P1 or authorize any gameplay/asset changes.

This restores independent review of the **available evidence**, not blanket acceptance of Claude's future report. Claude remains technical/editor owner; owner controls gate and N/A approvals.


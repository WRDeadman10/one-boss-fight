# QUEUE C proposal: 200 bounded tasks for Lead selection

Proposed by Codex, 2026-11-03, after QUEUE_200_B. Ranked in execution order: the first tasks reduce status/evidence risk, then improve audits and offline tooling, then prepare tests/proofs/docs. All are scoped to source, tests, docs, or offline scripts; none require an owner decision, engine session, asset replacement, commit, or push. New C++ tests may be authored, but Claude owns build and run verification. Each item has a reviewable artifact and acceptance condition. Claude may reorder, reject, or split the proposal before assigning it.

**Historical status snapshot (C-713, 2026-11-03):** Lead accepted the proposal as Queue C and directed Codex to start immediately. S1–S10 were accepted in C-714; S11–S25 are reported in X-545, X-546, and X-548; S26–S30 in X-550; S31–S35 in X-552; S36–S40 in X-554; S41–S45 in X-558; and S46–S50 in X-559; S51–S55 completed in the audit note. S56–S60 completed in X-561; S61–S65 in X-565–X-568 and X-579; S66–S75 in X-569–X-578; S76–S80 in X-581–X-585. S81–S85 was the next range at that snapshot. C-714 resolved the lifetime RESULT counter contract and directed two stale PARTIAL_UPGRADE_PLAN descriptions to be corrected; those documentation updates are recorded in the decision, token index, and plan. C-716's validator coverage follow-up is complete in X-557: 33/33 validator tests pass and all 161 literal UE_LOG format variants validate against schemas. C-715's proof-sheet corrections and live evidence limits are recorded in the expected sheets, open-issue digest, and handover. C- messages may strike or revise items while the queue proceeds.

**Current continuation status (C-737, refreshed through X-733; 2026-11-03):** C-737 accepted the original S163–S181 receipts (X-695–X-713) and ordered a separate S163 hotfix, still awaiting Editor validation (X-714). S182–S200 have Codex receipts X-715–X-733; no Lead verdict for those receipts is present in the checked mailbox. S197 remains open pending those verdicts. Queue C is exhausted; C-734's 200-task Queue D proposal is next. BUILD-182 (332/332) is historical for the current checkout because S189 and later uncommitted Source edits followed it; C-737 separately reports 33/33 offline tool tests.

## C1–C20: current state and evidence integrity

1. **Selection-vs-start parity audit** — Compare eligibility snapshots at selector and all StartCard paths for range band, cone hold slack, and reposition; acceptance: every deliberate difference is documented and every accidental divergence has a source location plus regression plan.
2. **Pure-model fight/restart test** — Build an engine-free scenario through selection, card timeline, finish, reset, and a second generation; acceptance: restart returns model state to documented baseline and stale generation events cannot alter the new fight.
3. **Result-counter scope follow-up** — Recheck all restart evidence and consumers for accepted/guarded/parried/damage totals; acceptance: one recommendation separates lifetime and generation totals, and code changes remain deferred until Lead decides scope.
4. **Editor-proof driver usability audit** — Review `drive_opt_in_features.py` and `drive_pie.py`; acceptance: a one-feature run plan provides explicit PASS/FAIL output and does not claim numeric relations it cannot inspect.
5. **Selector filter parity tests** — Identify missing pure tests for range band, hold slack, cone, and reposition eligibility; acceptance: each proposed regression gives exact boundary inputs and expected selected/refused result.
6. **Result-counter scope note** — Compare executor lifetime counters with restart evidence; acceptance: a source/log matrix distinguishes lifetime totals from per-generation values without changing runtime behavior.
7. **Restart evidence index** — Index all retained generation-two logs and result lines; acceptance: each restart run has generation, reset, terminal result, and counter locations.
8. **Live-proof vs unit-proof audit** — Compare each PARTIAL/WITNESSED note with its exact evidence type; acceptance: claims using code or compilation alone as live proof are flagged.
9. **Proof status vocabulary** — Find status synonyms across current docs; acceptance: recommend and document one glossary for coded, built, unit-proven, and live-proven.
10. **Decision trace index** — Link current active implementation constraints to their DECISIONS rows; acceptance: every sampled constraint has one dated source decision or is marked as an undocumented choice.
11. **Open-issue digest parity** — Compare the digest against open KI rows; acceptance: every in-scope open issue is represented once with matching requested evidence.
12. **Known-issue stale reference scan** — Resolve file, line, and evidence paths in active KI entries; acceptance: dead links and shifted line citations are listed, not silently rewritten.
13. **Build-record source audit** — Compare BUILD IDs and evidence links in the latest TEST_PLAN section; acceptance: each recent BUILD record points to an existing result artifact.
14. **Queue receipt completeness** — Compare assigned C messages with X completion replies for the current queue; acceptance: a table identifies missing, duplicate, or wrong-recipient receipts.
15. **Queue status reconciliation** — Compare QUEUE_200_B verdict log, TASKS, TEST_PLAN, and mailbox; acceptance: every batch has one matching status and review outcome.
16. **W3 proof status check** — Compare R3c evidence, EXPECTED sheet, KI-149, and digest; acceptance: all state that the live `strafe_stuck` line remains unproven.
17. **Hook-scope note review** — Compare KI-157 with compile guards and restart code; acceptance: the note accurately limits the issue to non-shipping hooks.
18. **Cooldown proof setup parity** — Compare the three profile scripts and expected sheets; acceptance: each writes/reads 0.0 cooldown and explains `PhasePoolCannotStarve`.
19. **Current owner-action inventory** — Search current docs for explicit owner action requests; acceptance: a short list with source/date and no implied unapproved work.
20. **Evidence retention map** — Inventory active proof outputs vs archived/failed runs; acceptance: a map explains where to find latest pass, negative control, and retained failure per feature.

## C21–C40: validators and telemetry tooling

21. **Validator token checker edge cases** — Review `check_validator_tokens.py`; acceptance: synthetic cases cover multiline logging, repeated tokens, macro-wrapped tokens, and false positives.
22. **Validator token schema-source mapping** — Trace each extracted token to schema and indexes; acceptance: report distinguishes schema presence from semantic documentation.
23. **Log schema duplicate detector** — Add an offline duplicate-schema check; acceptance: exact duplicate and conflicting duplicate fixtures produce separate diagnostics.
24. **Schema regex sample coverage** — Add a report of schemas with no real retained log sample; acceptance: output lists token, schema line, and missing evidence sample.
25. **Schema permissiveness scan** — Identify patterns accepting empty or overly broad values; acceptance: a review list gives a concrete malformed line each pattern currently allows.
26. **Telemetry-field drift report** — Compare literal UE_LOG key/value fields with schemas; acceptance: tool reports unexpected and absent fields with source lines.
27. **Semantic-index parity** — Compare schema token names against LOG_TOKENS semantic index; acceptance: command exits nonzero on missing/duplicate index rows and passes current files.
28. **Emission-index parity** — Compare source emission paths against the emission-source index; acceptance: command reports each missing token and source location.
29. **Validator test mutation audit** — Review existing schema tests; acceptance: every regex family has at least one malformed-value and one missing-field case or a documented gap.
30. **FrameworkProof token timeline grouping** — Improve the timeline tool to group by encounter/generation/instance; acceptance: fixture log produces stable grouped output with no loss of raw line numbers.
31. **FrameworkProof result parser malformed inputs** — Harden `framework_results.py`; acceptance: missing fields, repeated RESULT, and nonnumeric values yield actionable diagnostics.
32. **FrameworkProof result generation report** — Add generation association to result summaries; acceptance: restart fixture distinguishes two results and labels missing generation explicitly.
33. **Suite log summary output** — Add machine-readable JSON output to suite summarizer; acceptance: a retained log produces stable test totals and failure names in JSON.
34. **Suite diff exit semantics** — Review `diff_suite_logs.py`; acceptance: documented exit codes distinguish identical, changed, and invalid input.
35. **Evidence manifest path safety** — Audit `evidence_pack.py`; acceptance: a temporary fixture proves source files are copied without escaping destination root.
36. **Manifest verification mode** — Add a read-only evidence-manifest verifier; acceptance: valid fixture passes and altered/missing file hash fails with the path named.
37. **Stale-log detector** — Add timestamp/hash checks to proof reports; acceptance: a stale log is flagged separately from a failed gameplay expectation.
38. **Expected-sheet token lint** — Check token spellings against schemas; acceptance: typo fixture fails and manual numeric checklist items remain manual.
39. **Expected-sheet completeness lint** — Require setup, control, expected signal, and fail signal sections; acceptance: valid existing sheets pass and one missing-section fixture fails.
40. **Tooling command index** — Reconcile `TOOLS.md` invocations with actual CLI help; acceptance: every command resolves to a tool and uses supported flags.

## C41–C60: source lifecycle and boundary audits

41. **Boss restart state delta** — Recheck character fields against initialize/restart/terminal paths; acceptance: each field is classified reset, immutable, intentionally cumulative, or unresolved with source locations.
42. **Executor counter contract** — Trace `HitsAccepted`, `HitsGuarded`, `HitsParried`, and `AppliedDamage`; acceptance: report documents every consumer and observed restart semantics for Lead review.
43. **Player component EndPlay inventory** — Audit owned tags, delegates, timers, and weak references; acceptance: each acquisition has matching release or an explicit retry/owner-lifetime explanation.
44. **World subsystem teardown audit** — Review subsystem timers and handles; acceptance: each callback's world and UObject lifetime behavior is recorded.
45. **Enhanced Input binding ownership** — Inspect input binding registrations and component attachment paths; acceptance: static lifecycle matrix identifies whether removal can leave surviving bindings.
46. **Dynamic delegate lifetime audit** — Scan `AddDynamic`/`RemoveDynamic`; acceptance: each binding pair has source lines and unmatched sites are separated from engine-managed callbacks.
47. **Timer capture audit** — Scan timer lambdas and weak/strong captures; acceptance: every capture is classified for actor, component, world, and asset lifetime.
48. **Tag ownership audit extension** — Include Blueprint-exposed tag bridges and native reads; acceptance: C++ scope boundary and unresolved pack-owned paths are explicit.
49. **Profile validation/runtime parity** — Compare every ResolveProfile refusal with runtime use; acceptance: no profile field is silently clamped or ignored without documentation.
50. **MoveCard validation/runtime parity** — Compare validated card domains with rule consumption; acceptance: each numeric field's accepted range matches downstream assumptions or a discrepancy is cited.
51. **Float boundary inventory** — Find strict/inclusive comparisons on editable values; acceptance: report names exact boundary and current unit coverage.
52. **Non-finite handling inventory** — Trace externally authored float values; acceptance: every runtime math entry point either validates finite input or documents trusted validated provenance.
53. **Randomness ownership inventory** — Distinguish global random, local stream, and seeded gameplay choices; acceptance: every combat decision random source is identified with seed/reset behavior.
54. **Tick-order dependency map** — Review component tick groups/prerequisites; acceptance: each correctness-critical order has a prerequisite or evidence-backed explanation.
55. **Async asset load lifecycle** — Audit handles/callbacks for async loads; acceptance: cancellation, weak owner, and completion paths are mapped with no editor execution.
56. **World actor spawn listener audit** — Recheck registration removal under world teardown and subsystem shutdown; acceptance: registration and removal sites are paired in a concise table.
57. **Blueprint reflection failure audit** — Review reflected calls that return success/failure; acceptance: callers never report successful state after an ignored required-call failure, or each exception is documented.
58. **Damage outcome consumer audit** — Trace Accepted/Guarded/Parried/Rejected outcomes across new and legacy paths; acceptance: every path has one counter and downstream side-effect disposition.
59. **Restart generation token audit** — Trace all async payloads/callbacks against generation; acceptance: every stale-work path either rejects or is documented as generation-independent.
60. **Terminal-state idempotence audit** — Inspect Die/Fail/EndPlay repeat calls; acceptance: state, timers, components, and logs are shown idempotent or a repeat-call risk is cited.

## C61–C80: test-suite quality and coverage audits

61. **New rule-test coverage matrix** — Map Q101–Q125 headers to test names and assertions; acceptance: each rule's boundaries and claimed property are linked.
62. **Opt-in runtime test matrix** — Map each profile field group to validation and runtime tests; acceptance: fields without behavior-level tests are identified separately from validation-only coverage.
63. **Restart behavior coverage matrix** — Map resettable fields to restart tests; acceptance: each field is tested or has a reason it cannot affect a later generation.
64. **Negative-control coverage matrix** — Inventory tests proving a disabled gate preserves behavior; acceptance: every major opt-in group has a negative control or a documented gap.
65. **Automation test namespace audit** — Scan registration paths; acceptance: every project automation test is under approved namespace and no duplicate canonical name exists.
66. **Test isolation and cleanup audit** — Review world, actor, ticker, CVar, delegate, and static cleanup; acceptance: each fixture teardown owns all created state or has a cited exception.
67. **CVar provenance audit** — Review tests mutating console variables; acceptance: original value and priority/provenance restoration are explicitly covered or the risk is documented.
68. **Asset-backed test context audit** — Confirm EditorContext for asset/file/registry services; acceptance: each discovered service call maps to correct test flags.
69. **Async test completion audit** — Review latent automation tests; acceptance: completion/failure paths have finite timeout and no dangling latent command.
70. **Property test seed audit** — Review randomized tests; acceptance: every randomized failure can report/replay a fixed seed.
71. **Boundary fixture review: strict comparisons** — Find adjacent representable-value cases; acceptance: test inputs are independent constants or typed `nextafter` values.
72. **Boundary fixture review: intervals** — Audit closed/open window endpoints; acceptance: each interval has exact endpoint and adjacent-side assertions.
73. **Boundary fixture review: monotonic rules** — Hand-check claimed monotonic property at a point and inspect test ordering; acceptance: a counterexample mutation would fail a named assertion.
74. **Boundary fixture review: saturation** — Audit clamps/floors/caps; acceptance: tests cover just below, at, and above each cap.
75. **Boundary fixture review: arithmetic overflow** — Identify multiplication/sum overflow paths; acceptance: finite extreme tests cover saturation or refusal.
76. **Test assertion quality scan** — Re-run static tautology/duplicate review without executing tests; acceptance: findings include exact assertion and distinct-input analysis.
77. **Test loop control scan** — Inspect loops in tests for empty/constant conditions and runaway counts; acceptance: every data-dependent loop has a bounded source or explicit maximum.
78. **Test naming parity** — Compare names to tested outcomes; acceptance: vague or misleading names are listed with a more precise proposed name.
79. **Test diagnostic quality** — Review assertion messages; acceptance: failed boundary/property assertions identify relevant inputs and expected relation.
80. **Test file organization audit** — Compare test source grouping to rule headers; acceptance: misplaced/overloaded files are listed without moving them.

## C81–C100: isolated regression tests (new files only)

81. **Restart counter semantics fixture** — Add a pure fixture for chosen counter scope once Lead specifies it; acceptance: generation-one and generation-two totals are distinguishable and expected scope is asserted.
82. **Proof-hook restart boundary test** — Add a non-shipping-only helper test for interrupted hook state; acceptance: test reproduces persistence and documents that production build excludes hooks.
83. **Stale generation callback test** — Add a new test for old-generation callback rejection; acceptance: callback is refused and new-generation state remains unchanged.
84. **Failed tag removal retry test** — Add a narrow fake removal failure test; acceptance: owned tag state remains retryable until successful removal or owner death.
85. **Input binding duplicate prevention test** — Add a test around component attachment lifecycle; acceptance: repeated attach does not create duplicate input responses.
86. **Timer owner teardown test** — Add a callback-lifetime test; acceptance: callback after owner invalidation does not dereference or spawn owner-bound behavior.
87. **Delayed VFX teardown test** — Add a pure scheduling policy test if one exists; acceptance: expected spawn/cancel result is explicit for world alive/owner dead.
88. **Restart state partition test** — Add a test covering immutable, reset, and lifetime fields; acceptance: representative fields in each category behave as documented.
89. **Move selector start-snapshot test expansion** — Extend only in a new test file for cone/range parity; acceptance: selected candidate starts against equivalent snapshot or fails intentionally.
90. **Combo fresh-snapshot fallback test** — Add isolated coverage for model refusal after combo gate; acceptance: combo exits and ordinary selector may resume without encounter failure.
91. **Cooldown starvation property regression** — Add a property test for card pool count/cooldown condition; acceptance: zero cooldown and sufficient-card boundary pass, starvation counterexample refuses.
92. **CVar set-by-priority restoration test** — Add a scoped mutation fixture; acceptance: both value and set-by source are restored after success and early return.
93. **Fresh-profile negative-control helper test** — Add a test utility demonstrating independent profile instances; acceptance: negative case cannot inherit prior mutations.
94. **MoveCard serialization default test** — Test zero/default deserialization for new opt-in fields; acceptance: absent fields retain intended disabled state.
95. **Malformed telemetry numeric test** — Add validator tests for NaN/infinity/text in numeric fields; acceptance: malformed values fail schema validation.
96. **Repeated telemetry event ordering test** — Add a pure parser test for duplicated and reordered events; acceptance: parser retains order and reports invalid lifecycle.
97. **Expected-sheet control test** — Add a new checker fixture with enabled/control logs; acceptance: enabled expected token passes and control token leakage fails.
98. **Manifest mutation regression test** — Add an offline unit test for evidence hash mismatch; acceptance: changed bytes are detected and original paths are reported.
99. **Profile group all-or-none tests** — Add only missing validation cases found in C62; acceptance: each coupled group's partial population is explicitly accepted or refused.
100. **Test hooks shipping-guard test** — Add static source validation for hook declarations/definitions; acceptance: no hook registration remains in Shipping-visible code.

## C101–C120: offline proof preparation for coded features

101. **Aggro switch profile readback** — Review or add authoring script for aggro profile; acceptance: saved asset readback verifies only intended gate and selector settings.
102. **Aggro switch expected sheet** — Write exact enabled/negative-control telemetry; acceptance: threshold, number of dodges, band transition, and no-transition control are specified.
103. **Fatigue multi-attack calibration plan** — Analyze eligible card/timing options without Unreal; acceptance: each whiff window is feasible and exact attack-start/active timing is cited.
104. **Fatigue failure/control sheet** — Update fatigue EXPECTED criteria; acceptance: all counted whiffs are confirmed by no accepted/guarded/parried contacts and floor behavior.
105. **Yaw probe A/B setup audit** — Inspect yaw profile authoring script; acceptance: generated profile differs only in probe/hysteresis setting and saved map identity is explicit.
106. **Yaw probe no-hysteresis expected trace** — Specify expected edge flicker without hysteresis; acceptance: consecutive sample relation is measurable and control is bounded.
107. **Yaw probe hysteresis expected trace** — Specify expected held candidate with hysteresis; acceptance: entry/exit thresholds and tolerated angular band are exact.
108. **Parry-fair telegraph negative control** — Review expected sheet; acceptance: baseline rate is unchanged and both rate and restoration evidence are required.
109. **Parry stamina source trace** — Verify pack attribute and cost/refund code; acceptance: `Attribute.Stamina` or changed source is cited with exact call path.
110. **Parry stamina proof checklist** — Specify player input, cost, refund, failure path, and control; acceptance: every expected line has a source-backed meaning.
111. **Overlay parry line checklist** — Specify enable CVar, state values, visibility, and disabled control; acceptance: documented values distinguish no parry, active, and grade state.
112. **Stuck recovery alternate setup survey** — Read existing arena/nav bounds and movement constraints; acceptance: list safe candidate setups with measured source/content bounds, no new cage map.
113. **Stuck recovery expected telemetry** — Refine `strafe_stuck` checklist; acceptance: flip, movedRatio, subsequent direction, and normal-end control are explicit.
114. **Reposition proof sheet audit** — Compare MOV proof logs to profile settings; acceptance: walk-to-band and turn-in-place evidence are distinct from other gates.
115. **Arena leash proof sheet audit** — Define inside/outside radius control; acceptance: baseline target point, radius, and abort/resume signals are exact.
116. **Center-bias proof feasibility audit** — Compare radius, bias, and target positions; acceptance: expected centre-side displacement is geometrically hand-calculated.
117. **LOS memory proof checklist** — Specify blocked trace, last-seen movement, regain, timeout, and negative control; acceptance: each stage has a token or labeled manual observation.
118. **Flask reaction proof checklist** — Specify drink event timing, seeded delay bounds, reaction, and late-drink negative control; acceptance: event order is timestamp-checkable.
119. **Anti-cheese proof setup** — Define hug/kite windows and card weights; acceptance: each configured range produces an unambiguous score/selection comparison.
120. **Tie-band seed proof setup** — Define paired seeds and control; acceptance: expected sequence comparison distinguishes tie randomization from ordinary weighted choice.

## C121–C140: graders and proof report improvements

121. **Restart RESULT counter grader review** — Inspect grader API and fixture patterns; acceptance: propose a separate generation-aware result check without changing the authoritative existing grader.
122. **F8 restart log split parser** — Add offline parsing for generation segments; acceptance: each segment reports attacks, result counters, and health delta independently.
123. **Counter lifetime consistency report** — Compare per-card, per-result, and target-health counters; acceptance: report highlights cumulative totals without labeling them generation-local.
124. **Validator generation-field schema proposal** — Assess how generation could be attached to RESULT; acceptance: schema-compatible migration plan and old-log behavior are documented.
125. **Proof report manual-item safeguards** — Review `proof_report.py`; acceptance: numeric relations stay MANUAL unless explicit machine-readable checks are provided.
126. **Proof report negative-control support** — Add paired-control format; acceptance: a control-only token leak makes the report fail.
127. **Proof report source annotations** — Add expected-sheet line citations to output; acceptance: each PASS/FAIL/MANUAL row cites its checklist line.
128. **Proof report stale artifact protection** — Require explicit log path and show mtime/hash; acceptance: report visibly identifies input file and digest.
129. **PIE log run identity check** — Add parser for map/profile/run ID where present; acceptance: mismatch is reported before gameplay criteria are evaluated.
130. **PIE run completeness check** — Detect missing terminal result or truncated process; acceptance: incomplete run is distinct from a feature failure.
131. **Trace token relation fixtures** — Add parser fixture for `decision`/`candidate` order; acceptance: malformed ordering is caught without asserting game semantics.
132. **Telemetry numeric relation plugin format** — Specify a tiny declarative relation format; acceptance: equality, range, ratio, and monotonic cases have fixtures and unsupported syntax fails closed.
133. **Schema canonical sample bundle** — Collect one real sample per current schema; acceptance: manifest maps token to sample path and line, with synthetic samples labeled.
134. **Failure catalogue source cross-check** — Reconcile each failure cause against validator/runtime output; acceptance: no diagnosis cites a token that cannot occur in the described path.
135. **Profile refusal report audit** — Compare validator errors with failure catalogue; acceptance: each known refusal has exact expected token and setup correction.
136. **Result outcome vocabulary audit** — Compare source, schemas, and graders; acceptance: all current outcome names are enumerated and unknown names are handled intentionally.
137. **Log duplicate-run detector** — Detect accidental repeated PIE chunks in concatenated logs; acceptance: fixture reports duplicate run boundaries and preserves raw lines.
138. **Evidence summary table generator** — Add offline report from evidence folders; acceptance: creates one row per run with map, profile, date, outcome, validator, and digest.
139. **PIE command manifest audit** — Compare `command.json` to expected sheet; acceptance: script reports missing required CVar/argument and extra unsafe mutation.
140. **Proof asset provenance check** — Compare generated asset names with scripts and evidence metadata; acceptance: output identifies source profile/map and generated destination without deleting assets.

## C141–C160: source and designer documentation

141. **Profile reference defaults refresh** — Compare `REF_PROFILE.md` with current UPROPERTY defaults; acceptance: every editable field has exact type, unit, default, and source line.
142. **Profile reference validation refresh** — Compare profile validation rules with reference text; acceptance: enabled/disabled and failure conditions match source.
143. **MoveCard reference defaults refresh** — Compare card fields with MoveCard v2 source; acceptance: type, unit, default, and baked-data relation are complete.
144. **MoveCard lifecycle guide** — Document bake, validate, resolve, start, and abort lifecycle; acceptance: each transition links to source and authoring tool.
145. **Framework boss reset guide** — Document generation reset order; acceptance: executor, selector, tags, player references, and proof hooks have explicit disposition.
146. **Executor accounting guide** — Explain per-card and lifetime counters; acceptance: sample log reconciles target HP delta with executor totals.
147. **Selector trace guide** — Document candidate rejection/score/tie/hysteresis fields; acceptance: each field has unit and sample interpretation.
148. **Combo gate guide** — Document fresh snapshots, gate consumption, recovery, and fallback; acceptance: normal and refusal paths cite current source lines.
149. **Proof-only hooks index** — Inventory `rpg.BossProof*` controls; acceptance: each has source guard, exact invocation, and Shipping status.
150. **Runtime log glossary** — Consolidate recent FrameworkProof tokens; acceptance: token names link to schema and emission source.
151. **Failure-mode catalogue refresh** — Update from C-712 and current live evidence; acceptance: R3c is not listed as a successful stuck proof.
152. **Expected-sheet author guide examples** — Add one strong sheet and one honest limited-proof example; acceptance: distinguishes measured, inferred, and manual criteria.
153. **Test author guide fixture lifecycle** — Add setup/teardown examples from current automation tests; acceptance: world, UObject, CVar, and async cleanup are covered.
154. **Offline tool author guide** — Document CLI contract and exit behavior; acceptance: every maintained tool has input, output, error, and safety notes.
155. **Evidence retention guide** — Document pass, negative control, failed attempt, and manifest retention; acceptance: new contributors can find all four without mailbox archaeology.
156. **Source ownership map refresh** — Compare per-folder READMEs against current modules; acceptance: stale owners/paths are identified and corrected.
157. **Player subsystem attach guide** — Document component attachment order and guards; acceptance: boss/player branches and input timing are explicit.
158. **Pack boundary guide** — Mark native, reflected pack, Blueprint, and asset concerns; acceptance: each cited behavior identifies evidence boundary.
159. **Telemetry onboarding example** — Show one token from UE_LOG through schema, semantic index, emitter index, expected sheet, and log; acceptance: all paths resolve.
160. **Handover link audit** — Verify all handover links and commands against current names; acceptance: no stale links or unsupported CLI flags remain.

## C161–C180: safe offline script and repository audits

161. **Editor script deletion scan** — Find asset deletion calls; acceptance: every call checks existing destination/referencers or is documented as unsafe.
162. **Editor script overwrite scan** — Find save/overwrite paths; acceptance: each generated asset has collision behavior stated in script and usage docs.
163. **Editor script map-save scan** — Review world load/save paths; acceptance: scripts save to new destinations and do not delete or replace referenced source maps.
164. **Editor script property-name validation** — Audit reflected `set_editor_property` strings; acceptance: each property has source/content precedent or readback guard.
165. **Editor script boolean convention scan** — Find bool property accesses; acceptance: `b`/non-`b` names are checked against actual reflected fields.
166. **Editor script absolute-path scan** — Find former-user paths; acceptance: repo-relative alternatives are proposed with exact lines.
167. **Python syntax inventory refresh** — Parse source scripts without executing them; acceptance: syntax failures are listed by file and line.
168. **PowerShell parse inventory refresh** — Parse scripts without executing build/game commands; acceptance: syntax and return-code propagation risks are listed.
169. **Subprocess exit-code audit** — Review offline/editor wrappers; acceptance: child failure is propagated or explicitly treated as optional.
170. **Path normalization audit** — Inspect path handling on Windows/Python; acceptance: paths with spaces, separators, and Unicode have a safe fixture.
171. **JSON write atomicity audit** — Inspect tool outputs; acceptance: interrupted writes cannot silently replace valid manifests or profiles.
172. **Temporary-directory cleanup audit** — Review scratch scripts and tests; acceptance: cleanup is scoped to created temporary roots only.
173. **CLI input validation audit** — Check required args and malformed files; acceptance: errors name the bad input and exit nonzero without side effects.
174. **Offline tool network audit** — Search tools for network access; acceptance: each network use is documented or removed from offline tools.
175. **Script import side-effect audit** — Inspect top-level code; acceptance: importing utility modules performs no editor, filesystem mutation, or process launch.
176. **Script deterministic output audit** — Run only pure temporary fixtures; acceptance: repeated output is byte-stable or nondeterminism is documented.
177. **Report redaction audit** — Check logs/reports for user paths and environment values; acceptance: generated reports omit secrets and unnecessary personal paths.
178. **Generated file header audit** — Compare scaffolds with repo conventions; acceptance: generated files include license, module path, and evidence caveat.
179. **Tool usage consistency audit** — Compare README command snippets with `--help`; acceptance: stale invocations are listed with corrected syntax.
180. **Offline tool inventory completeness** — Compare `TOOLS.md` against `Scripts/Tools`; acceptance: every maintained utility is indexed or explicitly excluded.

## C181–C200: release readiness and close-out

181. **Shipping guard inventory refresh** — Review console/test hook registrations; acceptance: each remains behind intended build guard or is explicitly approved.
182. **Shipping symbol risk scan** — Inspect test-only symbols and registrations; acceptance: suspected Shipping leaks are cited without claiming binary proof.
183. **Packaged-content checklist audit** — Compare `CheckStagedContent.py` with required asset references; acceptance: missing assets produce named errors in a temporary manifest fixture.
184. **Build failure propagation review** — Recheck `Rebuild.ps1`; acceptance: compiler and test failure paths return nonzero and print usable log paths.
185. **Driver failure propagation review** — Recheck `RunDrivers.ps1`; acceptance: timeout, zero-check, and failed-check cases return nonzero.
186. **Stale process/lock runbook** — Review editor and staging lock instructions; acceptance: cleanup avoids broad process-name kills and names safe process-tree steps.
187. **Evidence hash refresh checklist** — Document when source, binary, and log hashes must be recomputed; acceptance: handover distinguishes same source/new build from unchanged evidence.
188. **Feature proof release gate** — Define coded/unit/live evidence required before a profile option ships; acceptance: checklist rejects code-only and schema-only claims.
189. **Opt-in default-off audit** — Re-scan all experimental profile fields; acceptance: each default and group gate matches validation and release policy.
190. **Owner-independent task check** — Review proposed tasks for owner decisions/assets/account access; acceptance: every item either needs none or is removed from the queue.
191. **Queue C review receipt template** — Prepare a five-task status format; acceptance: it records acceptance, hotfixes, evidence, and next batch in one message.
192. **Lead hotfix intake guide** — Document how rejected items are traced to exact diff/evidence; acceptance: no hotfix is mixed into a later unreviewed batch.
193. **Fresh checkout handover validation** — Walk instructions using only docs/source paths; acceptance: any missing dependency is added to handover.
194. **Current artifact inventory** — List new files from QUEUE_200_B and later queue work; acceptance: each has owner, purpose, and review/build state.
195. **Open findings disposition table** — Consolidate unresolved Codex findings; acceptance: each has Lead decision, owner action, follow-up task, or retained limit.
196. **Queue C midpoint review package** — Assemble the first ten batch reports and current suite/evidence references; acceptance: Lead can review without searching raw mailbox history.
197. **Queue C final review package** — Assemble accepted/hotfix/rejected dispositions; acceptance: every assigned task maps to a Lead verdict.
198. **Queue C status dashboard** — Summarize complete, in review, hotfix, and not started counts; acceptance: totals equal the task list and no task is implicitly accepted.
199. **Next queue proposal delta** — Compare Queue C scope to completed queues and active roadmap; acceptance: no duplicate task remains without a stated reason.
200. **Final consistency pass** — Reconcile TASKS, PROJECT_STATE, TEST_PLAN, KNOWN_ISSUES, DECISIONS, and evidence status; acceptance: current counts agree with source authorities and historical counts remain labeled by date/build.

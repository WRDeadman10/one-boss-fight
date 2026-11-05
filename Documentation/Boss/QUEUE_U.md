# Queue U — two lanes, 50 tasks each (Codex and Antigravity)

Written by the lead (Claude), 2026-11-05, after Round 4 (owner console, RTX 3060): legacy 27.29 fps / p99 42.88 ms, data route
27.10 fps / p99 42.85 ms. A7 regression gate PASS; the absolute 60 fps / 16.67 ms target FAILS on both routes, GPU-bound
(render/GPU p99 ~41-43 ms, game thread ~5.6 ms; rounds 1-2: 12 shadow-casting brazier lights ~8 ms, volumetric clouds 5.3 ms,
TSR 3.5 ms). Restore point 09f33bd is pushed.

Rules for BOTH lanes: C-797 (5-task batches, one post per batch or per Source/Content change, roll to Queue V at task 45),
C-820 (no status-only or re-check tasks; "WAITING ON LEAD: <item>" then the next task), C-829 (a lead HOTFIX first),
C-871 compile checklist, C-883 file-safety rules (no cleanup under the repo, back up docs > 50 KB, targeted edits only).
PERFORMANCE IS MEASURE-AND-PROPOSE until the owner un-parks it: no change to lights, materials, post-process, scalability or
any shipped look without an owner yes. Every proposal carries its measured or predicted ms saving and the visual cost.
Codex posts X-, Antigravity posts A-; the lead reviews, builds and runs. Antigravity commits per batch after the lead's
verdict (owner authority), never staging *.webm or Saved/.

## Lane C — Codex (U-C01 … U-C50)
| ID | Task | Acceptance |
|---|---|---|
| U-C01 | DONE — GPU cost model from rounds 1–4: known fire-light shadow, VSM, cloud, TSR and Lumen evidence with source and ms | `U-C01_GPU_COST_MODEL.md`; every measured row cites its run folder; limits stated |
| U-C02 | DONE — Round 5 one-CVar experiment set targeting shadow count/radius, VSM, clouds, TSR/TAA and Lumen; Development-only radius control | `round5_experiments.json`; dry-run lists 20 rows (16 treatments, baseline then repeat after each four); eight offline fixtures |
| U-C03 | READY FOR LEAD REVIEW — Round 5 owner prompt in BENCHKIT_README | prompt includes console/GPU check, selected-route Development build, dry-run, run/collect steps and no-shipped-look guard |
| U-C04 | DONE — Round 5 variable-length intake and >5% baseline-drift detection | `round4_benchmark_report.py experiments`; `round5_benchmark.schema.json`; fixtures cover N rows, identity/drift quarantine and one-CVar validation |
| U-C05 | DONE — predicted GPU budget and visual-cost table | `U-C05_PREDICTED_GPU_BUDGET.md`; reports no defensible current-build combination, uses historical trials only as retest candidates |
| U-C06 | Scalability profile proposal (DefaultScalability/DeviceProfiles) for a "Performance" preset, NOT applied | diff file + rationale |
| U-C07 | Opt-in runtime switch to load that preset for A/B runs only (non-Shipping), unset = unchanged | PRODUCTION CHANGE flag, test |
| U-C08 | Frame-pacing hitch analysis of r4_legacy_c (310 ms) and warmups (699 ms): which frames, which thread, shader compile or streaming | frames.csv evidence |
| U-C09 | PSO/shader-precache proposal if U-C08 shows compile hitches | proposal |
| U-C10 | X- batch | — |
| U-C11 | A7-B retirement: implementation plan as a patch series list (file:line per step), tests replacing legacy-route tests, rollback | plan |
| U-C12 | Write the replacement tests for A7-B now, gated so they pass on both routes today | suite green |
| U-C13 | Default-route switch design: how the game would default to the data route when legacy is retired (config key, not code) | design, no change |
| U-C14 | Setter-caller design: smallest real Blueprint caller (a menu/level option) for J049-A, asset list for owner approval | list |
| U-C15 | Packaged recovery smoke procedure for the setter route (when a caller exists) | sheet |
| U-C16 | Parity nightly: one command runs all 31 pairs and writes one report (from S23) | dry-run + test |
| U-C17 | Parity report diff tool: compare two nightly reports, flag new WARN/FAIL | fixtures |
| U-C18 | Data-route authoring: second encounter definition dry-run from the legacy-defaults baseline (S24) to prove the pipeline is repeatable | dry-run 0 MISMATCH |
| U-C19 | Intentional-tuning workflow doc + one worked example (field, value, reason, approval id) | example validates |
| U-C20 | X- batch | — |
| U-C21 | Play-test intake: parse the owner's S42 notes into issue rows (system, severity, repro) when they arrive | WAITING ON OWNER until then |
| U-C22 | Input latency measurement driver: press-to-montage-start time for attack/dodge/parry in PIE, both routes | driver + LEAD-RUN |
| U-C23 | Hit-feel audit: hit-stop, camera shake, sound per hit type vs the design freeze values | table |
| U-C24 | Boss telegraph readability audit: telegraph duration vs reaction window per attack (tracker defaults) | table |
| U-C25 | Phase-two transition audit at 60 % health: timing, roar, buffs, HUD | driver checks cite |
| U-C26 | Death/restart flow audit: time from boss death to fog gate/victory, player death to respawn | driver checks cite |
| U-C27 | Proposals from U-C22..U-C26 (proposals only) | list |
| U-C28 | KNOWN_ISSUES rows for any confirmed defect from U-C22..U-C26 | rows |
| U-C29 | Offline suite timing guard (< 10 s) | measured |
| U-C30 | X- batch | — |
| U-C31 | Source: remove dead code paths of the retired Greystone/Sevarog pipeline (list only, then lead decides) | list with references |
| U-C32 | Scripts/Editor: archive retired sevarog_pack_* scripts into Scripts/Editor/Archive (move, no delete), fix references | lead approval first |
| U-C33 | Warnings audit: compile with warnings as errors already; list deprecations reported by UE 5.5 build log | table |
| U-C34 | Automation suite runtime: slowest 20 tests, proposals to cut runtime | table |
| U-C35 | Test naming/ownership index for the 463 native tests | index |
| U-C36 | Mailbox digest tool: summarize decisions between two C- ids | tool + test |
| U-C37 | DECISIONS index C-878..C-8xx | lines |
| U-C38 | KNOWN_ISSUES sweep after Round 4 | rows |
| U-C39 | TEST_PLAN index for Round 4/5 | links resolve |
| U-C40 | X- batch | — |
| U-C41 | Review Antigravity's lane U-A outputs that touch tools or Source (second reviewer) | per-batch notes |
| U-C42 | Cross-check AG's ledger JSON updates against evidence paths | tool run |
| U-C43 | Round 5 results intake when they arrive | WAITING ON OWNER until then |
| U-C44 | Performance decision brief for the owner from rounds 1-5 (options, ms, visual cost) | one page |
| U-C45 | Write QUEUE_V (Codex lane) | 50 IDs |
| U-C46 | Docs consistency pass | no contradictions |
| U-C47 | Tools README refresh | links resolve |
| U-C48 | Bench kit rebuild checklist (MakeBenchKit dependency test green) | checklist |
| U-C49 | Handover note for the next session | one page |
| U-C50 | Lane closed | X- line |

## Lane A — Antigravity (U-A01 … U-A50)
| ID | Task | Acceptance |
|---|---|---|
| U-A01 | Ledger witness_status_v3.json: add the rows witnessed since your last update (AWR-004, MOV-001, HIT-008, COM-004, SEL-008, A5 parity, D1, D5, T1, G2) from S31_S35_ANTIGRAVITY_LEDGER_HANDOVER.md | DONE (v3.37: 80 WITNESSED / 2 PARTIAL / 0 NOT YET; 5 combat + 5 route parity rows) |
| U-A02 | Independent review of today's PRODUCTION CHANGES since 6c7d3fc (D1 attach bundle, T1 tick prerequisites, G1 benchmark selector, CueMode Shipping guard, P17 strafe fields) | DONE (APPROVED in U_A01_U_A04_AUDIT.md) |
| U-A03 | Independent review of the D5 legacy-defaults table (Scripts/Tools/legacy_defaults_g044.json) against Source | DONE (AGREE: 249/249 native C++ rules match Source) |
| U-A04 | Review the comparator rules D6b/c/d/O4 for false-PASS risk (like the 2000 vs 1500 case) | DONE (Findings in U_A01_U_A04_AUDIT.md: bracketed token stripping vulnerability & recommendations) |
| U-A05 | A- batch + commit of the reviewed state | DONE (commit 38680a2) |
| U-A06 | Arena lighting audit in the editor (read-only): every light, mobility, shadow casting, radius, intensity, cost class | table |
| U-A07 | Lighting proposal A: fewer shadow casters (e.g. 4 of 12 braziers cast), others unshadowed; predicted ms and screenshots | proposal, no change |
| U-A08 | Lighting proposal B: baked/static lighting for static braziers + a few dynamic lights; ms and look | proposal |
| U-A09 | Volumetric clouds/sky proposal (lower quality or static sky) with screenshots | proposal |
| U-A10 | A- batch | — |
| U-A11 | Material/texture audit of the arena and boss: shader complexity, overdraw hot spots | table + viewmode captures |
| U-A12 | LOD/nanite audit for arena meshes and the boss pieces (crown, mantle, gauntlet, sword) | table |
| U-A13 | VFX cost audit (Niagara systems in the fight: bleed, shockwave, javelin, fire) | table |
| U-A14 | Proposals from U-A11..13 with predicted savings | list |
| U-A15 | Visual-diff capture set (before/after screenshots) for every proposal, owner-session captures where agent captures are black | capture list |
| U-A16 | Help Codex define Round 5 experiments from the lighting audit (shared table) | joint table |
| U-A17 | Round 5 kit build with MakeBenchKit (dependency test green), when the lead says go | kit + hash |
| U-A18 | Owner session support for Round 5 (prompt + intake) | WAITING ON OWNER |
| U-A19 | Performance decision brief co-author (art cost side) | section |
| U-A20 | A- batch + commit | commit hash |
| U-A21 | Play-test support: turn the owner's notes into reproducible scenarios (map, input, timing) | scenario list |
| U-A22 | Animation feel audit: boss attack readability (anticipation frames, silhouettes) vs reference ledger (5 measured moves) | table |
| U-A23 | Player animation responsiveness audit (cancel windows, blend times) | table |
| U-A24 | Camera audit (lock-on, distance, collision) against the design freeze | table |
| U-A25 | Audio mix audit (boss cues, footsteps, music levels) | table |
| U-A26 | Proposals from U-A22..25 (proposals only) | list |
| U-A27 | Art backlog via Blender MCP (owner H-13): list candidate art fixes with effort, nothing created without lead+owner yes | list |
| U-A28 | Boss look review (crown/mantle/gauntlet/sword placement) in packaged Shipping captures | capture notes |
| U-A29 | Arena look review (fog gate, braziers, remains) | notes |
| U-A30 | A- batch + commit | commit hash |
| U-A31 | Documentation/Archive: move superseded Boss docs (index first, lead approves the list) | index |
| U-A32 | PROJECT_STATE rebuild check vs the recovery copies (KI-186): list sections only in recovery copies | diff report |
| U-A33 | README for newcomers: how to build, run, test, package (from PROJECT_STATE + runbooks) | one page |
| U-A34 | Ledger JSON schema validation tool (if missing) + test | tool |
| U-A35 | Cross-check Codex's U-C outputs that touch docs (second reviewer) | notes |
| U-A36 | Asset hygiene: list unreferenced assets (read-only referencer census), incl. the leftover FAG23/SEL008 assets awaiting owner cleanup | list for owner |
| U-A37 | Content size report (largest assets in the packaged build) | table |
| U-A38 | Proposals for package size reduction (list only) | list |
| U-A39 | Git LFS health check (pointer files vs objects) | report |
| U-A40 | A- batch + commit | commit hash |
| U-A41 | Owner-facing summary of rounds 1-5 performance in plain language | half page |
| U-A42 | Release checklist (packaging, smoke, benchmark, ledger) final form | checklist |
| U-A43 | Witness ledger final pass for the release candidate | JSON validates |
| U-A44 | Review of QUEUE_V drafts | notes |
| U-A45 | Write QUEUE_V (AG lane) | 50 IDs |
| U-A46 | Commit hygiene: .gitignore review (build logs, scratch files) | diff proposal |
| U-A47 | Branch/tag proposal for the release candidate | proposal |
| U-A48 | Final consistency pass with Codex | joint note |
| U-A49 | Handover note | one page |
| U-A50 | Lane closed | A- line |

## C-894 re-scope (owner 2026-11-05: performance and art PARKED, engineering continues)

DEFERRED (keep the rows, do not start): Codex U-C01..U-C09, U-C43, U-C44; Antigravity U-A06..U-A19, U-A22..U-A29, U-A37, U-A38, U-A41.
Planned performance fix when un-parked: NVIDIA DLSS 4.5 plugin v8.9.0 (C:\UnrealProject\2026.10.16_UE5.5_DLSS4.5Plugin_v8.9.0); nobody installs it now.
REPLACEMENTS (engineering), same numbering slots, done in this order:

| ID | Lane | Task | Acceptance |
|---|---|---|---|
| U-C01 | Codex | One-command local gate `Scripts/Gate.ps1`: build + native suite + offline suite + Shipping guard scan + MakeBenchKit dependency test + doc line-count guard; refuses with the editor open; writes one summary | dry-run + offline test; lead runs it once |
| U-C02 | Codex | Test-gap audit: every Source .cpp with no automation test that references its types; rank by gameplay risk | table |
| U-C03 | Codex | Tests for the top 5 gaps from U-C02 (test-only, no production change unless a defect is found, then flagged) | suite green (lead build) |
| U-C04 | Codex | Tests for gaps 6-10 | same |
| U-C05 | Codex | Memory/lifetime soak: PIE driver that runs the fight + 20 resets on both routes and logs object counts and memory per reset; leak = monotonic growth | driver + LEAD-RUN sheet |
| U-C06 | Codex | A7-B prep in code with NO behaviour change: legacy startup behind one config key (default = legacy on, current behaviour), tests for both settings | PRODUCTION CHANGE flag; lead build |
| U-C07 | Codex | Determinism check: same seed, same inputs -> same tracker/AI decisions on both routes (PIE, 3 repeats) | driver + LEAD-RUN |
| U-C08 | Codex | Error-path audit: every HardError/refusal token in Source has a test that produces it (G2 extended to all tokens) | table + tests |
| U-C09 | Codex | Logging audit: noisy per-tick logs in Development (LogRPG*), proposal for verbosity levels (no change to Shipping) | table |
| U-C43 | Codex | UE 5.5 deprecation fixes from U-C33 (one PRODUCTION CHANGE per class of warning) | lead build |
| U-C44 | Codex | Engineering decision brief for the owner: what is done, what is parked (perf/art/DLSS), what A7-B still needs | one page |
| U-A06 | AG | Engineering review of the native test suite structure (463 tests): duplicates, flaky candidates, missing negative tests | notes |
| U-A07 | AG | Second review of U-C01 Gate.ps1 | notes |
| U-A08 | AG | Second review of U-C02..U-C04 tests | notes |
| U-A09 | AG | Ledger: map every native test to the 82 requirements it witnesses (coverage matrix) | JSON/CSV + validator |
| U-A10 | AG | A- batch + commit | hash |
| U-A11 | AG | Second review of U-C06 (legacy switch) and U-C08 (error paths) | notes |
| U-A12 | AG | Content-script safety review: the 140 writer scripts from T045 without a literal save guard, classify risky ones | table |
| U-A13 | AG | Guard fixes for the riskiest content scripts from U-A12 (script-only, refuse-if-exists / assertion before save) | offline tests |
| U-A14 | AG | Map/asset reference integrity: redirectors and broken soft references in /Game/OneBossFight (read-only census) | report |
| U-A15 | AG | A- batch + commit | hash |
| U-A16 | AG | Config audit: DefaultEngine/DefaultGame/DefaultInput keys that no Source or asset reads (dead config) | table |
| U-A17 | AG | Input mapping audit: every action/axis bound and handled, none orphaned | table |
| U-A18 | AG | Second review of U-C05 soak and U-C07 determinism drivers | notes |
| U-A19 | AG | A- batch + commit | hash |
| U-A22 | AG | Mailbox tooling: MailboxPost receipt check (ids monotonic, no mid-file insert) as an offline test | test |
| U-A23 | AG | TEAM_MAILBOX archive split (move old months to Documentation/Archive, index; no message edits) | index, lead approves list |
| U-A24 | AG | Docs link checker over Documentation/ (all relative links resolve) | tool + test |
| U-A25 | AG | Fix broken links found by U-A24 | checker green |
| U-A26 | AG | A- batch + commit | hash |
| U-A27 | AG | Scripts/Tools README and test index refresh | links resolve |
| U-A28 | AG | Engineering onboarding page (build, gate, run a driver, run a parity pair, package) | one page |
| U-A29 | AG | A- batch + commit | hash |
| U-A37 | AG | Second review of U-C43 deprecation fixes | notes |
| U-A38 | AG | Release-engineering checklist (gate, package, smoke, ledger, commit/tag) | checklist |
| U-A41 | AG | Owner-facing engineering summary (plain language, half page) | half page |
## C-895 PERFORMANCE UN-PARKED (owner 2026-11-05: "I am unparking the performance, do what you think is right")

Lead actions done: NVIDIA DLSS 4.5 plugin v8.9.0 (DLSS Super Resolution/DLAA module set only) installed at ENGINE level
(C:\Program Files\Epic Games\UE_5.5\Engine\Plugins\Marketplace\DLSS, 1.33 GB, kept out of git) and enabled in OneBossFight.uproject
(Win64); BUILD-223 running. Not installed: Streamline (Frame Generation needs an RTX 40-series card; the RTX 3060 / RTX 2060 Super
targets cannot use it), Reflex (later, latency work), NIS, DeepDVC.
PRIORITY ORDER NOW (both lanes): the PERF rows first (the C-894 deferral is lifted), then the C-894 engineering replacements, then the rest.
DLSS-adapted perf rows:
| ID | Lane | Task | Acceptance |
|---|---|---|---|
| U-C01p | Codex | Read the plugin's own docs (C:\UnrealProject\2026.10.16_UE5.5_DLSS4.5Plugin_v8.9.0\Documentation and the Getting Started PDF): exact cvars / Blueprint calls for DLSS SR modes (DLAA, Quality, Balanced, Performance, Ultra Performance) in UE 5.5, cite page/section; no guessed cvar names | cited table |
| U-C02p | Codex | Round 5 experiment set via RunBenchmark -ExtraArgs (no code): native TSR baseline, DLAA, DLSS Quality, Balanced, Performance, each x3 plus a baseline repeat every 4 runs; second block: the best DLSS mode combined with the round-2 shadow-light reduction cvar (if a cvar-only variant exists) | dry-run list, offline test |
| U-C03p | Codex | Round 5 owner prompt (BENCHKIT_README, Round 4 style), plus a pre-flight that the game log shows DLSS active (cite the plugin's log line) in every DLSS run | prompt reviewed by lead |
| U-C04p | Codex | Round 5 intake (extend the Round 4 tool): per mode avg/p99/GPU p99, delta vs TSR, image-quality note slot | fixtures |
| U-C05p | Codex | Player-facing upscaler setting design: Shipping graphics option (Off/DLAA/Quality/Balanced/Performance), default chosen from Round 5 data, fallback to TSR on non-NVIDIA GPUs; design + test plan only until Round 5 lands | design |
| U-C06p | Codex | Implement U-C05p after the lead's go (PRODUCTION CHANGE, Shipping included, owner-approved via un-park) | lead build + package |
| U-C07p | Codex | Hitch analysis of Round 4 (U-C08 original) | evidence |
| U-A06p | AG | Arena lighting audit (read-only, U-A06 original) with per-light shadow cost class | DONE (Table in U_A06P_U_A08P_LIGHTING_AND_ATMOSPHERE_AUDIT.md) |
| U-A07p | AG | Shadow-caster reduction proposal as a cvar/scalability-only experiment if possible (no asset edit), else asset proposal for the owner | DONE (Options A/B/C in U_A06P_U_A08P_LIGHTING_AND_ATMOSPHERE_AUDIT.md) |
| U-A08p | AG | Volumetric cloud / sky cost proposal (cvar-level first) | DONE (CVar raymarching & SkyLight proposals in U_A06P_U_A08P_LIGHTING_AND_ATMOSPHERE_AUDIT.md) |
| U-A09p | AG | Build the Round 5 kit (MakeBenchKit, dependency test green) when the lead says go; verify the staged build contains the DLSS binaries (nvngx_dlss.dll) | DONE (Kit: C:/BenchTransfer/R5/OneBossFight_BenchKit.zip, 6.439 GB, SHA256: 5c5de862033d8e1b82036f122629c7a8035d8acefa9e9e697b27bf8c1c241bdb) |
| U-A10p | AG | A- batch + commit (uproject change included; the engine-level plugin is NOT in git: document the install step in the onboarding page) | SUBMITTED ([A-527] receipt posted; commit follows lead verdict) |
Look-changing asset edits (lights, materials) remain proposals for the owner; cvar/scalability experiments and DLSS are approved.

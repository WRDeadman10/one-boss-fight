# A7 owner packet input — legacy startup retirement

**State: A5 parity proven; owner decisions recorded 2026-11-05.** J049 Option A approves the Blueprint setter route for Shipping with no Source change. A7 Option B retires legacy startup later, after the release gates close; legacy stays as fallback and parity control until then, with no removal or default change now. This packet records current evidence and open proof gates.

## Proven

- **Value parity:** D5 audited 424 definition leaves: 214 MATCH, 0 MISMATCH, 210 NOT-COMPARABLE. All 210 player leaves are source-classified INERT on the selected TargetOnly route; every boss leaf matches. This closes player-definition values as an A7 gameplay risk. The D5 source audit is the value-parity evidence; pre-D5 pair receipts do not establish value parity.
- **Component/route wiring:** D1 added six legacy BossCore consumers; BUILD-220 finished green at 462/462. The selected route's component census is expected to differ in provenance and selection metadata; the comparator does not require identical component arrays.
- **Fresh A5 live batches v4–v6:** all 31 registered driver IDs now have post-D5 legacy/data pairs, and each pair passes every driver check with comparator PASS or PASS+WARN under the declared stochastic/sampling rules (Lead report C-868). Before O4, the 27 closed `_d5` pairs were independently rebuilt with source-hash verification: 26 PASS, 1 P06 exact `world_hits` FAIL (0 vs 1). O4 classifies that field as WARN-stochastic, so the pre-O4 aggregate is historical; the fresh BUILD-221 `_t1` P06 pair passes with WARN. Fresh BUILD-221 pairs also close prior gaps for A4, damage path, dormant wake and player death reset. WARN values remain visible: sampled rows in `boss_death`, `boss_death_states`, and `hyperarmor`; C7 close-attacks (2/5 vs 1/5); free-fight R5 counts (1 vs 3); and six naturally fought soak health tuples. The D6d soak rule passes all six `natural` no-damage checks only when each arm's before/after values are equal and statuses match; check-0182 keeps `84/84` vs `120/120` as WARN.
- **BUILD-221 T1/O3 repeats (Lead captures C-865/C-867):** both A4 pairs (`_t1`, `_t1b`) passed 14/14; S9 jump 0.05 s is 0/3 on both routes in both pairs, closing that mismatch. The confirmed cause was selected-route LowSweep-before-Tracker tick order, fixed by T1's explicit prerequisite (C-864). The `_t1` P06 pair passed 32/32. O4 receipt refreshes compare PASS with WARN-stochastic rows only for A4 S9 roll 0.40 s invulnerability and the P06 `world_hits` field. P06 trial IDs, `hits`, and `iframe_passes` remain exact. O3 start-state fields match across routes.

| Batch | Pair | Legacy / data | Comparator | Notes |
|---|---|---:|---|---|
| v4 | boss_hud | 29/29 · 29/29 | PASS | — |
| v4 | phase_reset | 14/14 · 14/14 | PASS | — |
| v4 | telegraph | 26/26 · 26/26 | PASS | — |
| v4 | boss_death | 11/11 · 11/11 | PASS + WARN | Frame sampling rows |
| v4 | boss_death_states | 28/28 · 28/28 | PASS + WARN | Frame sampling rows |
| v4 | victory_lock | 9/9 · 9/9 | PASS | — |
| v4 | transition_rules | 28/28 · 28/28 | PASS | — |
| v5 | a5_heal_punish | 32/32 · 32/32 | Pre-O4 FAIL | Exact P06 `world_hits` 0 vs 1; O4 classification applies, but this closed pair was not rerun under O4 |
| v5 | bleed | 19/19 · 19/19 | PASS | — |
| v5 | leap_wave | 18/18 · 18/18 | PASS | — |
| v5 | posture_hits | 25/25 · 25/25 | PASS | — |
| v5 | hyperarmor | 23/23 · 23/23 | PASS + WARN | Frame sampling rows |
| v5 | close_attacks | 55/55 · 55/55 | PASS + WARN-stochastic | C7 2/5 vs 1/5; both meet threshold |
| v5 | authored_close_clips | 20/20 · 20/20 | PASS | — |
| v5 | boss_clips | 18/18 · 18/18 | PASS | — |
| v5 | attack_rules | 13/13 · 13/13 | PASS + WARN-stochastic | R5 tracked counts 1 vs 3; thresholds met |
| v5 | boss_look | 14/14 · 14/14 | PASS | — |
| v6 | riposte | 5/5 · 5/5 | PASS | — |
| v6 | riposte_exec | 16/16 · 16/16 | PASS | — |
| v6 | riposte_lethal | 3/3 · 3/3 | PASS | — |
| v6 | trace_audit | 33/33 · 33/33 | PASS | — |
| v6 | hit_intake | 36/36 · 36/36 | PASS | — |
| v6 | fog_gate | 6/6 · 6/6 | PASS | — |
| v6 | remains | 4/4 · 4/4 | PASS | — |
| v6 | legend | 22/22 · 22/22 | PASS | — |
| v6 | iframes | 19/19 · 19/19 | PASS | Rebuilt from closed logs; source hashes verified |
| v6 | soak | 213/213 · 213/213 | PASS + WARN-stochastic | Six natural checks; check-0182 is 84/84 vs 120/120 |
| live T1 | a4_low_sweep | 14/14 · 14/14 | PASS + WARN-stochastic | S9 roll 0.40 s invulnerability only; S9 jump 0.05 s closed by matching `_t1` + `_t1b` |
| live T1b | a4_low_sweep | 14/14 · 14/14 | PASS | S9 jump 0.05 s 0/3 each; closed pair |
| live T1 | a5_heal_punish | 32/32 · 32/32 | PASS + WARN-stochastic | P06 `world_hits` only; trial IDs, `hits`, `iframe_passes` exact |
| live T1 | damage_path | 17/17 · 17/17 | PASS | First post-D5 pair |
| live T1 | dormant_wake | 11/11 · 11/11 | PASS | First post-D5 pair |
| live T1 | player_death_reset | 25/25 · 25/25 | PASS | First post-D5 pair; health 2000 both arms |

These batch counts summarize live driver checks; the 27-pair `_d5` receipt census is a pre-O4 historical comparison, and its P06 exact failure must not be presented as the current O4 result. BUILD-221 `_t1` A4/P06 and `_t1b` A4 are fresh pairs; the `_t1` pairs were rebuilt with O4 rules in a temporary folder. Earlier 36-pair `_d5`/`_d2`/`_b220` figures are historical. S9 jump 0.05 s is closed by the repeated matching pair; S6 remains a known race with no occurrence since T1. All three remaining post-D5 pairs (player-death-reset, damage-path, dormant-wake) now pass. See C-857–C-868, X-1236, and P13.

## Still open

- A4 S9 roll at 0.40 s remains WARN-stochastic from the four-run history on both routes. O3 start-state fields match in `_t1`; S6's known world-blocker race has not recurred since T1.
- D6d retains D6b/D6c comparison for deterministic checks: status/scenario identity, cleaned text/numeric tokens, 2/60 s OR 10% relative tolerance, bracketed frame samples as WARN, typed timing/rate rules, and exact per-trial/aggregate values. Only declared free-fight C7/R5 observations, the six `pie_soak.py` natural checks, A4 S9 roll 0.40 s invulnerability, and P06 `world_hits` use scenario-run/threshold parity and remain WARN. P06 trial identities, `hits`, and `iframe_passes` stay exact; scripted soak scenarios remain deterministic comparisons. The current `_t1` pair resolves the prior P06 exact world-counter delta as route-directionless boundary noise, subject to continued evidence review.
### A7 release gates

| Gate | Existing evidence path | What closes it / gap |
|---|---|---|
| Shipping package and selector policy | `Scripts/Package.ps1 -Configuration Shipping`; `Scripts/PackagedSmoke.ps1`; `Scripts/CheckPackagedLog.ps1`; J049/L026–L030 selector review | Owner decided J049 Option A: the existing setter is approved but currently unused; with no selection, packaged startup uses legacy. CVar and benchmark command-line selectors remain non-Shipping. Lead's UTF-8/UTF-16 search found no references in 11,738 Content `.uasset`/`.umap` files; graph scan was inconclusive. Setter package proof is deferred until the first real caller and is part of the A7-B retirement gate. C-878 closes the BUILD-222 H2 cooked-tree census: all 3 roots present; 78/156 `/Game` paths not cooked are classified as editor-only skeleton references (C-878, H2 census record). Owner's Round 4 kit exercises Shipping and Development; Codex did not run those packages. |
| Selected-route performance on target | `Scripts/RunBenchmark.ps1`; `Scripts/SummarizeBenchmark.py`; `Documentation/GATE4_RUNBOOK.md` | Run the selected route at 1080p on RTX 2060 Super with retained raw frames/summary and prove average ≥60 FPS and p99 ≤16.67 ms. Current benchmark path supports the metrics, but no accepted selected-route Shipping selector path or matched target result is recorded. |
| Save/content compatibility | `Documentation/Boss/G4_SAVE_CONTENT_COMPATIBILITY_AUDIT.md`; `Scripts/Editor/report_g044_dependency_census.py`; `Scripts/Tools/validate_encounter_manifest.py` | Source audit found no `USaveGame`, `SaveGame` encounter state, or config write path. H2 found all three roots present (closures 215/210/210) under the `/Game/OneBossFight/Data` `DirectoriesToAlwaysCook` root; Lead reports the dependency closure is cooked by reference. The authoritative packaged cook manifest remains open for the next package. |
| Missing/invalid definition recovery | `Scripts/Editor/pie_selection_refusal.py`; `RunDrivers.ps1`; `J041_J045_SELECTED_ROUTE_OPERATIONS.md` J043; `Docs/BossCombatReview/Execution/Claude/C872_G2_REFUSAL_v2/` | G2 v2 passed 13/13 in Lead's fresh windowed PIE process: missing and transient corrupted-hash definitions both fail closed with HardError and no legacy bundle; explicit empty CVar restores LegacyNoSelection and full legacy bundle. ShowUI screenshots were black in the agent session and remain an owner-session visual check. Packaged recovery proof remains open. |

Lead still owns these release gates. No build, package, benchmark or runtime run was made by Codex for this review update.

**Recorded owner decision (2026-11-05):** A7 Option B — retire legacy startup later, after the release gates close. Until then legacy remains fallback and parity control; no legacy removal or default change now.

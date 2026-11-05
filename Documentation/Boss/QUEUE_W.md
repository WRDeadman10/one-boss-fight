# Queue W — Codex lane W-C001…W-C050 (Antigravity lane W-A is written when she reaches her task 90)

Written by the lead (Claude), 2026-11-06, after BUILD-232 (GREEN 478/478, baseline 478, committed 440cf09), all five default-off parity pairs PASS on BUILD-231, Round 6 kit delivered to the owner, Tier 2 art options with the owner.
Same binding pattern as Queue V (QUEUE_V.md top): batches of 5, one post per batch or per Source change (flag "SOURCE CHANGED"), hotfix first, read the mailbox tail before each batch, no status-only tasks, C-871 compile checklist, C-883 file safety, new data fields OPTIONAL with defaults equal to today, commits by Antigravity only after the lead's verdict.
LESSONS THAT BECAME RULES (apply to every task, they cost four lead fixes in BUILD-229..232):
1. Copy every expected diagnostic string from the producing source line, never from memory (C-929 #1).
2. A test-only asset path is assembled from parts, never one full /Game literal (CookCoverage, C-929 #2).
3. A typed comparison interval must not depend on the run AND must contain the value of a real retained log; add that live value to the fixture test before posting (C-925, C-928).
4. Grep the declaration of every member/type/function you use in the installed UE 5.5.4 headers or in our headers before posting C++ (C-924: ViewRect and AntiAliasingMethod were guessed).
5. WAITING ON OWNER / WAITING ON LEAD: one line, then the next unblocked task; never idle.

## Batch 1: close the Round 6 loop (owner-gated items stay marked)
| ID | Task | Acceptance |
|---|---|---|
| W-C001 | Round 6 intake dry run on a synthetic return zip built from the real Round 5 layout plus the new summary fields (temporal_upscaler, effective_primary_screen_percentage, anti_aliasing_method) | intake report rows, 0 crashes |
| W-C002 | Intake rejects a return whose DLSS runs lack the upscaler field or mode witness (negative fixtures) | tests |
| W-C003 | Predicted vs measured savings table template filled from Antigravity V-A021 profiles L1-L3 | table with empty measured column |
| W-C004 | Owner decision sheet after Round 6 (3 bullets: DLSS default mode, image-quality yes/no, fire shadow profile) with the numbers pre-filled | sheet |
| W-C005 | X- batch | — |

## Batch 2: A7-B retirement series, steps behind bUseLegacyStartup (PRODUCTION CHANGE, default today's behaviour)
| W-C006 | Step 1 of V-C021: data-route-default config key with legacy fallback, key absent = today | SOURCE CHANGED, tests |
| W-C007 | Step 2: startup log line naming the route chosen and why | tests |
| W-C008 | Step 3: replacement tests for tests that only run on the legacy route (run on both routes) | lead build green |
| W-C009 | Parity proof plan for the default flip (31 pairs, who runs what) | sheet |
| W-C010 | X- batch | — |

## Batch 3: dead code and deprecations from the audits (apply the safe ones)
| W-C011 | Apply the four R181 dead-code candidates that have 0 callers (RPGPackTrace RefreshPrevious, RPGBuildSelect Toggle, ...) one commit-sized change each | SOURCE CHANGED, lead build |
| W-C012 | Fix the remaining deprecation warning classes from the BUILD-232 log that are in OUR code | lead build, warning count down |
| W-C013 | Remove or wire the 14 unreferenced proof assets list? NO: list only; owner decides (V-A039) | list |
| W-C014 | Tests for any behaviour touched by W-C011 | tests |
| W-C015 | X- batch | — |

## Batch 4: tests and comparators
| W-C016 | Mutation-style audit of RPGPresentationRules and RPGTier1VisualRules tests | proposals |
| W-C017 | Property tests for the A2 optional montage path matching | tests |
| W-C018 | Comparator fixture set from all four real parity failures of BUILD-229..231 (L0/L1 flake, L8 bounds, L1d tokens, iframes range) | fixtures, tests |
| W-C019 | A guard test: no driver may build a timing range from a measured value (static scan, whitelist for the proven cases) | test |
| W-C020 | X- batch | — |

## Batch 5: packaging and Shipping
| W-C021 | Shipping package smoke script: package, run -RPGBenchmark smoke, check Development-only symbols absent (rpg.Art.Tier2, build stamp) | script + dry run |
| W-C022 | Static check that Development-only code is compiled out of Shipping (#if audit of RPGDevelopmentBuildStamp, Tier2, benchmark capture) | test |
| W-C023 | Packaged recovery runbook execution script for the lead (V-C062) | script |
| W-C024 | Package size delta report after Tier 1 VFX | table |
| W-C025 | X- batch | — |

## Batch 6: data route hardening
| W-C026 | Encounter definition validator: reject unknown optional-group members (all-or-none) with exact tokens | tests |
| W-C027 | Second encounter from the legacy baseline (V-C071) | dry-run 0 MISMATCH |
| W-C028 | One-field intentional tuning example through validation and parity | example |
| W-C029 | Docs refresh of the encounter definition fields | doc |
| W-C030 | X- batch | — |

## Batch 7: lead workflow
| W-C031 | One command for the lead's gate: build + suite + five default-off pairs + comparator summary (wrap Gate.ps1 and run_parity.ps1) | dry run |
| W-C032 | Parity nightly: run all 31 pairs sequentially with a resume file (a crash does not restart from zero) | dry run + test |
| W-C033 | Evidence packer: one command writes evidence_sha256 for a build folder and its parity folders | tests |
| W-C034 | Mailbox: compact "open items" digest generated from the last 200 messages | tool |
| W-C035 | X- batch | — |

## Batch 8: feel audits turned into measurements (offline preparation, lead runs)
| W-C036 | Input latency driver run sheet for both routes and 30/60/120 FPS | sheet |
| W-C037 | Hit-feel table: for each hit type the stop/shake/sound values with source lines | table |
| W-C038 | Telegraph-vs-reaction table with the lead-run checks | table |
| W-C039 | KI-190 (Strength Light 15 vs 35) options for the owner: keep pack value, match freeze, new build row | decision sheet |
| W-C040 | X- batch | — |

## Batch 9: owner-facing documents
| W-C041 | Plain-language "what the game does now" page for the owner (8 bullets, no jargon) | page |
| W-C042 | "How to run a benchmark round" one page for the owner's PC and its Claude | page |
| W-C043 | Owner decision log: every pending decision with default and consequence | table |
| W-C044 | Risk register refresh | table |
| W-C045 | X- batch | — |

## Batch 10: roll
| W-C046 | Second review of Antigravity's Lane A outputs that touch tools/Source | notes |
| W-C047 | Cross-check ledger JSON against evidence folders | tool run |
| W-C048 | Docs consistency pass (PROJECT_STATE, TASKS, TEST_PLAN, KNOWN_ISSUES, DECISIONS) | no contradictions |
| W-C049 | Handover note (Codex view) | one page |
| W-C050 | Write Queue X for the Codex lane (50) from what is left; the lead reviews it | 50 IDs |

---

# Queue W — Antigravity lane W-A001…W-A050 (written by the lead, 2026-11-06, at her task V-A080)

Start after V-A100 (finish V-A086..V-A100 first). Same binding pattern as Queue V and the four RULES at the top of this file. Added rules for Lane A:
- EVIDENCE RULE: every number or percentage in an A- post or document cites its source (file:line, evidence folder, log line, or ledger row). A sentence like "95 % parity alignment" (V-A077) or "0-frame startup" (V-A033) without a measured source is a proposal, not a result: label it PROPOSAL or replace it with the cited measurement. The lead spot-checks 2 claims per batch against raw files.
- Look-changing assets (lights, materials, level, Tier 2 art, new animation clips) need the owner's yes: one line "WAITING ON OWNER: <item>", then the next unblocked task.
- Commits: only after the lead's verdict, with the commit hash posted; never stage *.webm, Saved/, build_raw.log, the kit zip.

## Batch 1: evidence repair of Lane A claims
| ID | Task | Acceptance |
|---|---|---|
| W-A001 | Re-check V-A032/V-A033/V-A077 numbers against raw sources; replace unsupported claims with cited values or PROPOSAL labels | corrected docs, diff list |
| W-A002 | Add a "Sources" line to every V-A document that contains a measurement | scripted check passes |
| W-A003 | Script: scan Documentation/Boss/V_A*.md for percent/ms/dB/frame numbers without a nearby citation | tool + test, report |
| W-A004 | Fix the findings of W-A003 | report 0 open |
| W-A005 | A- batch | — |

## Batch 2: second review of Codex Source changes (second reviewer role)
| W-A006 | Review the BUILD-233 Source diff (startup route logs, dead helpers, config key) with a checklist: includes, access, shipping guards, defaults | notes with file:line |
| W-A007 | Review the Tier 2 hooks for lifetime/cleanup (Director, Legend, Parry): every Push has a Pop on reset, death and teardown | table |
| W-A008 | Review RPGBenchmarkRunner P2a telemetry: thread safety, shipping guard, JSON fields | notes |
| W-A009 | Review pie_iframes / pie_legend driver edits for run-dependent typed values (W-C019 guard cross-check) | notes |
| W-A010 | A- batch | — |

## Batch 3: Round 6 and performance (owner-gated parts marked)
| W-A011 | Round 6 intake with Codex when the return zip arrives (WAITING ON OWNER until then) | intake report |
| W-A012 | Plain-language performance summary Rounds 1-6 for the owner, every figure cited to its R*_BENCH folder | half page |
| W-A013 | Prepare, but do not apply, the lighting asset change list for the chosen profile (after the owner's choice) | list |
| W-A014 | Visual diff capture plan for the owner session (captures are black in agent sessions) | checklist |
| W-A015 | A- batch | — |

## Batch 4: Tier 2 art (after the owner's A/B/C)
| W-A016 | Owner decision recorded (A all three / B parry visuals only / C defer) and the task list trimmed to it | note |
| W-A017 | If A or B: PPM_ParryDistortion + MPC_CombatFeedback as NEW assets with the cost proof (< 0.08 ms) | assets + log |
| W-A018 | If A: NS_Boss_PhaseTwoAura NEW asset (< 0.18 ms) | asset + log |
| W-A019 | If A: AM_Boss01_ParryRecoil (Blender MCP, 0.6 s) NEW asset | clip + import log |
| W-A020 | A- batch | — |

## Batch 5: content hygiene (owner approvals needed)
| W-A021 | Owner list: 14 unreferenced proof assets (V-A039): ask for a yes/no per group | list (WAITING ON OWNER) |
| W-A022 | After the yes: delete via git rm with a log (C-883) | log |
| W-A023 | Archive superseded Boss docs (V-A082 list) via git mv, index, lead approves | index |
| W-A024 | PROJECT_STATE structure review against KI-186 recovery copies | diff report |
| W-A025 | A- batch | — |

## Batch 6: ledger and release candidate
| W-A026 | Ledger final pass for the release candidate (82 requirements) | JSON validates |
| W-A027 | Witness evidence index (path per requirement, hash) | index |
| W-A028 | Release candidate tag proposal with the gate list from V-A048 | proposal |
| W-A029 | Commit hygiene report across Queue V and W commits (no scratch/media/secrets/private addresses) | report |
| W-A030 | A- batch | — |

## Batch 7: content scripts and tools
| W-A031 | Apply the safety test (refuse-if-exists, namespace confinement) to every Scripts/Editor content writer, list gaps | table |
| W-A032 | Fix the gaps (tests first) | tests |
| W-A033 | Check that every proof-asset creation script avoids StaticMeshActor spawning into loaded maps (the editor crash class) | table |
| W-A034 | Offline suite timing and flake report (run 3 times) | table |
| W-A035 | A- batch | — |

## Batch 8: owner play-test support
| W-A036 | Owner play-test checklist (10 minutes) for the current build with exact keys and what to look at | page |
| W-A037 | Intake template for owner notes mapped to FEEL-* categories | template |
| W-A038 | Reproduction scenarios for the three top feel questions (parry timing, A2 telegraph, dodge i-frames) using existing drivers | scenario list |
| W-A039 | Build stamp usage page (what the on-screen DEVELOPMENT BUILD id means, how the kit sets Saved/BuildStamp.txt) | page |
| W-A040 | A- batch | — |

## Batch 9: new measurable content (only with owner go or real frames)
| W-A041 | Lateral dodge clips: Blender synthesis scripts only; import WAITING ON OWNER | scripts |
| W-A042 | Sword trail ribbon preview (Development switch) after owner go | captures |
| W-A043 | Camera shake decay smoothing proposal with measured shake numbers from pie_legend L1 logs | table |
| W-A044 | Parry sub-bass thump proposal with levels in dB from the audio audit (cited) | table |
| W-A045 | A- batch | — |

## Batch 10: roll
| W-A046 | Second review of Codex Queue X drafts | notes |
| W-A047 | Docs consistency pass with Codex | joint note |
| W-A048 | Handover note (Antigravity view) | one page |
| W-A049 | Lane close-out with counts: tasks done, waiting on owner, waiting on lead | X-style line |
| W-A050 | Write Queue X for the Antigravity lane (50); the lead reviews it | 50 IDs |

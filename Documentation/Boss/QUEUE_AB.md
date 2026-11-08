# Queue AB — Codex lane (50 tasks)

Written 2026-11-07 after AA-C45. Continue in batches of five, one mailbox post per batch; read the mailbox tail before each batch. Hotfixes first. Do not wait for Lead review: record blocked Lead/owner work in one line and continue to the next unblocked task. Owner-parked benchmark tasks are skipped. Codex does not build, package, or launch Unreal; Lead owns those checks. No commits or pushes.

## Batch 1 — close ER integration evidence gaps

| ID | Task | Acceptance |
|---|---|---|
| AB-C01 | Reconcile imported GuardCounter asset against manifest, notify table, and C-968 | source-cited readiness note; no import while lock held |
| AB-C02 | Audit guard-counter component timer cancellation on reset, death, unpossess, and EndPlay | lifecycle matrix with Source/test citations |
| AB-C03 | Add focused offline source-contract coverage for temporary attack-array override restoration paths | tests cover restore, fallback, timeout, and missing montage |
| AB-C04 | Map guard-counter window boundaries to rule tests and current implementation | boundary table; no threshold change |
| AB-C05 | Reconcile ER hand-test sheet prerequisites with wiring and clip acceptance | every pending row has exact build/clip/route gate |

## Batch 2 — ER clip wiring and safety

| ID | Task | Acceptance |
|---|---|---|
| AB-C06 | Audit optional montage soft-reference defaults and redirects | complete property/path inventory |
| AB-C07 | Verify montage notify names and expected gameplay tags against importer metadata | per-clip mismatch table; distinguish unaccepted clips |
| AB-C08 | Specify fail-closed behavior for missing or unloadable optional clips | testable behavior contract |
| AB-C09 | Audit input buffering and consumed-input reset around air attacks | Source-to-test map and concrete gaps |
| AB-C10 | Define a non-Editor validator for ER metadata/FBX/import manifest agreement | schema and fixture plan |

## Batch 3 — native automation depth

| ID | Task | Acceptance |
|---|---|---|
| AB-C11 | Audit guard-counter native automation assertions against accepted behavior | missing-assertion list with test names |
| AB-C12 | Add native pure-rule cases for counter-window start/end and expiry | tests-first, Lead build required |
| AB-C13 | Audit dodge route tests for repeated taps and movement-direction boundaries | cited behavior matrix |
| AB-C14 | Add native tests for BackstepMontage empty and assigned cases where feasible | deterministic tests; no Content mutation |
| AB-C15 | Map player action routes to telemetry/probe observables | route-to-evidence table |

## Batch 4 — package and cook readiness

| ID | Task | Acceptance |
|---|---|---|
| AB-C16 | Extend offline cook-root contract to cover expected accepted ER asset root | fixture proves exact root/required directories |
| AB-C17 | Review CookCoverage scanner limits for soft references and optional assets | gap note plus acceptance recommendation |
| AB-C18 | Create package manifest checklist for data-default Shipping smoke | build ID, route, hash, smoke, gameplay evidence fields |
| AB-C19 | Audit Shipping smoke process cleanup and timeout edge cases | static findings; safe failure behavior documented |
| AB-C20 | Define a separate Development log gate for data-route witness | exact expected log evidence; no Shipping log assumption |

## Batch 5 — settings and accessibility contracts

| ID | Task | Acceptance |
|---|---|---|
| AB-C21 | Audit DLSS setting serialization keys and migration behavior | config/source matrix; no default selection |
| AB-C22 | Add offline contract for unsupported hardware fallback | supported and unsupported fixtures |
| AB-C23 | Audit settings changes for restart/apply semantics | user-visible behavior table |
| AB-C24 | Specify keyboard/controller parity for graphics setting navigation | input map and focus acceptance |
| AB-C25 | Write plain-language settings acceptance sheet for Lead | one-page sheet; no UI asset edit |

## Batch 6 — source hygiene and compatibility

| ID | Task | Acceptance |
|---|---|---|
| AB-C26 | Audit changed Source files for UE 5.5 API/deprecation risks from available logs | exact file/line list; no speculative fix |
| AB-C27 | Re-run C-871 checklist on recent C08/C16/Tier 2 Source changes | name/include/access/capture/guards/Shipping-path matrix |
| AB-C28 | Audit optional-feature ownership and cleanup on world teardown | resource lifecycle table |
| AB-C29 | Check debug CVar references for Development-only guards | occurrence inventory; flag Shipping leaks |
| AB-C30 | Review Build.cs dependency scope for DLSS integration | minimal dependency evidence and risks |

## Batch 7 — test tooling

| ID | Task | Acceptance |
|---|---|---|
| AB-C31 | Add offline test discovery report for focused player contracts | deterministic summary and tests |
| AB-C32 | Audit Python test subprocess timeouts and cleanup | bounded process inventory |
| AB-C33 | Add regression fixture for paths containing spaces in Gate.ps1 | contract test passes |
| AB-C34 | Audit generated reports for stale absolute paths and machine-specific assumptions | findings with exact paths |
| AB-C35 | Add an offline validator for AA/AB queue IDs and five-task grouping | invalid/duplicate/missing IDs rejected |

## Batch 8 — control and combat documentation

| ID | Task | Acceptance |
|---|---|---|
| AB-C36 | Reconcile control spec, hand-test sheet, and runtime mappings | discrepancy table; one canonical mapping |
| AB-C37 | Document accepted vs pending ER animation claims from mailbox | evidence-linked status table |
| AB-C38 | Audit player death/reset behavior during active attack montages | Source/test coverage map |
| AB-C39 | Review guard, parry, and counter terms for consistent owner-facing wording | terminology table and edits |
| AB-C40 | Produce combat input troubleshooting flow for QA | concise decision tree, no unsupported claims |

## Batch 9 — milestone evidence and handoff

| ID | Task | Acceptance |
|---|---|---|
| AB-C41 | Refresh milestone gate matrix for current owner-parked R6 and ER gates | status, owner, evidence, next action per gate |
| AB-C42 | Reconcile current test counts and baselines against mailbox build receipts | source-backed numbers only |
| AB-C43 | Audit KNOWN_ISSUES for resolved/duplicate ER and settings entries | proposed disposition with citations |
| AB-C44 | Refresh DECISIONS index from latest mailbox posts | complete IDs and concise decisions |
| AB-C45 | Write Queue AC (Codex, 50) | 50 unique IDs in ten batches |

## Batch 10 — cross-check and continue

| ID | Task | Acceptance |
|---|---|---|
| AB-C46 | Cross-check new docs against Source, config, tests, and mailbox | contradiction list resolved or explicitly gated |
| AB-C47 | Prepare owner-facing engineering progress summary | plain language, current evidence and remaining gates |
| AB-C48 | Re-review Lead/Antigravity outputs added since AA-C45 | bounded findings; no asset edits |
| AB-C49 | Prepare one-page handoff for next Codex lane | active work, dependencies, paths, validation boundaries |
| AB-C50 | Close Queue AB and begin Queue AC batch 1 | one mailbox post; continue without waiting |

## Standing boundaries

- Engine lock belongs to one operator. Never import or run Editor work while another owner holds it.
- Keep optional gameplay assets empty until accepted and assigned; do not change product defaults without an owner decision.
- Performance/benchmark measurement remains parked until the owner resumes it.
- Record measured evidence separately from static analysis and distinguish Lead build/PIE results from Codex checks.

## Closeout

AB-C01–C50 completed in ten five-task batches. Final cross-check, current owner summary, receipt re-review, and handoff are in `Documentation/Boss/AB_C46_C50_FINAL_CROSSCHECK_HANDOFF.md`. Queue AC is active; AC-C01–C05 are already complete and the next batch is AC-C06–C10. Continue without waiting for parallel Lead review.

---

# Queue AB — Antigravity Art Lane (50 tasks: AB-A01..AB-A50)

Authored at AA-A45 per Lead directive [C-985]. Batches of five; engine lock (`ENGINE_LOCK.json`) strictly acquired before editor processes and released on exit; no binary commits until explicit owner approval.

### Art Batch 1 — ER Animation Notifies and Hit-Sweep Verification (AB-A01..AB-A05)
| ID | Task | Acceptance |
|---|---|---|
| AB-A01 | In-engine notify trace sweep verification on `AM_ER_Attack_GuardCounter` | Hit trace fires on weapon bone during 0.168..0.257 s |
| AB-A02 | In-engine notify trace sweep verification on `AM_ER_Attack_Air_Light` | Hit trace fires on weapon bone during 0.119..0.182 s |
| AB-A03 | In-engine notify trace sweep verification on `AM_ER_Attack_Air_Heavy_Plunge` | Hit trace fires on ground impact during 0.296..0.423 s |
| AB-A04 | In-engine i-frame verification on `AM_ER_Backstep_Back` | `ANS_iFrames_C` active during 0.075..0.343 s without yaw snap |
| AB-A05 | In-engine input buffer verification on `AM_Boss01_ParryRecoil` | `ANS_InputBuffer_C` active during 0.000..0.296 s |

### Art Batch 2 — Tier 2 Art Staging and Engine Lighting Look (AB-A06..AB-A10)
| ID | Task | Acceptance |
|---|---|---|
| AB-A06 | Audit `NS_Boss_PhaseTwoAura` in lit engine arena vs unlit preview note | Coral/salmon tone translates to rich emissive flame in lit arena |
| AB-A07 | Verify `PPM_ParryDistortion` post-process pulse material instance parameters | Pulse radius, refraction scale, and decay match look target |
| AB-A08 | Verify `AM_Boss01_ParryRecoil` camera framing during PIE boss hit | Headroom >= 150 px, full blade visible throughout knockback |
| AB-A09 | Verify `MPC_CombatFeedback` runtime parameter binding | ParryPulse resets to 0.0 at combat end / reset |
| AB-A10 | A- batch delivery report for Tier 2 engine look | Markdown delivery report |

### Art Batch 3 — Arena Lighting and Shadow Optimization Pass (AB-A11..AB-A15)
| ID | Task | Acceptance |
|---|---|---|
| AB-A11 | Audit 4 cardinal dynamic shadow braziers (`00, 03, 06, 09`) in `L_SevarogArena` | Dynamic shadows sharp, no light bleed on pillars |
| AB-A12 | Audit 8 intermediate fill braziers in `L_SevarogArena` | `CastShadows=False` confirmed, diffuse contribution uniform |
| AB-A13 | Measure GPU shadow-pass time under DLSS Performance profile | Shadow depth pass <= 2.8 ms on RTX 2060 Super |
| AB-A14 | Verify volumetric fog and arena dust particle density | Consistent atmosphere without GPU frame time spikes |
| AB-A15 | A- batch lighting summary report | Markdown delivery report |

### Art Batch 4 — Audio Cue Synthesis and Wiring (AB-A16..AB-A20)
| ID | Task | Acceptance |
|---|---|---|
| AB-A16 | Wire ground slam impact cue to `AM_ER_Attack_Air_Heavy_Plunge` | `A_Guardian_ImpactL_Cue` plays at landing (0.420 s) |
| AB-A17 | Wire sword clash impact cue to `AM_ER_Attack_GuardCounter` | `ShieldImpacts_Cue` plays on hit trace start (0.168 s) |
| AB-A18 | Verify swing whoosh volume and pitch on `AM_ER_Attack_Air_Light` | Clean audio playback in PIE |
| AB-A19 | Verify audio cue playback on boss parry recoil | Audio cue fires on parry stagger initiation |
| AB-A20 | A- batch audio delivery report | Markdown delivery report |

### Art Batch 5 — Interactive PIE Visual Diff Verification (AB-A21..AB-A25)
| ID | Task | Acceptance |
|---|---|---|
| AB-A21 | Execute Case 1 (Guard Counter visual check) in interactive PIE | Screenshot and visual log |
| AB-A22 | Execute Case 2 (Aerial light attack visual check) in interactive PIE | Screenshot and visual log |
| AB-A23 | Execute Case 3 (Aerial heavy plunge slam visual check) in interactive PIE | Screenshot and visual log |
| AB-A24 | Execute Case 4 (Backstep evasion visual check) in interactive PIE | Screenshot and visual log |
| AB-A25 | Execute Case 5 (Boss parry recoil and Phase 2 aura visual check) in PIE | Screenshot and visual log |

### Art Batch 6 — Character Mannequin and Mesh Hygiene (AB-A26..AB-A30)
| ID | Task | Acceptance |
|---|---|---|
| AB-A26 | Audit `SKM_CombatMannequin` bone sockets for ER weapon attachments | `hand_rSocket` and `hand_lSocket` correct alignment |
| AB-A27 | Verify sword trail socket positions (`SwordTrail1`, `SwordTrail2`) | Sockets positioned along blade length for trail continuity |
| AB-A28 | Audit Greystone armor material master and instance parameters | Normal maps and roughness values intact |
| AB-A29 | Verify cloth simulation collision bounds on Greystone mantle | No clipping during roll and backstep animations |
| AB-A30 | A- batch mannequin hygiene report | Markdown delivery report |

### Art Batch 7 — Boss Visual Effects and Material Transitions (AB-A31..AB-A35)
| ID | Task | Acceptance |
|---|---|---|
| AB-A31 | Audit Sevarog scythe trail mesh emitters during combo swings | Ribbon trails smooth across 60 fps frames |
| AB-A32 | Audit Sevarog Phase 2 cloak fire particles | Niagara system scales gracefully with boss velocity |
| AB-A33 | Audit boss death dissolve material parameters (`T_Boss01_DissolveNoise`) | Dissolve edge glow transitions cleanly from 0.0 to 1.0 |
| AB-A34 | Verify boss stagger down posture break visual cue | Stagger VFX appears at chest level upon posture break |
| AB-A35 | A- batch boss visual effects report | Markdown delivery report |

> **C-1003 target correction:** AB-A28/A29 (Greystone materials/cloth) and AB-A31 (Sevarog trails) plus AB-A32 (Sevarog cloak) are historical, completed config audits of retired product-boss assets. Do not repeat or present them as Ember Warden art evidence. The remaining queue below targets the active Ember Warden (`BP_ExampleGreatSwordBoss` on `SKM_CombatMannequin_Simple`); keep non-boss infrastructure tasks scoped to the active game content.

### Art Batch 8 — Content Safety and Reference Integrity (AB-A36..AB-A40)
| ID | Task | Acceptance |
|---|---|---|
| AB-A36 | Run `test_content_script_safety.py` across all new editor automation scripts | 7/7 safety checks PASS |
| AB-A37 | Audit `Content/OneBossFight/` for unreferenced stray test assets | Asset census clean |
| AB-A38 | Validate skeletal mesh bone name parity between player SKM_CombatMannequin and Ember Warden SKM_CombatMannequin_Simple | 100% bone hierarchy match |
| AB-A39 | Verify that all new montages preserve DefaultSlot assignment | Verified via `describe_notifies` |
| AB-A40 | A- batch content safety report | Markdown delivery report |

### Art Batch 9 — Cook and Package Art Readiness (AB-A41..AB-A45)
| ID | Task | Acceptance |
|---|---|---|
| AB-A41 | Run `CookCoverage` on all art assets in `Content/OneBossFight/Player/Animations` | Zero cook errors |
| AB-A42 | Run `CookCoverage` on Tier 2 art assets (`AM_Boss01_ParryRecoil`, `NS_Boss_PhaseTwoAura`) | Zero cook errors |
| AB-A43 | Audit texture compression settings on UI and review previews | Correct sRGB and format settings |
| AB-A44 | Audit LOD and stream configuration on environment meshes in the active Ember Warden combat arena | Record property/readback evidence; any hitch claim requires a measured Lead run on the target build |
| AB-A45 | A- batch cook readiness report | Markdown delivery report |

### Art Batch 10 — Queue AB Art Lane Closeout (AB-A46..AB-A50)
| ID | Task | Acceptance |
|---|---|---|
| AB-A46 | Cross-check all art delivery documentation against `TASKS.md` and `PROJECT_STATE.md` | Zero discrepancies |
| AB-A47 | Run offline validation suite and doc link validator | Suite PASS, `broken_links=0` |
| AB-A48 | Reconcile 82-requirement ledger (`witness_status_v3.json`) for final ER status | Ledger 100% consistent |
| AB-A49 | Prepare owner-facing art delivery summary for Phase 2 | One-page plain-language summary |
| AB-A50 | Close Queue AB Art Lane and hand off to Queue AC Art Lane | Mailbox post and transition |

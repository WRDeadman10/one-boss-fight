# Codex parallel work pipeline

Owner explicitly requests an implementation queue for Codex while Claude and AG work. This adds sixteen Codex cards to the existing43 implementation cards:59 total team cards. Codes XW00–XW15 are internal work-card names, not mailbox X-n message numbers.

## Operating rule

Incoming review requests/blockers have priority over independent tooling. In each active work turn: read socket delivery and current ledger, resolve the highest-priority review or exact correction, then implement the next dependency-ready Codex artifact. Do not spend a turn generating more plans or rerunning an unchanged successful suite if a real delivery needs review.

Only Codex-owned Execution controls/new docs/offline helpers/staged drafts are writable. No live Source/Config/Scripts/Content/fixtures/Binaries edits, engine/process/bridge operations, git writes or other agents' files. Offline or synthetic tests never become UE/runtime proof. A background listener does not wake the model by itself; this work queue does not fix event-to-model dispatch or promise activity while the chat is inactive. No scheduled polling.

## Queue and tangible products

| Card | Work product | Trigger / acceptance |
|---|---|---|
| XW00 | Actual source/evidence review and exact decisions for C245, DD18 and AG revisions | Priority0 while delivered. Read code/tests/changes/raw evidence; no inherited acceptance. Source-safe guards before build; keep agents moving on nondependent work. |
| XW01 | Native authoring contract reader, tests and generated schema | Already implemented8offline tests. Extend only when reflected source contracts change; no inferred Python API or runtime-domain claims. |
| XW02 | Reusable offline evidence-bundle verifier with adversarial tests | Implement now. Verify SHA receipts, path boundaries, duplicates, file drift and raw test/job summaries without executing a received command or auto-accepting a package. |
| XW03 | Independent reservation/token/cleanup boundary cases tied to actual DD18 APIs | On actual registry delivery. Staged tests/case inputs for stale serial, wrong registry, release replacement, world teardown, quarantine and aliasing. Not synthetic proof of UE cleanup. |
| XW04 | Native-domain authoring regression checks | After exact AG field mapping is stable. Positive/negative numeric/identity cases from actual validators; separate schema validity from native capability and real asset compatibility. |
| XW05 | Offline project dependency/path pin checker | After preview source acceptance. Check canonical package/object paths and disk hashes; never certify class exports, skeleton fit or cooking from file presence. |
| XW06 | Action-identity/failure/cleanup adversarial acceptance fixtures | Once C09 API is concrete. Tests target instance-before-playback, stale event attribution, death/break priority and cleanup-before-unlock. No alternate production executor. |
| XW07 | Timeline/frame-rate/time-scale metamorphic expected-case checks | On C11 schema and observed clock definition. Exact source-clock/event expectations, missed/duplicate boundaries; no unearned subframe precision. |
| XW08 | Damage/defense/geometry outcome acceptance fixtures | On C12 move/defense contracts. Tests derived from approved semantics and visible contacts; preserve measured dodge/roll constraints. |
| XW09 | Context/utility/movement replay evidence checks | On C14/C15 data and log schema. Detect illegal awareness, stale target, eligibility/motion ownership and unexplained fallback; no synthetic AI performance claims. |
| XW10 | Server/client identity and authority evidence checks | Authority design review starts with C05/C09; executable log checks when C17 schema exists. Separate real listen/dedicated two-client evidence from model fixtures. |
| XW11 | Performance evidence importer/verification tests | Use actual benchmark data when available. Check hardware/proxy/session/settings/warmup/sample provenance and p99, not average FPS alone; no fabricated hardware results. |
| XW12 | All83 evidence-closure candidate ledger and consistency checks | Per actual accepted milestone. Every closed row references exact behavior, raw evidence/hash and scoped X decision; mapping or tests count never closes a row automatically. |
| XW13 | Current-binary regression/cook/Shipping evidence reconciliation | At stable C19 candidate. Verify matching source/asset/binary pins and actual gates; never inherit old40 driver gate. No Codex engine run. |
| XW14 | Exact stable-batch include/exclude/hash proposal for AG | After accepted stable C20 inputs. Identify approved owned changes and preserved dirt; no commits, pushes or history operations by Codex. AG executes only explicit released batch. |
| XW15 | Evidence-based owner progress/artifact view | Meaningful milestone changes only. Distinguish implementation, tests, authoring usability and release status; no invented overall percentage or finish date. |

## Dependency discipline

XW00 interrupts every other card when an agent is waiting. XW02 depends on the already observed receipt/log formats, so it can progress immediately. Later cards wait for real schemas/APIs/evidence rather than inventing a duplicate architecture. Use existing accepted code/tools where available; build a new artifact only when it fills a concrete gap.

Each code card ends with actual source, meaningful tests, raw output/exit code/SHA, limits and a mailbox handoff when substantive. Preserve its own failed attempts too. Changes to the contract require new tests; an unchanged accepted artifact is reused, not repeatedly “audited” for activity. No auto-execution/auto-approval from the JSON queue.

Current next step: finish C245's retained-identity review; start XW02 receipt/path/log verification code; then review DD18/AG actual deliveries as they arrive. Claude remains sole engine operator and AG remains scoped content/offline plus only later accepted-batch git operator. All83/networking required;A5visuals parked.

# AT-C41–C45: offline closeout and handoff

## Completed checks

- Queue validator now includes `QUEUE_AT.md` and enforces 50 unique ordered IDs under ten headings with five rows per batch. AA, AB, and AT each validate at 50 rows.
- Focused route/stage/cook/camera/aura/smoke/hash/source-reference contracts: 76/76 passed. The first invocation exposed that the queue-validator test imported a sibling script as a top-level module; its import is now package-qualified and the full set passes.
- Python syntax checks passed for changed Python tools and contracts. PowerShell parser AST passed for the changed aura launcher.
- Documentation link check: `broken_links=0`. `git diff --check` passed (only Git LF-to-CRLF normalization notices).
- TEST_PLAN remained read-only. No Unreal, PIE, build, cook, package or staged-output access; no raw evidence or asset changes.

## Current Lead/owner gates

- Camera KI-037/KI-066: B+C plan remains unapplied; owner choice and package proof open. C-1108's two-bool config suggestion is incorporated in the plan only.
- KI-191: PARTIAL; full-fight aura visibility remains not discernible, pair comparison lacks accepted result, owner disposition and first-use/cook/package proof remain open.
- KI-192: PIE-closed on Lead C-1100 evidence; package remains open.
- KI-193: PARTIAL pending staged/cooked package evidence.
- KI-196: tested DATA-default no-assignment moving cases proven in PIE; package open.
- KI-197: source/stage-root fix and offline contracts complete; Lead dual-package identity proof pending.
- KI-198: tested DATA-default guard-counter case proven in PIE; package open.
- KI-199: DATA-default workaround proven for tested standing/moving cases; root cause not isolated and package open. Do not request parity-only legacy reruns.

See `KNOWN_ISSUES.md`, `TEST_PLAN.md`, `AT_C26_C30_OWNER_GATED_PATCH_READINESS.md`, and `AT_C31_C35_SHARED_PACKAGE_INTAKE.md` for evidence boundaries and intake fields. No commit or push was made.

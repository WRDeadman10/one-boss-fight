# A-41 and C-87 evidence review

2026-10-25. Codex read the submitted reports, AG extraction script/log, Claude probe sources, raw combat-style/ability/BT/notify exports, current native rules and the existing bot driver. No editor or runtime test was run by Codex.

## A-41: usable offline subset; residual corrections

Revision 03 fixes durations, dual root metrics, foot-grounding overclaims, production trace ownership and the get-up route. All 20 log input hashes/sizes still match current files. This subset can inform reconciliation while runtime evidence remains pending. Complete visual baseline acceptance remains pending.

Remaining corrections within AG's own files:

- The A4 table hash prefix `083cfc091924` is stale; the current FBX and raw log are `10ae94157485...`. The report also labels unscaled offline hand distances 15.8–37.0 cm as being on the 1.5x runtime boss. State the original extraction space/scale and preserve world-space reach as unverified. The revised script no longer emits those selected-frame values; retain their earlier raw provenance or drop them.
- `RPGTelegraphRules::TargetFor` returns a target only for A1/A1b/A3a/A3b. A2/A6 do not receive CloseTelegraph stretching. Moreover A1 fallback shares ActiveStart .35 and target cap .35, so `RateFor` returns 1; a positive cvar alone does not prove compensation of an early raw trace. Describe the exact per-row predicate; retain runtime mismatch as pending.
- The `.txt` A5 sidecar declares CommitTime .35 and release .40; it does not prove maximum arm draw at .35. Cite it as author intent. Sidecar frames are zero-based, extraction frames begin at 1; do not equate their frame labels without an offset convention.
- Integrity cleanup remains incomplete: report has 2 control characters, timing matrix 3, geometry table 1. Carriage-return escapes also split `rpg.CloseTelegraph` into a new line starting `pg.CloseTelegraph`; hash `f61...` begins with a form-feed instead of `f`. Use literal safe text and verify the saved files. Cosmetic BladeEnd at 140 is 23.3 cm behind tip; Weapon End at 142 is 21.3 cm. Avoid assigning one offset to both.
- Incorporate Claude's newly resolved MidRange/Sprint/Retaliation into the pending visual inventory. Their actual appearance still awaits capture.

## C-87: substantive progress; scope and precision

Raw exports confirm the three additional damaging montage assignments and the native table omits them. The native tracker therefore does not supply its instance/commit/telegraph handling for them. Whether pack ability/state logic supplies other safeguards remains unresolved; “no phase/stagger legality check” is too broad before the pack path is inspected.

The combat-style export and live dump contain **11 boss abilities**, including `GA_EnemyRagdollDeath`, rather than exactly 10. Retain the death ability in lifecycle coverage. The extra player ability later in the dump must not be counted as a boss grant.

The BT export supports ordered selectors and 25-percent chance decorators. Those decorator probabilities do not establish successful action frequencies: rare activation failure can fall through, lower-band failures may reach later branches, and other eligibility checks can reject attempts. Preserve those distinctions in opportunity counts.

E-002-08 currently summarizes a graph read without retaining the raw graph/node/pin export. Preserve the `Get Abilities By All Tags` and activation-loop evidence, including the function that builds/filters its returned array, eligibility and cooldown checks. Style-array order alone does not prove returned iteration order. Sprint may also be selected when Leap fails for reasons beyond cooldown; F-2 remains conditional until those checks and natural samples are reconciled.

No native A4 caller was found beyond StartForTest; `StartMove` is BlueprintCallable. Conclude no route in the inspected native/BT/style evidence and retain a possible Blueprint caller as unresolved unless callsites are inspected. A5's healing trigger likewise needs its actual detection predicate described before an exclusive “only potion” conclusion.

E-001 raw cvar/world lines match the current saved editor log. This supports configuration at those recorded timestamps; it does not establish future run state. File timestamps and DLL hash establish consistency with the source snapshot, not a reproducible build proof.

## Bounded next diagnostics

Claude may continue the proposed observer in its claimed Evidence/probes folder alongside the unchanged existing bot driver: one code-default run (wake 1, telegraph .4), then one warm-state run (0/0), with the same build and other settings recorded. Existing P0 diagnostic authorization covers this. Read the actual 420-second limit rather than the stale 240-second header. Preserve each unique BalanceRuns archive and observer output in the evidence set before the second run replaces mutable summaries. Record cvars at run start/end, exact driver/probe hashes, phase, montage-local position/rate, instance/restart ambiguity and observed counts. A montage poll may miss short/restarted/overlapped playback; state that limitation. A bot that never heals does not exercise A5 selection. These are diagnostic samples, not frequency estimates or P0 acceptance.

No gameplay/source/config/asset changes, new instrumentation in gameplay code, build, implementation phase or design changes follow from this review.

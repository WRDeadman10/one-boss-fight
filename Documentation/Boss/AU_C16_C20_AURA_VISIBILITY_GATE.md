# AU-C16–C20 — aura evidence gates and comparison sheet

**Status:** C16–C18 and C20 complete offline; C19 remains a Lead PIE gate. No Unreal run or asset edit by Codex. The owner visual disposition remains open.

## Lifecycle and diagnostic scope

- The Lead-only lifecycle probe now samples health at 50.1%, full health, and exactly 50%, then checks Tier 2 off/on, encounter reset, and next-phase reactivation. The summary requires all seven checks to pass. This is a requested observation matrix, not a claim that a Live PIE run has passed; the probe has not been run by Codex.
- The aura comparison manifest and `FRAME_READY` log include the active Niagara asset, active state, attach parent/socket, component transform, FollowCamera and pivot, health fraction, run/route/capture ID, frame completion, mean gray and PNG SHA-256. Unsupported component readbacks serialize as `UNKNOWN` instead of guessed values.
- Transient restoration is a named readback-checked helper. A synthetic injected-comparison-error fixture verifies restoration of the original component asset and activation; source contracts verify the error path calls `finish("error")`, which invokes restoration. No editor property or saved asset is changed.

## Evidence-only comparison sheet

| Evidence item | Current evidence | Status / limit |
|---|---|---|
| BUILD-255 full fight | Owner review describes six initial black source frames; distinct from BUILD-259 | Historical capture-specific; no transfer of findings |
| BUILD-259 full fight | Four ER moves reported; aura not discernible; no parry action | Technical observation only; no owner visual check recorded |
| C-1042 focused aura lifecycle | Controlled lifecycle and parry/PPM response reported | Focused PIE scope; not a full-fight appearance result |
| C-1075 paired comparison | Approved DATA capture reported mean gray 0.1; legacy candidate runtime readback inactive | Failed evidence; no visual comparison |
| C-1077 hotfixed paired comparison | Black frames reported on both routes, mean gray 0.000 | Failed evidence; root cause not established |
| Separate showcase options | Three render options reported and sent to owner | Owner disposition not found in latest mailbox history |
| AU-C15 approved-only retry | Instrumented to record run identity, route, frame hashes, camera/pivot and explicit failure stage | Lead PIE pending; only proceed to pair capture if retained frame is complete and clears the numeric capture floor |
| Cook/package | KI-191/KI-193 gates remain open | PIE/readback does not establish staged or packaged appearance |

Numeric brightness is used to reject unusable capture output; it cannot choose a visual option. Owner boxes and selections are unchanged. The phase-transition-order difference remains a hypothesis from prior static comparison and is not elevated to root cause here.

## Verification

`python -m unittest Scripts.Editor.test_pie_tier2_aura_offline Scripts.Editor.test_pie_aura_comparison_contract Scripts.Editor.test_aura_png_metrics -q` — 16 passed. Changed Python files compile. `git diff --check` passes with only workspace line-ending notices. Lead must run C15 before the gated paired comparison C19.

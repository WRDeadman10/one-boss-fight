# AQ-C26–C30 — open-KI offline triage

## C26 — five bounded offline audits

These audits read source, existing tests, and retained evidence only. None
closes a runtime, owner, build, cook, or package gate.

| Target | Offline audit question | Bounded acceptance |
|---|---|---|
| KI-189 — first-use Niagara load | Trace the opt-in aura/shockwave/parry soft-reference load sites and existing contracts. | Name each synchronous load and gate; separate default-off behavior from first-use hitch measurement. No preload change. |
| KI-192 — R2 charged-hold split | Compare the intended 0.35 s mapping, probe cases, callback scope, and retained route samples. | Establish what the source and samples do and do not explain; preserve the authored threshold. No tuning. |
| KI-193 — exact cook closure | Check required path list, source cook-root checks, and staged-manifest tooling/evidence. | Identify the exact eight package paths and state why source configuration cannot replace same-build staged manifest and runtime evidence. No package run. |
| KI-196 — moving dodge | Review corrected movement-input probe and accepted defaults evidence against prior invalid zero-speed probe. | Distinguish accepted tested PIE cases from the remaining staged-package gate. No input change. |
| KI-197 — stage identity | Trace Package.ps1 output, MakeBenchKit defaults/overrides, and the identity preflight boundary. | Record path ambiguity and any destructive kit-output behavior without running scripts or asserting contamination. No package-script edit. |

## C27 — KI-189 source-to-test boundary

`RPGTier2BossPresentation.cpp:50–54` synchronously resolves the selected aura
soft reference when the mesh exists, then attaches the result. The focused pure
rules in `RPGTier2BossRulesTests.cpp:7–25` cover show/spawn eligibility and
duplicate/reset rules; they do not load a Niagara asset or time its first use.
The optional attach socket contract at `RPGTier2BossRulesTests.cpp:33–55`
checks default `NAME_None` and explicit `spine_03`, not an asset load or
rendered visibility. `KNOWN_ISSUES.md:330` is accurate: default-off behavior
does not prove a warmed or first-use runtime timing result. **Next gate:** Lead
records cold first-use and warmed-event timing with Tier 1 enabled, while
confirming the default path remains unloaded; only propose preload if measured
material. No source change follows from this offline audit.

## C28 — KI-192 mapping and callback boundary

The retained record in `AC_C26_C30_DLSS_AND_PERFORMANCE_GATES.md:23` reports
the 0.36 s legacy/data montage split, matching choices at 0.34/0.35/0.70 s,
and approximately 25–32 ms game ticks. The probe's explicit 0.35 s boundary
case is at `pie_er_control_latency.py:29`. The audit doc identifies
`RPGDodgeTiming.cpp:489–520` as the triggered R2 tap/strong replay callback,
not the hold threshold implementation. These facts establish one game-tick
bounded route difference, not a physical device latency measurement or a
root-cause attribution. **Next gate:** preserve the 0.35 s mapping; if Lead
authorizes another diagnostic, vary game tick rate and inspect the actual
Enhanced Input mapping/action values on both routes without changing gameplay
thresholds first. KI-192 stays open.

## C29 — KI-197 stage identity boundary

`Scripts/Package.ps1:30` selects the shared `Saved\StagedBuilds` root for both
configurations. `Scripts/MakeBenchKit.ps1:16–20` defaults Shipping to a
separate root with fallback to the shared root, and Development to the shared
root; explicit overrides are available. This supports path ambiguity, not a
claim that outputs have actually been contaminated. Existing KI-197 records
that a read-only stamped-root preflight passes but the package wrapper remains
unreconciled (`KNOWN_ISSUES.md:338`). Separately, `MakeBenchKit.ps1:23–24`
removes its fixed derived `OneBossFight_BenchKit` output directory when it
already exists. Claude confirmed this replacement behavior is intentional by
design, not a defect or blocker. This audit did not execute the script.

**Next gate:** give `Package.ps1`, smoke, benchmark, and kit explicit aligned
per-configuration roots and clean-output semantics; preserve unique stamps and
same-build manifests. Keep the fixed derived-directory replacement behavior
documented; KI-197 remains open. No stage or kit was readied by this audit.

## C30 — handoff status

The five next offline candidates are selected above. Three audits (KI-189,
KI-192, KI-197) are complete; KI-193 and KI-196 remain queued. Runtime and
package evidence are deliberately left to their assigned Lead/owner gates.

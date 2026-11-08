# AQ-C21–C25 — Development package gates

## Evidence boundary

Current source and PIE evidence does not establish that a staged Development
package contains or executes the same behavior. Keep each package/cook claim
separate from native build, editor PIE, and source cook-directory configuration.
Do not close KI-193, KI-196, KI-198, KI-199, or the selected camera option's
package gate from PIE results alone.

## Per-feature acceptance

| Item | Already established before package gate | Required Development-package evidence |
|---|---|---|
| KI-193 air attacks | Source defaults and both-route PIE hits, 4/4 per route (KNOWN_ISSUES.md KI-193) | Compare all eight paths in `Scripts/Tools/er_tier2_required_cook_assets.txt` against the authoritative cooked/staged manifest for the same build. Run the staged Development executable on legacy and data routes; capture default-wired ground R1/R2 and AirLight/AirHeavy hit attribution/damage. Preserve command, exit code, manifest and hashes, full logs, route/case summaries. |
| KI-196 moving dodge | Default-wired moving case proven in DATA-default PIE (KNOWN_ISSUES.md KI-196) | In the staged DATA-default package, verify first moving dodge after draw and repeated moving dodges; require same-run `route=data` witness and preserve measured travel, action counts, executable/build identity, logs/video and exit status. PIE values remain PIE evidence. Do not queue a legacy parity rerun per C-1104. |
| KI-198 guard counter | Real blocked A4 → armed → R2 → GuardCounter hit with boss HP loss in the tested DATA-default PIE case (KNOWN_ISSUES.md KI-198) | In the staged DATA-default package, demonstrate the real A4 block, arm, accepted R2, correct montage, Strong hit attribution and boss HP delta. Retain same-run `route=data` witness, per-step trace and process/package identity. |
| KI-199 dodge retry | First standing and moving dodge workaround plus repeats proven in tested DATA-default PIE cases; root cause unisolated (KNOWN_ISSUES.md KI-199) | In the staged DATA-default package, run standing-first-after-draw and moving-first-after-draw cases plus repeats. Show one retry, activation, buffered-key consumption, root-motion result, and no duplicate activation; preserve same-run route witness. Leave underlying cause unclaimed. Do not queue a legacy rerun per C-1104. |
| Camera B/C | B and C have separate DATA-default Lead PIE evidence; C-1090 tested B+C in attack mode in two nominal arms, both DATA-default per C-1099 (9 A4/A6 tracker starts/run, zero refusals, zero intrusion samples, 36–37° reported median view-to-boss). Owner choice remains pending. | Only after owner selection: stage the chosen config/default and identify it from the same package manifest. Exercise the selected option in the DATA-default Development package with same-run activation witness, exact CVar request/readback and representative close-overlap/framing/input cases. Prove the result does not depend on Development-only diagnostic code/CVars, and preserve baseline-off comparison, packaged config readback, logs/video, hashes, cleanup and exact executable identity. C-1090 covers one DATA-default attack-mode case without the specified look injection; additional combined scenarios and package evidence remain open. Do not queue legacy parity reruns per C-1104. |

## Clean run identity and retained artifacts

1. Start from a clean, closed-editor state. Record source revision, target,
   configuration, UAT command and arguments, environment/config overrides, and
   the unique staged directory. Do not reuse a Development stage as Shipping
   evidence or vice versa.
2. Preserve complete UAT cook/package logs and process exit codes. Record the
   staged executable and project DLL paths plus SHA-256; preserve the cooked
   content manifest/export and its hash. A configured cook root alone does not
   prove exact staged package presence.
3. Run each route as a separate identified case from the staged executable.
   Retain complete stdout/logs, per-case summary, short video where visual
   behavior matters, and a manifest mapping every artifact to the exact package
   hash and route.
4. Report PASS only when required paths are present and every required case
   completes with its expected observable. Missing artifact, wrong package
   identity, early process exit, unresolved path, or incomplete route leaves
   that gate OPEN. Never aggregate PIE and package evidence into one result.
5. Development package acceptance does not imply Shipping acceptance, target
   hardware performance, or final owner approval. Those require their own
   explicit gates.

## Offline checks

`python -m unittest Scripts.Tools.test_aq_package_gates` checks the package/PIE
separation and verifies the recorded KNOWN_ISSUES package status is still open.
It does not package, cook, launch, or prove runtime behavior.

# DD12 package 01: one encounter cluster plan, source and test delivery for review (NOT built, NOT run)

Order: Codex X-263 / `Codex/DD12_ENCOUNTER_CLUSTER_PACKAGE_01.md`. Implementer: Claude. Exactly THREE NEW files; NO existing Source file was edited (the 174 existing files are byte-identical: `pre_source_manifest_sha256.txt` equals the accepted DD11 manifest, `post_write_source_manifest_sha256.txt` has 177 files and differs from it by exactly the three added lines; 11 relevant pins in `pre_pins.txt` verify). Nothing was built, no UHT, no automation, no engine process, no git operation. The actual diff is `three_file.diff` (all three files against /dev/null); `Review/` holds the copies.

| file | state | lines | sha256 | line endings |
|---|---|---|---|---|
| `Player/RPGBossEncounterClusterAdapters.h` | NEW | 41 | `2b0b9a2813d79707e150717d28990903771399ed8a6a654b6137927a1f92b7fd` | CRLF, 0 bare LF, 0 bare CR |
| `Player/RPGBossEncounterClusterAdapters.cpp` | NEW | 87 | `8e83c527e24a49c531b8a8317e5ac8f64f2d667274f872eec0bdc59a8bc57a1e` | CRLF |
| `Tests/RPGBossEncounterClusterAdaptersTests.cpp` | NEW | 613 | `c2d3a3fbdbba6375f654967c1ead19f689c8918cb99907ffb54a00410b20feb1` | CRLF, 0 quoted `"/Game/` literal |

`three_file.diff` sha256 `130e18b33cb4fc189ba4cde4cba239a8b67540d6a0bde91d62a24330a238c2f7`. The tests hash above is the state AFTER the independent pass below; the state before it (tests `453cea4b...`, previous diff) is kept in `first_state_before_review/`. The two production files did not change.

## What it does

The accepted stats and encounter policy adapters each describe a plan for the SAME native class and legacy instance (`URPGBossEncounter`, `RPGBossEncounter`); inserting both would create the encounter twice. `RPGBossEncounterClusterAdapters` is the ONE encounter plan:

- `ValidateEncounterCluster(Config, Error)`: clears the diagnostic, then `RPGBossStatsAdapters::ValidateStats` on the COMPLETE four-stat record (finite for all four, generic domains, the native health override capability: health above 1, so 1.5 is valid and 1.0 or 0.5 is `UnsupportedNativeHealthOverride`), then `RPGBossEncounterPolicyAdapters::ValidateEncounterPolicy` (gate radius finite, not negative, 0 valid). The exact existing tokens and paths are reported; no new domain, tuning, fallback or compiler restriction.
- `ConfigureEncounterCluster(Component, Config, Error)`: the accepted lifecycle check in the accepted order (restated privately, as before), then the whole cluster validation, then ONE write block of exactly three fields on an exact `URPGBossEncounter`: `BossMaxHealth` from `Stats.MaxHealth`, `GateRadius` and `bResetOnPlayerRespawn` from `EncounterPolicy`. No older mutating callback is invoked before the policy is validated, so no partial write is possible. The three posture writes stay with the posture plan.
- `MakeEncounterClusterPlan()`: class `URPGBossEncounter`, legacy name `RPGBossEncounter`, required fields `Stats.MaxHealth`, `EncounterPolicy.GateRadius`, `EncounterPolicy.bResetOnPlayerRespawn` (constants reused from the existing headers), callback `ConfigureEncounterCluster`. Unwired.
- It creates, registers, begins, ticks and loads nothing, parses no manifest Value text, uses no reflection or ImportText, looks up no actor or target, reads and writes no pack attribute, starts no timer, reset or dormancy and executes no health override; every other native field and all runtime state stay unchanged. Authoring assignment only: not an effective gate, reset or pack health proof, not readiness. The native public fields already provide the seam; no native, Binding or schema edit was needed.

## Tests (4 focused, `OneBossFight.Binding.EncounterCluster.*`; the discovered count is to be reported from the actual run, not assumed: 101 + 4 = 105 if all are found)

| test | covers |
|---|---|
| `Assign` | plan identity (class, legacy name, three exact paths in order, callback set) and the proof of the duplicate gap: the cluster plan has the same class and instance name as BOTH older encounter plans and its required fields are exactly the union of theirs; config A through the plan callback with manifest Value text that contradicts the typed record (only the typed record counts); the owner's component set (identity and count) captured after the fixture and immediately before each configure call and compared right after, for the callback and for the direct config B (the allocation limit of such a snapshot is stated); all three destinations equal the typed record and differ from a distinct start; every other field and the runtime state (test freeze sentinel, dormancy, waking, generation, counters) unchanged; nothing registered or begun; config B (health 1.5, gate radius 0, reset true), a fractional gate radius and a negative-zero gate radius through the direct helper |
| `Validation` | whole-record refusal with the exact token and path through BOTH the validator and the assignment, and no write at all (all three typed fields and all other state equal the start): valid boundary cases (gate 0, -0.0, 0.001; health 1.5 and 1.0001; fractional posture with zero regeneration); INVALID STATS with a valid non-default policy (health NaN, +Inf, 0, negative, 1.0, 0.5; posture 0; negative regeneration delay; regeneration rate NaN) and INVALID POLICY with a valid non-default health (gate NaN, +Inf, -Inf, -0.0001, -1), so a premature write in either order is caught; precedence (stats first, including a posture field before an invalid gate); diagnostics cleared; the component still configurable afterwards |
| `Isolation` | two configured components independent, a later config change does not reach A, a refused record leaves A exactly as it was in both orderings (valid health with invalid policy, invalid health with valid policy), an untouched component and the class default object keep the native values (health 2000, gate radius 1200, reset true), the sentinel survives |
| `Rejections` | wrong class (a posture, a scene component), registered, begun (the gate radius is set to 0 first, exactly as the earlier encounter tests do, because the native `BeginPlay` stores the home transform and only sleeps for a gate radius above 0; plain actor owner; prerequisites asserted), owner begun, orphan (invalid owner), destroyed-retained, destroyed wrong-class (`InvalidComponent` first); each leaves the target and the other native components unchanged |

No compile test, on purpose (order): the package adds no schema or compiler API; the use of the accepted validators is backed by the cluster's own refusals in `Validation`, `Isolation` and `Rejections`.

## Judgement calls (please confirm or change)

1. Four tests instead of mirroring six (no Compile test by order; Authoring would only repeat reflection that DD3 and DD6 already proved for the fields this cluster writes). 2. The lifecycle check is restated privately again (a shared helper stays a later consolidation package). 3. The plan-versus-older-plans equality is asserted in `Assign` rather than relied on by comment. 4. The begun fixture follows the earlier encounter test exactly (gate radius 0 first); I read `URPGBossEncounter::BeginPlay` and it does nothing else on a plain actor with a gate radius of 0.

## What this does NOT prove or do

No effective gate, reset or pack health behavior (nothing is registered or ticked, no attribute is touched), no real startup chronology or component order, no combined preflight composition (a later order), no wiring, reservation or activation, no serialized or Details proof, no production compile, no 40-row gate on a new binary. The component-set snapshot has the allocation limit of any snapshot; the begun fixture is a plain actor, not a real startup.

## Next, when you release it

Scoped verification order: fresh safety; UHT (no header of the existing files changed, so UHT is expected NOT to be needed for existing headers, but a new header with no generated code may still re-scan; report the actual UHT output if invoked) and build; run only `OneBossFight.Binding.EncounterCluster`; only if clean the full suite with the actual count reported (the 101 earlier paths present plus the new ones, `OneBossFight.Content.CookCoverage` passing); exact diagnostics; final manifests, pins and binaries. No UHT, build or automation before your review of this diff.

## Independent read-only pass (not by me) and the changes it caused

The pass read the three files against the headers and the UE 5.5 engine source: every symbol resolves, the `RequiredFields` and `Configure` assignments match the older plans, the component-set capture is valid (a component created with the actor as outer joins the owner's set at initialization), no whole copy or assignment of the config from an lvalue, no shadowing, every `Check` token and path in `Validation` matches `ValidateStats` and `ValidateEncounterPolicy`, the begun-play fixture is safe (`BeginPlay` stores the home transform and sleeps only for a gate radius above 0), no quoted `/Game/` literal; verdict: expected to compile and pass. Test-strength findings and my changes:
1. Lifecycle-before-validation was not tested (every rejection used a valid record, so swapping the order would have passed): `ExpectRejected` now refuses every fixture with a valid AND an invalid record (health 0, gate radius -1) and expects the lifecycle token either way, with the state unchanged.
2. Valid boundary cases only reached the validator: `Check` now also runs the assignment on every valid record, requires success, compares all three destinations with the record, checks no component was created and every other public field unchanged, then arms the start state again.
3. Component-set capture was missing around the other calls: now captured before and compared after in the Validation refusals and in the two Isolation refusals (through shared helpers `CaptureOwnedComponents` and `SameOwnedComponents`).
4. Wording: the encounter state compares only PUBLIC fields and getters (the private runtime state is not observable); the comments and messages now say so.
5. Added the precedence case health 1.0 (native floor) with an invalid gate radius: the stats record is still first.
6. Comment: the late-owner fixture also dispatches an actor-level `BeginPlay` on an actor with no components; the header comment now says "the only component BeginPlay".
7. Kept: the Isolation assertion of the native defaults (2000, 1200, true) is a documented-values check on purpose.

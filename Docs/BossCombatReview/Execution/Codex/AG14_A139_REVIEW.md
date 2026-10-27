# A139 / AG14: corrections required

2026-10-27, Codex. Reviewed actual report `Antigravity/CATALOG_COVERAGE_CONSUMER_AUDIT.md` (22160 bytes, SHA256 `25c6e41ccae6c4186cc08be0d1c2104a3ef6e06ef13d2f083c11a1bd44851038`). All **15** table input hash/size receipts independently match. Corrected AG13 report is 30869 bytes / `f15a99cd3bf750dfaea8b537388eec278cab2792bf05a547c0a09d88541354dc`; all **17** current table receipts now match, closing X211's compiler receipt exception. Historical wrong receipts remain historical.

AG14's central selected-source finding is useful: HitIntake/SwingTracker query their table objects rather than reading epoch coverage; diagnostic output is not combat execution proof. Final acceptance awaits the bounded corrections below. No runtime defect, asset reload, test or policy change is established by this review.

## 1. Hyperarmor is copied into coverage, omitted only from formatted lines

`RPGCombatCatalog.h:77–83` defines `FCoverage::Effective` as **FRPGWeaponAttackRow**, which includes `HyperArmorStart` and `HyperArmorEnd` (`RPGWeaponAttackTable.h:44–47`). `Find` copies the entire row into that field. Both coverage formatters omit these fields from their text, but the values remain present in the coverage object. Correct executive finding3, matrix, diagram/conclusion, witness4 and Option B. No expansion of FCoverage is needed merely to hold these existing fields. A formatter omission is not a missing schema field.

Witness4 must compare the stored `Effective` fields with formatted output and the separately copied swing window. Do not assert no field exists or that hyperarmor necessarily applies at0.400s: montage/kind/style/position must match, the relevant row must be established and applying the immunity effect can fail (`UpdateHyperArmor` and `SetHyperArmor`). Default window metadata alone is not successful runtime immunity proof.

## 2. Cached UObject pointer does not establish package-reload outcome

BeginPlay table caching and absence of explicit consumer reload code are source facts. They do not prove an engine package reloader cannot replace/fix up a reflected `UPROPERTY(Transient) TObjectPtr` reference, or mutate an object in place. Retract the guaranteed unchanged-address result in witness3/section4.3. No reload mechanism was inspected or exercised. Raw address alone is also insufficient to distinguish replacement/object reuse.

Use an explicitly conditional unrun experiment: record weak/serial object identity and selected values before/after a specified future approved reload/replacement operation; inspect actual reference identity and newly copied hit/swing rows. No destructive reload action is authorized now. Keep no-explicit-refresh observation separate from observed engine behavior.

## 3. Override/API/storage details

`RPGHitIntake.h:175` declares `BleedOverride` as a plain private float, not a UPROPERTY. `Scaler` is a persistent **member** at185, not a stack object. Trace `OnHit`/`OnLoss` pairing rather than implying health multiplication completes synchronously on lookup.

Swing's actual restore method is `ClearCostOverrides()` (cpp63–70); there is no `ResetTestTable()` in the reviewed source. Include `CostOverrides` precedence at cpp251–255, not just the stamina toggle and hyperarmor override. `Wanted>=0` leaves pack cost when negative; `StaminaExtra` plus attribute read/write outcomes constrain the final charge. A table value is not a guaranteed exact total stamina deduction. Preserve test-hook target guards.

Both hit and swing paths copy a row. An in-place table change affects a **subsequent lookup on that same object**, not an already captured row/current swing. Do not claim global immediate mutation propagation. Pointer retention and value-copy timing are separate.

## 4. Witness1 and2 need controlled keys, values and side effects

Witness1 cannot mutate arbitrary `Rows[0]` and infer a sword-light result: built-in default row0 is claymore-light, while authored row order was not inspected. Resolve the exact selected lookup and actual consumer object identity first. Coverage text uses **WeaponId**, not necessarily StyleName. Pin actual row/index/provenance and route; choose distinguishable fixture values without presenting them as approved gameplay thresholds. Observe the copied hit row as well as posture readback, controlling holds, posture caps/regen, merges, attack classification and overlays so a99 input is not assumed to cause99 observed loss. Follow existing no-PIE-component-property-edit rule; future approved fixture/test hooks only, no ad hoc reflection mutation instruction.

Witness2 must branch exact -> first any-kind -> fallback; an unlisted style alone does **not** guarantee fallback because any-weapon rows may exist. Control both row sets and `Fallback` contents;20 is the built-in default, not a guaranteed authored fallback. For catalog experiments respect `W.bRequireExactRows`: compile can reject the intended fallback fixture. A fictitious style can also fail earlier typed reference validation; specify an isolated pure lookup experiment or a valid future fixture, not guaranteed successful production compile. Include any-weapon and fallback branches distinctly.

## 5. Scope and guarantees

Bound codebase-wide exclusivity/never claims to the inspected source (or state exact search scope); the two coverage formatter functions are separate direct consumers, not a demonstrated proxy chain. Correct the subsystem formatter citation to current cpp378–380, not311. Retain source versus Blueprint caller limits.

`FContext::Publish` is single-attempt per context; runtime subsystem ownership is per game instance. Do not equate game-instance and entire process lifetime. `Compile(..., bResolveAssets=false)` does not populate coverage; the production resolution path uses `LoadOrDefault`, which may supply a rooted transient default table. Successful compilation is not proof an authored asset was loaded.

Option B's assertion that direct epoch consumption guarantees strict immutability and **complete parity** is too strong. Pure copied row reads could align selected inputs, while overrides, lookup keys, capture timing, caps, pack effects and dependency/association rules still require evidence. Full-row snapshots already contain hyperarmor. Options remain proposals, not an instruction to rewire consumers or change tuning policy. Readiness publication and combat consumption remain different claims.

## Next

AG revises only its own report in one bounded pass, with actual input/output receipts. No new broad audit, implementation, source/asset/config/script edits, engine operations, owner interruption, Claude wake or acknowledgment wait. Keep all proposed witnesses explicitly UNRUN, preserve historical claims and receipt failures. All83 active, A5 parked, P1 design-only and 2b+ held. Codex ran raw receipt verification and source inspection only; no Unreal/model tests are claimed.

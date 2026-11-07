# AB-C11–C15 — ER integration and test readiness

Date: 2026-11-07. Static review plus native assertions authored; no Unreal test/build/import/cook/PIE run.

Superseding update (C-973): the AirLight/AirHeavy optional fields and runtime array overrides are now implemented test-first under the approved production change. This audit's earlier “no dedicated optional fields” statements describe the state at the time of AB-C11–C15 completion; see `Documentation/Boss/AB_C16_C20_RELEASE_AND_AIR_FIELD_PROPOSAL.md` for the implementation and remaining Lead checks.

## C11 — Backstep integration requirements

`BackstepMontage` and `BackstepPlayRate` already exist; empty reference preserves the pack route. C-968 rejects the current Backstep animation pending R4 because it rolls/flips. Required before assignment: accepted owner-reviewed video; new-only import; a `UAnimMontage` on the player's expected skeleton/slot with the accepted short hop and root motion; confirm play rate, facing, root-motion extraction, and completion behavior in PIE. Current importer produces `UAnimSequence`, so a montage conversion/creation step is still missing.

## C12/C14 — optional assignment coverage

Native `Content.PackWiring` asserts both montage soft references are empty on the default object. It does not prove non-null assignment selects the montage in gameplay, nor does it exercise a loaded montage asset. A test that only assigns a transient montage pointer would prove container storage but not the route, so no such shallow test was added. Backstep's pure decision rule covers roll/backstep selection; runtime path still needs a Lead test with an accepted montage. Air light/heavy have no optional fields or route to test yet.

## C13 — GuardCounter readiness

C-968 permits import only. A-582 reports the new asset is an `AnimSequence`, while `GuardCounterMontage` and the strong-attack array both use montage types. A-582 also reports 1.6667 s sequence length and a 0.8000 s sub-slice, which differs from importer metadata's expected 0.8000 s asset duration; inspect the import receipt and asset readback before treating the duration assertion as satisfied. The runtime integration uses a successful-block timestamp and a proposed 0.60 s R2 window; clip metadata's 0.333–0.533 s hit window is not consumed by current code. Owner video review, montage asset, Lead build, and blocked-contact PIE remain pending.

## C14 — air attack wiring readiness

The spec's intended route is ER-A2 to `FallingAttackMontages` and ER-A3 to the strong path selected while airborne. Current `URPGDodgeTiming` only binds R1 light / R2 heavy ground actions, injects the pack's light/strong actions, and has no air-montage soft fields or airborne selector. R4 and owner video gates also remain. Implement only after accepted assets exist and the Lead confirms pack's live montage array structs/airborne state route; do not infer that the imported AnimSequence can be assigned into the pack arrays.

## C15 — probe/evidence mapping

`pie_er_control_latency.py` records case input timestamps, per-tick player montage name/position, component counters for dodge, and tick duration; it separates baseline montage from the sample. This supports route and game-tick-bounded press-to-observation evidence, not physical device latency. The current probe does not instrument successful guard contact, counter window timestamp, or array restoration; those require a dedicated block/counter driver plus Lead-owned PIE. The C-969 two-route latency run remains scheduled after the import lock, and bench-dependent work remains parked.

## Immediate static blocker summary

Do not assign or ship the imported GuardCounter sequence yet: type and duration/readback evidence need reconciliation. Avoid broad import of all four clips; only GuardCounter is import-authorized under C-968, while the other three remain R4-gated. Status correction is reflected in `GATE07_ANIMATION_REVIEW.md` and KI-193.

# C-1237a: Per-boss montage notify timing opt-in

## Result

Added `URPGBossDefinition::bUseMontageNotifyTimings`, defaulting to `false`, and carried the value into the immutable participant configuration used on the data route. `RPGBossAttackTrackerAdapters::ConfigureAttackTracker` applies the flag to the tracker before encounter activation. Existing definitions therefore retain native legacy timing unless an author opts a definition in.

Compilation fails closed when the value is `true` without an explicit typed source-manifest field. A false value with no serialized source entry is represented by additive native-default provenance. No Ember definition or montage asset was changed; the Ember draft remains on its false default.

## Tests and evidence

The native `OneBossFight.Binding.DraftWorldIsolation` automation test now verifies default false, compiling an explicitly sourced true value, application to a transient `URPGAttackTracker`, and refusal of true without provenance.

- Focused offline parity-driver contract: 8/8.
- Python syntax check: PASS.
- Development editor build: PASS (80 compile/build actions).
- Full `Automation RunTests OneBossFight`: PASS, 497 started / 497 passed / 0 failed; exit code 0.
- Pinned DD27j manifest hash: `cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`.
- C-1155 root and execution locks were both released. No PIE was run; Lead owns the timing parity gate.

Evidence logs and the repeatable lock/build/suite runner are in `Docs/BossCombatReview/Execution/Codex/C1237A_MONTAGE_TIMING_OPT_IN/` and `Scripts/Editor/run_c1237a_montage_timing_opt_in_build.ps1`.

## Parity driver cleanup

The Ember notify parity driver now exercises only timing-off and timing-on for A1, A3a, and A3b. The PARRY arm, distance/press controls, and shared-counter checks were removed. Pack parry acceptance remains separate because its collision-trace windows do not depend on tracker timing. This cleanup does not verify the remaining timing driver in PIE.

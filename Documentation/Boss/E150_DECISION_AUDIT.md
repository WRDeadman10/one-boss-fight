# E150 decision audit: fallback token compatibility

Queue E incorrectly tags this combo-fallback question as D18; D18 is the parry cooldown-edge audit. The matching scope is Queue D D4, the combo fallback boundary audit. Queue E is corrected to point there.

`RPGBossCombo::Step` returns named reasons such as `Combo.DefaultRecovery`, `Combo.Target`, and `Combo.Depth`; the caller can fall back to ordinary selector evaluation after combo continuation refuses. `RPGBossComboFallbackTests.cpp` asserts the cone refusal token and proves the ordinary fallback starts from the same fresh snapshot. These strings are diagnostics/control values in current code, but no versioning or external consumer compatibility policy is documented.

No owner policy is needed while tokens remain internal to this implementation and tests. If scripts, saved data, telemetry consumers, or external integrations depend on exact token spelling, the project owner must approve a compatibility/versioning contract before such a dependency is introduced. Static inspection only; no tests/build/Editor run.

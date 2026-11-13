# V-C022 — A7-B replacement test matrix

The current legacy-vs-selected parity control stays until the owner-approved A7-B gates close. This matrix maps the future replacement tests; it does not edit or remove the current tests.

| Existing contract / source | Replacement test after retirement | Required assertions |
|---|---|---|
| `AbsentPreservesLegacyStartup` (`RPGBossStartupActivationTests.cpp:293+`) | `AbsentSelectionDoesNotAttachLegacyAfterRetirement` | Fresh world with no request reports the explicitly chosen no-selection result; no boss legacy bundle and no accidental partial setup |
| `LegacyStartupConfigOff` (`:328+`) | Retain as the no-legacy safety case until the config key is removed in its own reviewed phase | With retirement switch off, no legacy boss/player bundle; the test must not imply shipping selection proof |
| `SelectedStartupActivatesExactParticipants` (`:353+`) | Keep and extend to run through the eventual real caller seam | Exact boss/player participants, all required components, binding/manifest identity, no legacy component leakage |
| missing/invalid selection cases and `Scripts/Editor/pie_selection_refusal.py` | `RequestedMissingOrInvalidSelectionFailsClosedWithoutLegacyFallback` | `HardError`, exact refusal token, cleanup complete, boss disabled, no legacy bundle, player diagnostics retained |
| reset/rebind and respawn cases (`:353-419` and later startup tests) | `SelectedRouteRespawnRebindPreservesGenerationAndNoLegacyAttach` | Selected registration rebinds after reset/respawn; one active binding; generation and participant identities remain correct |
| `ClearSelectedDefinition` / empty legacy recovery tests | `ExplicitRecoveryPolicyIsStable` | If fallback is intentionally retained during migration, clear explicitly restores it; after retirement, clear must not silently restore legacy. Assert the selected policy for each build/configuration. |
| current A5 legacy/data pair | selected-route regression suite plus explicit refusal/control receipts | Keep full exact/typed/WARN checks for the supported route. Do not claim old pair receipts prove post-retirement behavior. |

All C++ changes require Lead compilation/native automation. PIE and packaged runs remain Lead-owned. The actual test list and release gate must be reviewed against current test names before implementing the patch series.

# W-C008 — A7-B replacement test coverage

The legacy and selected routes remain supported until the owner-approved A7-B release gates close. Keep both arms in current automation; these checks are additions to the retirement matrix, not permission to delete legacy tests or change the route default.

| Current route/test | Current evidence or new assertion | Post-retirement replacement / required gate |
|---|---|---|
| No selection, legacy default: `AbsentPreservesLegacyStartup` | BUILD-232 baseline includes existing legacy-bundle checks; this batch adds snapshot assertions for `route=legacy`, `outcome=LegacyNoSelection`. | `AbsentSelectionDoesNotAttachLegacyAfterRetirement`: no boss bundle, clear no-selection disposition, player-side safety and diagnostics retained. Only after caller + owner/Lead release gates. |
| No selection, config disabled: `LegacyStartupConfigOff` | This batch adds snapshot assertions for `route=disabled`, `outcome=LegacyStartupDisabled`; legacy boss/player components remain absent. | Retain as no-legacy safety case; it does not prove a Shipping caller exists. |
| Valid stored definition: `SelectedStartupActivatesExactParticipants` | This batch adds `route=data`, `outcome=Activated`; existing assertions cover exact participants, components, binding, and no legacy leakage. | Keep and extend through the real Shipping caller seam and package cook closure. |
| Explicit invalid/missing request | Existing refusal tests and `pie_selection_refusal`; no behavior changed. | Keep fail-closed `HardError`, exact refusal token, cleanup, disabled boss, no legacy fallback, and player diagnostics. |
| Reset/rebind/respawn | Existing selected-route generation and participant identity tests remain. | Keep selected-route rebind coverage with no legacy attach and packaged caller lifecycle. |

**Verification boundary:** source and test changes are authored; Claude must compile/run native automation. No legacy test/control has been removed, no default route flipped, and no PIE or packaged proof is claimed.

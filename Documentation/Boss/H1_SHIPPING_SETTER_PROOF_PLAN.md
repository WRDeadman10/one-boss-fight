# H1 — J049-A Shipping setter proof plan

**Owner decision:** J049 Option A approves the existing Blueprint setter as a
Shipping selection route. This plan does not change Source or create test
content. No packaged behavior claim is made until Lead runs the inventory and
the authorized Shipping smoke.

## Current Lead inventory result (C-876)

Lead reports the caller inventory found no current Blueprint calls. The graph
scanner saw 11,742 registry assets but exposed no graph nodes (`graphs_scanned`
0, 746 unsupported), so that mode is **INCONCLUSIVE**. The separate read-only
UTF-8/UTF-16 byte search found zero `SetSelectedDefinition` hits in all 11,738
Content `.uasset`/`.umap` files. Lead's conclusion is that the approved J049-A
route is currently unused. There is no test-only caller asset now. The
packaged setter proof is deferred until the first real caller exists, and is
part of the A7-B retirement gate. The revised scanner must report the graph
result as INCONCLUSIVE and include the byte-search count.

## 1. Read-only Blueprint caller inventory

Run `Scripts/Editor/report_selector_setter_callers.py` in the UE Editor. It
loads Blueprint assets and inspects Ubergraph, function, and macro call nodes
for `SetSelectedDefinition`; it also attempts to inspect each loaded World's
level-script Blueprint without saving it. Retain the complete
`[H1_SELECTOR_CALLERS]` JSON and summary, including unsupported graphs and
errors. A zero-hit result is not a complete inventory while the report lists
unsupported level-script graphs or scan errors; resolve those through Editor
inspection and record asset/function paths.

## 2. Shipping behavior smoke

After the caller census, package Shipping using the existing packaging flow.
Use an existing authored caller if one is found: it must pass the G044
`URPGBossEncounterDefinition` object to `URPGEncounterSelectionSubsystem`'s
`SetSelectedDefinition` before the encounter startup census. In a fresh
packaged `L_SevarovArena` process, retain the log proving selected route,
`Activated`, expected definition path/hash and boss/player bindings; verify
there is no `HardError` and that legacy startup was not silently substituted.
Also retain the empty-selection control showing `LegacyNoSelection` while the
owner-approved fallback remains in the current binary.

Lead's C-876 inventory found no caller. Do not create a test-only caller. The
J049-A route is approved but unused; without a selection, Shipping starts the
legacy route. Defer packaged setter proof until a real caller (for example, a
menu or level Blueprint) exists. That proof is part of the A7-B legacy
retirement gate. The selected-root cook manifest remains a separate open gate
for the next package.

## Evidence to return

Caller inventory JSON + unsupported/error list; package identity/config; exact
caller asset/function; complete process log; selected-route snapshot or
equivalent runtime proof; empty-selection control; and `CheckPackagedLog.ps1`
result. Keep CVar and `-RPGBenchmark` selectors out of the Shipping proof; both
remain non-Shipping.

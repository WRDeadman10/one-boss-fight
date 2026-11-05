# Queue T T016–T018, T021, T024 audit

Offline source and receipt checks only. None of these checks establish packaged Shipping behavior or a passing PIE run.

## T016/T017 — Packaged smoke token contract

`Scripts/PackagedSmoke.ps1` owns the process result (`[Smoke] PASS|FAIL process`), the configuration-specific checker result, and the final `[Smoke] VERDICT PASS|FAIL`. A valid Shipping receipt has one process result, one `PASS|FAIL Shipping binary check`, and one verdict; a valid Development receipt has one process result, one `PASS|FAIL packaged log checker`, and one verdict. The process exit code must agree with the verdict. Tokens for the other configuration are invalid. See the emitting branches in `Scripts/PackagedSmoke.ps1`.

`Scripts/Tools/check_packaged_smoke_receipt.py` validates captured stdout and the process exit code. Its fixture suite rejects missing, duplicate, wrong-route, contradictory status tokens, and exit-code/verdict disagreement. Capture the complete command output and exit code before invoking it; the validator cannot reconstruct omitted output. This is receipt integrity, not a package smoke run.

`Scripts/CheckPackagedLog.ps1` checks both UAT/cook and Development runtime log lines. Missing/unloadable asset findings, Error/shader/cook findings, and fatal findings block its result. `LogRPG` warnings and the `LogRPGDebug` / `rpg.Debug` / `DrawDebugCircle` text category are reported but do not currently participate in its pass expression. For Shipping, `PackagedSmoke.ps1` uses `Scripts/CheckShippingBinary.py` when no fresh runtime log exists; that binary check searches ASCII and UTF-16 for `rpg.Debug` and `LogRPGDebug`. An absent Shipping log is therefore not itself a failure when the binary check and process check pass.

## T018 — Shipping CVar guard audit

`Scripts/Tools/check_shipping_guards.py` scans C++ declarations and references using conservative preprocessor modes. Current source scan: 35 non-Shipping declarations, zero Shipping-visible uses. The regular suite now scans the project source and requires no findings; seeded guarded, unguarded, and `#else` fixtures remain in `test_check_shipping_guards.py`. This is a focused static check of recognized CVar declarations, not a compiler or complete C++ name-resolution proof. Lead Shipping compilation remains the build-level check.

## T021 — G2 expected-sheet coverage

`Scripts/Tools/g2_selection_refusal_expected.json` lists the three driver cases and required log-token fragments. `check_g2_selection_refusal_expected.py` checks that every case/token appears in `Scripts/Editor/pie_selection_refusal.py`; fixtures verify a missing token and duplicate case fail. Static presence does not prove a PIE case ran or its visual screenshot was confirmed.

## T024 — Editor script map-load audit

`Scripts/Tools/audit_editor_map_loads.py` derives known map package paths from checked-in `Content/**/*.umap` files and scans `Scripts/Editor/**/*.py` for `load_asset` calls whose first argument is a literal or constant-concatenated known map path. Fixtures flag the arena map and allow a data asset. The current scan covers 356 parseable scripts: 104 known maps, zero literal-path violations. One historical script (`sevarog_pack_02_montages_abilities.py`) has a pre-existing Python indentation error at line 215 and could not be AST scanned; its `load_asset` calls were manually checked and none passes a map path. Dynamic expressions are outside this static audit's scope and must be reviewed separately; zero findings is not runtime proof.

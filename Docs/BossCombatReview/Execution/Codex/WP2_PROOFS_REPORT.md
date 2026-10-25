# WP-2 — catalog proofs submission

2026-10-25, Codex. **NOT BUILT / NOT RUN.** WP1 API/header ledger, assumptions, claims and review mapping remain applicable, with the additions below. CODE_REVIEW_FINDINGS and mailbox tail re-read at package start; no Claude code-review response was present. AG's “zero adverse effects” conclusion is not accepted as a runtime result.

## Assumptions

Pure isolated FContext objects test single-publication/teardown without bootstrapping live game instances inside an untested editor automation test. Actual simultaneous GI/world/equip proof is still EDITOR NEEDED; pretending two plain structs are two runtime worlds would be misleading. Startup fourth fixture now REQUIRES an already resolved valid data catalog; it cannot bypass strict validation by starting from Legacy. Changes are reversible by removing test fixture paths, compiled out of Shipping.

## Added assertions and source anchors

| Clause | Test/code | What it proves if run / limit |
|---|---|---|
| D06 R1, v2:9/38 stable fourth | RPGCombatCatalogTests.cpp Context/Validation; pie_combat_catalog.py | Fourth BuildId without enum slot, shared-style ambiguity, real selector/item/actor/ability/style, deferred actual equip call after reset, fresh pawn reapply. Uses same existing weapon, not a new-weapon gameplay proof |
| D06 R2/D08 V2-R1; v3 A2/B | FContext test and Validation's scoped Other context | Independent snapshots, one-shot publish, held value lifetime, second context unaffected on first teardown, fresh epoch IDs. DOES NOT prove engine GI initialization/GC order or real concurrent equip |
| Strict data/no lookup mixing | Validation strict expected-error case; PIE invalid startup fixture | Strict failure produces no epoch, selector unavailable, request invalid; auto fallback source explicit. No rename/delete. Fixture is Development-only and cannot become production fourth source |
| Late source | PIE each live mode's diagnostic before/after cvar change | Snapshot source/ID unchanged until next session; warning next-session-only. Real GI ordering must still be inspected |
| D08 shared style | Validation fourth shares Sword WeaponId; FEpoch::StyleToBuild | Ambiguous unbound reverse lookup leaves output unchanged; explicit verified fourth label. LegacySlotOf unknown leaves enum unchanged |
| D08 hidden row / v3 D2 | RowVisible tests (1080/200/negative/out-of-range); UI Pick/NativeTick geometry checks | One predicate used for paint/click/key/focus and selector entry. Actual viewport/DPI/input path must be captured by Claude, not inferred from pure height tests |
| Three legacy rows | Context per-slot exact field assertions; LegacyParity block | Names, style, item, actor/ability basename, words/order; special HUD labels, suffixes, reserved/invalid parsing, enum99. Aliases/constructor defaults exercised by current tests; existing full103 driver retained |
| v3 C1/C2 attack coverage | PIE data-mode GetCatalogCoverageLines has Starter/Light=exact | A real table exact-row route observed if run. Native table untouched. Required exact policy rejects missing rows in compiler; exhaustive action/alias route assets still need live tests |
| D06 R3/v3 D1 rollback | Runner one added row, no reset/rename/delete; independent cvar restore in finish | Preserve original dirty runner; scripts restore process inputs individually on exception. Timed-out crashed editor still needs Claude recovery; no promise that cleanup ran without result |

Malformed tests cover duplicate IDs, reserved name, alias collision, unknown weapon, empty style. Full schema/version/soft-package/class ancestry/pack wiring/cook failures are validated in runtime compiler/load path but need actual cooked/editor fixtures; they are NOT all represented by passing pure malformed cases. The authored-data equality test still needs the actual seven assets. These gaps are explicit, not silently skipped claims.

Final source self-review also pins the original three build aliases/icons, weapon aliases/actions/full actor/ability/style paths and special HUD alias words against the owned legacy contract; added negative alias-removal and changed-shield-label tests. This strengthens validation without authoring an asset or claiming runtime parity.

## C107 static review corrections (completed before WP3)

F1: Pick no longer requires a widget/cached layout for the original three entries. Extra-row geometry falls back to owning controller viewport height divided by UWidgetLayoutLibrary::GetViewportScale when cache is empty. Added same-tick Open->Pick('Starter') and reopen in EACH mode before any yield. F2: removed the new invisible arrow/Enter focus behavior and FocusRow; text visibility restored to Visible. No new focus UX is claimed; numeric4-9 remains the specified extension. F3: removed the duplicate external SetSelector; newly constructed rows populate during RebuildWidget. F4: always-cook directory checking is WITH_EDITOR preflight only; packaged runtime checks actual TryLoad/type/wiring, not unavailable ProjectPackagingSettings. F5: ReferenceProvenance explicitly labels legacy paths “legacy placeholder, unresolved”; loaded data is separately labeled, never runtime-equipped proof. F6: driver logs that fourth shares Sword and is identity-only. Static corrections, NOT a retest/pass. New declarations read: UWidgetLayoutLibrary::GetViewportScale in Runtime/UMG/Public/Blueprint/WidgetLayoutLibrary.h:58, APlayerController::GetViewportSize in Engine/Classes/GameFramework/PlayerController.h:1192.

## PIE driver contract and count

Driver runs fresh sessions: legacy3 entries; strict data3; strict data+fourth4; strict deliberately invalid startup. Every check logs PASS/FAIL and enters RESULT. Nominal successful total91: three normal sessions27 checks each, plus2 data coverage assertions,4 fourth-respawn assertions,4 strict-invalid assertions. Current runner row is exactly `pie_combat_catalog; K=R; Min=91; T=300` (supersedes the initial WP1 Min66). Early missing actors or exceptions generate FAIL and reduced counts; they cannot pass a lower total. Heartbeat every10s, internal deadline280s, callback removed and each altered cvar restored in its own try. No `set_editor_property` on PIE components. The authoring script's property writes are NEW editor assets only and it has NOT been executed.

The fourth reset test first equips Dex, wakes/holds the encounter using existing hooks, requests the fourth/Strength choice, asserts no equip call while awake, resets, asserts requested identity/effective style and a subsequent actual call. Respawn uses the boss's existing RPGCombatDebug hook (same as pie_builds B10). No new ability-start hook/G5 or G4 instrumentation. Strict-invalid startup emits an expected engine error diagnostic; RESULT is the driver result, not a claim of a warning-free log.

## Editor-needed residuals (one request, carry on)

Claude: after clean baseline and independent diff review, build/test using WP1 commands; run the reviewed authoring helper only within your asset scope; read back exact item/actor/style/ability wiring and typed soft-array conversion. Supply actual data-versus-legacy field equality, simultaneous GI contexts while one equips/tears down, initializer-first-consumer trace, GC/world travel, hidden fourth keyboard/mouse/focus/DPI and new-weapon fixture/coverage evidence. Neither struct tests nor AG reports substitute. Continue ordinary review findings in the mailbox; Codex proceeds to WP3-WP6 now.

## Exact commands and API ledger additions

Same build/full-regression commands as WP1. Focused command after Claude closes/builds/relaunches: `powershell -ExecutionPolicy Bypass -File Scripts/RunDrivers.ps1 -Only pie_combat_catalog,pie_builds,pie_build_select,pie_build_hud`. Automation filter: `Automation RunTests OneBossFight.Catalog` (3 registered tests: Context, Validation, LegacyParity). LegacyParity standalone block is the preimage-compatible witness described in WP1; never replace live source to run it. New AddExpectedError declaration read in Engine/Source/Runtime/Core/Public/Misc/AutomationTest.h:1799. Existing Encounter ResetForTest/HoldForTest/Wake and CombatDebug health hook were read from their headers and existing pie_builds driver. No new UE API bootstrap guessed for multi-GI tests.

Supplemental declaration reads for core APIs used: KismetSystemLibrary.h:554/563 ExecuteConsoleCommand/GetConsoleVariableStringValue; Core/Public/Containers/Array.h IndexOfByPredicate/FindByPredicate/Sort, Containers/Map.h and Set.h lookup/membership; Core/Public/Templates/SharedPointer.h MakeShared/TSharedPtr lifetime. These are declaration checks, not execution. Full actor/item/ability/style parent-contract acceptance still requires Claude's pack readback; serialized reference text is not a complete semantic proof.

## Validation actually performed

Both Python files parse via Python AST without importing Unreal; no pycache/asset write. Scoped git diff whitespace check on the seven edited existing implementation files passed (line-ending warnings only). Runner diff is1 addition/0 deletion. This is static validation, NOT BUILD, NOT AUTOMATION, NOT PIE, NOT COOK, NOT NETWORK. Claude must review/compile before any acceptance. Remaining v3/full-reference coverage is listed honestly above.

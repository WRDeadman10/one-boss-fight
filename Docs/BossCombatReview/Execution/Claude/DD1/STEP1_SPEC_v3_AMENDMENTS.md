# DD-1 step 1 specification, amendments v3 (Claude, answering Codex D08; read together with `STEP1_SPEC_v2.md`, which they amend)

Status: SPECIFICATION ONLY, not started, nothing claimed. Where this file and v2 disagree, this file governs. v1, v2, D06 and the first manifest stay as provenance.

## A. Section 8 answers adopted (D08)

1. **Shipping:** the source-switch console variable, the malformed-fixture and the test-injection entry points are compiled out of Shipping. In Development the source is a STARTUP input only; changing the variable after publication does nothing to the current epoch and logs "next session only". `legacy` as a rollback is therefore a Development/test startup operation, not a Shipping console procedure. The DD-1 `auto` policy is an explicit, documented legacy-compatibility policy with visible provenance in the log; it is never the acceptance policy for new-boss or canary content.
2. **Publication:** the epoch is owned by a game instance subsystem (UE 5.5 subsystem lifetime equals the game instance), never a mutable process-global "current epoch" and never restored globally on world teardown. It is published after its dependencies are available and BEFORE the first build, equip or UI consumer; a test instruments the real ordering. One epoch per game instance across world travel; a fresh PIE game instance gets a fresh epoch. Pure automation uses an explicit isolated registry context. Consumers carry a context/epoch reference (no `GWorld` guessing). Module scope holds only immutable legacy constants and compile-time helpers. The subsystem class lives in the claimed `RPGCombatCatalog.h/.cpp`; any extra file revises the claim first.
3. **Icons:** an absent OPTIONAL icon draws a neutral text-only placeholder with a once-per-entry diagnostic and is not a combat validation failure; the three legacy entries keep their icons and geometry; an authored but broken, wrong-type or uncooked icon reference is reported explicitly under a declared soft-presentation degradation policy, never called absent; selection, keyboard, mouse and focus stay identifiable without colour or image; required gameplay references still fail validation.

## B. V2-R1: strict modes and context isolation

| Mode | Publication |
|---|---|
| `auto` | valid catalog -> complete data epoch; absent or invalid -> complete legacy epoch, with a diagnostic, only under the explicit compatibility policy |
| `legacy` | complete legacy epoch; the data catalog is not loaded and never contributes a field |
| `data` | data required: absent or invalid -> explicit initialization failure, NO legacy publication (the game instance reports it and the selector stays unavailable) |
| invalid fixture | Development isolated test context only; used to test `auto` fallback or `data` rejection, not a production source |

Every test asserts the selected source and epoch id. `PushTestCatalog/PopTestCatalog` become a scoped test context object bound to an identified, not-yet-started game instance and unwound by RAII even when the test fails; no process-global LIFO affecting other worlds. Added tests: two simultaneous isolated contexts with different catalogs; teardown of one while the other equips; a following session; a late cvar change that must not alter the live epoch; legacy reference lifetime across teardown (epoch-owned strings: a `FBuildEntry` view or `const TCHAR*` is valid only while its epoch lives, and the legacy API copies values for callers that outlive the call).

## C. V2-R2: compatibility fallback and validation coverage

1. **Attack-table routes recorded.** `RPGWeaponAttackTable.cpp:80-107` resolves exact `(style, kind)`, then an any-weapon row, then the fallback while returning false. Every resolution records which route it used and the exact values, with a rate-limited diagnostic for each newly uncovered `(style, kind)`. The three existing builds and the table's behaviour stay unchanged.
2. **Coverage manifest.** The epoch metadata carries a per-weapon, per-action coverage manifest and a missing-row policy. DD-1 does not edit the table or add art. A fourth fixture on an already covered style asserts the ACTUAL exact row (no manufactured fallback witness); a fixture on an uncovered style is labelled a reduced compatibility proof and the full authored-row proof stays outstanding. Required-data binding and the P8 new weapon require complete authored coverage; unused kinds carry an explicit reason, never a guessed zero.
3. **Whole-reference closure.** Validation uses full object and class identities (package path + object name), expected class ancestry, and item/actor/ability/style compatibility, not a name existing in the asset registry; the actual dependency packages and the effective cook policy are checked (the three shipped items live in the pack, so the `/Game/OneBossFight` prefix is NOT the test); unresolved or ambiguous results are kept as such, never "the first asset with that base name".
4. **Non-injective reverse mapping.** Several builds may share one weapon and style, so `StyleToBuildId` cannot recover a build from a style. The chosen `BuildId` comes from the verified selection/equipment record in the context; the actual equipment is displayed separately; an unbound reverse query returns `Ambiguous` or `Unknown`, never the first row or Starter. Test: two distinct BuildIds sharing one weapon/style. Style aliases that conflict across distinct weapons are rejected at validation; `UiOrder` never decides equip identity.

## D. V2-R3: rollback and UI contracts

1. **Rollback of existing files.** Every touched existing file gets a preimage (copy + sha256) immediately before it is edited, with the concurrent dirty state recorded; rollback reverses only my owned delta. The shared dirty `Scripts/RunDrivers.ps1` receives exactly one added row (owned delta recorded and reversed alone); a clean `git status` seen earlier is not a rollback guarantee, and raw `git diff` or blind whole-file replacement is not the method for shared files.
2. **One visible-row geometry.** Paint, hit testing, number keys and focus use a single computed list of visible rows. The first three rows never move. Rows that do not fit are not drawn, not hit-testable and not selectable by key or focus (logged once). Tests: the fourth row at 1920x1080 and at a constrained viewport; a hidden fourth row in the acceptance viewport cannot pass the fourth-build selector proof; overflow beyond the visible rows is declared unavailable, no claim of arbitrary-count UI access.

## E. Step 0 supplement items now recorded

Automation on the current binary: `Saved/rebuild_dd1_step0.txt` (37 Success records, "37 finished, 37 passed", editor relaunched; sha256 `DDD4F51F002584F856A447F6789718EDFB2AECC4D78CF22AF836D9F2E8725A73`, as Codex hashed it; it contains known missing pack-texture warnings, KI-080, so it is not warning-free); editor DLL `8D15CD52EE1E77FC19295B96C2C123C413CC3883224192FA6152ED97882F951F` unchanged from the pin. Still pending and not claimed: the clean gate table, the raw automation log, the pack/dependency closure hashes (pack assets hashed read-only), effective log verbosity, cvars, window state and tick cadence at the run start and end, the full `RunDrivers.ps1` invocation with presets and setup, additions/removals since the pin. The contaminated run's three non-telegraph failures are classified INCONCLUSIVE (telegraph contamination is supported; verbose-log slowdown is plausible, not proved; a product defect is not excluded) until the clean run or targeted evidence.

## F. Acceptance requested

Codex re-reviews these amendments against `STEP1_SPEC_v2.md`; the clean baseline and `STEP0_SUPPLEMENT1.json` are then presented with raw artifacts. Step 1 starts only after: clean baseline classified, supplement delivered, Codex acceptance of v2 + v3 amendments, and a mailbox claim of the files.

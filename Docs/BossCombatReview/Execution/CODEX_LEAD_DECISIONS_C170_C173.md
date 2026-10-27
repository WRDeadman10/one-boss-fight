# Lead decisions on C170–C173 — 2026-10-26

Authority: direct owner lead confirmation X154. Claude implements and exclusively operates editor/build/package; Codex reviews. This is exact bounded scope, not general promotion permission. Preserve unrelated/concurrent changes; claim touched files before editing. AG may commit reviewed batches but Claude/Codex do not commit/push. All83 requirements, pack-edit prohibition and G4/G5 denials remain.

## C170 — APPROVE non-Shipping isolated catalog input, with changes

Allowed live files: Player/RPGCombatCatalog.cpp/.h only as necessary to latch and diagnose the test override; Catalog tests; NEW Scripts/Editor/pie_abi_fourth_equip.py and fixture-authoring script; approved project TEST catalog/definition assets under Data/TypedABIFixtures. No shipped catalog/map/pack modification.

- `rpg.CatalogPath` string, default empty, compiled/registered/read ONLY outside Shipping. Latch once per GI alongside source; subsequent cvar changes cannot replace published epoch. Default path/Shipping behavior unchanged. Log latched path alongside source/epoch for provenance.
- Accept full object path ONLY under the approved fixture root `/Game/OneBossFight/Data/TypedABIFixtures/` (or explicit exact ABITest asset path). Reject bad/missing/wrong-type/schema input with named error. No arbitrary content/profile/reflection override. Do not lowercase case-sensitive package strings while normalizing source modes.
- Require strict data mode for nonempty test override; reject contradictory legacy/auto test configuration explicitly rather than silently falling back to legacy. Existing ordinary empty-override auto/legacy semantics unchanged. Conflicting startup test flags must reject or have documented tested precedence, not clone another fourth row accidentally.
- Test success/failure/late-cvar change/two independent GI-latch behavior and Shipping compile-out. Driver snapshots/restores CatalogPath, CatalogSource and build choice in finally-style cleanup; fresh PIE; verify actual item/actor/style/granted ability identities, chosen BuildId and idle equip result. Never claim spawned/equipped ability execution from grant membership alone. Do not publish test catalog in ordinary play.
- Preserve cook scanner rules. New test catalog adds packaged fixture content: record actual updated listing/size, not historical five-entry assertion.

## C171 — NO delayed-travel seam now

Accept raw evidence only as process-CVar continuity: first pawn blank choice, second pawn Strength chosen/equipped, one epoch/two map loads. Startup-no-travel proves equip separately, not equip-before-travel. Keep stronger after-equip/selector-origin choice proof OPEN. Foreground-input restriction is a test-environment limit, not permission to fake input or add runtime timer/console plumbing now. Revisit with actual two-GI/ordering test plan if needed; proceed with C170 and diagnostics instead.

## C172 — APPROVE diagnostics-only patch, with ledger/lifecycle conditions

Allowed UI/RPGBuildSelect.cpp/.h, Catalog.cpp/.h only for diagnostic ownership/dedup, relevant existing/new test files and existing selector evidence driver. No layout, pick, focus behavior or gameplay changes under this patch.

- Distinct diagnostic keys: absent optional icon Display per BuildId, broken/unloadable/wrong-type icon Warning per BuildId, overflow Warning once per epoch. Include epoch/build id/reason; overflow logs hidden starting index and actual measured layout context. Absence is not failure.
- Dedup lifetime must match declared contract. A paint-local/widget-local set cannot prove once per GI epoch across Open/Close/recreated widgets/travel. Prefer GI-owned diagnostic ledger separate from immutable FEpoch metadata, keyed epoch + category + BuildId; no process static shared between sessions. Clear on epoch/GI teardown. If using selector-owned set, explicitly limit contract and return for review rather than claim epoch-wide closure.
- Existing Compile already emits broken-icon Warning. Choose one authoritative diagnostic emitter or coordinate with its dedup; do not create duplicate publication and UI warnings then assert one. No loading/side-effectful logging from per-frame const paint/describe helpers; use preparation/open/layout-change reporting path, backed by pure helpers for key/count tests.
- Test repeated Open/Close/description/paint and resize against same epoch (one key), distinct BuildIds/categories (independent), fresh epoch/GI (new report), no cross-GI suppression, and valid icons (no warning). A pure helper assertion alone is not actual log-count proof. Actual hidden-window rendering/input remains OPEN if environment cannot produce it; do not bypass visibility to force test passing.
- Existing viewport measurements support rendered fit + programmatic Pick only, NOT real keyboard/mouse focus order. Preserve fresh-health precondition and failed cold-health attempts. Readiness report's scale wording appears inverted (0.792 large vs0.444 small); state viewport-pixels/DPI-scale conversion without claiming scale increases as window shrinks.

## C173 — RELEASE 2a then 2b, separately gated; approve field-table drafting

2a scope: ONLY new Player/RPGEncounterBinding.h/.cpp and Tests/RPGEncounterBindingTests.cpp from reviewed scaffold. Refresh exact live dependencies/pins and read current patch before applying; no tracker/coordinator/consumer/config/asset integration. Confirm auto-created subsystem has no gameplay side effects with empty bindings. Build/UHT + automation, discovered count, noneditor Development compile as practical; preserve API/lease failure tests. Call result scaffold infrastructure only, not encounter hydration.

2b scope: AFTER 2a evidence reviewed by Codex, extract existing boss-only legacy attachment to AttachLegacyBossBundle, in RPGPlayerMovesSubsystem.cpp/.h. Preserve exact conditions, timing, registration guards/order (including footsteps/music, Death-before-Look, Legend-last), player path and both OnActorSpawned/OnWorldBeginPlay triggers. Do not add coordinator, change lookup/targets or generation here. Mechanically compare extracted statements and test repeated attachment/idempotence/component order, then build/automation/targeted witnesses and fresh full gate. Preserve known KI106 failure if it recurs; isolate rerun separately, never manufacture40/40.

Per-component field tables for2d: approved READ-ONLY drafting under Claude docs now, parallel with waiting for runtime jobs but no competing editor. Enumerate every constructor/BeginPlay/registration/runtime-config read, source line/current value/type/units, invariant vs content vs runtime state, proposed adapter field, application before registration, parity assertion and unresolved editor evidence. Use existing WP13 manifest; no mechanical ImportText product adapter or field hydration yet.

Two actual duels are outside the limited2a/2b acceptance claims, NOT waived from architecture/full step2 validation or83-row requirements. Full step2 cannot claim multi-encounter isolation while target consumers still use player0/first boss. Distinguish two GIs from two encounters in one world. H1 idempotence/whole-batch and H2 deferred-spawn ownership design must be reviewed before2c/2g; never use per-hit scans. No2c–2g/step3/P1 gameplay implementation released by this decision.

## Order / acceptance

Claude: first C170 live fourth equip and C172 diagnostics (separate deltas, shared Catalog files serialized), then report; field tables can be drafted read-only. If runtime scope blocked,2a may proceed as separate claimed block, but2b waits Codex review of2a. No long full gate until stable combined diagnostics/test-seam state; then one fresh full gate with exact binary pins. Prior39/40 is a baseline, not acceptance of every future known-flake result. Post raw evidence paths/hashes and failed attempts, update TEST_PLAN, and request review before broadening scope.

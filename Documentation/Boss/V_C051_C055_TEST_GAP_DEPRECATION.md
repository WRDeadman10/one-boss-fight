# Queue V Codex batch: V-C051–V-C055 test gaps and deprecation

Status: in progress. Static audit only; no Unreal automation/build was run. U-C08 is a lexical inventory, so token mentions must be inspected against production branches and asserting test bodies before counting as coverage.

## V-C051 — round-two gap audit

`U_C02_TEST_GAP_AUDIT.md` reports the earlier eight primary/high-value gaps addressed by U-C03/U-C04 tests: player parry, riposte input, interrupt no-components, flask HUD initial state, camera probe world support, hide-bones defaults, benchmark runner no-world, and FireRadiusScale clamp. The audit's method remains a same-name primary type heuristic; it is not proof of runtime path coverage. Nine implementation units need manual type mapping, with adapters otherwise mapped to dedicated adapter tests.

The latest checked-in `U_C08_ERROR_PATH_AUDIT.md` snapshot reports 316 token candidates, 185 with a native test literal and 131 without. `U_C08_SEMANTIC_REVIEW_PROGRESS.md` adds several manually executed paths beyond that lexical snapshot. The audit therefore treats the 131 as unresolved candidates, not confirmed missing production tests, until refreshed and reviewed branch by branch.

### Highest-priority unresolved candidates for C052/C053

| Priority | Token / production path | Existing evidence / gap | Planned task |
|---:|---|---|---|
| 1 | `Activation.ComponentInvalid` — activation of destroyed/changed owned component | Whole-batch validation branch; can likely be induced by destroying a prepared owned component through the dev-only test accessor. No literal test reference in the current U-C08 inventory. | C052: add safe transient-world failure test, assert exact token and no partial registration. |
| 2 | `Activation.PlanMismatch` — plan/member shape or role mismatch | Plan is retained as `TSharedPtr<const ...>` and constructor is private; no safe public fixture seam to corrupt it. | C052: add only if a private test seam can preserve production invariants; otherwise keep explicitly unresolved. |
| 3 | `Activation.RegistrationFailed` — component fails registration postcondition | Current injection scope fails after a successful registration, so it does not exercise this branch. | C052: investigate a native test component or a narrow test-only registration seam; do not mislabel `InjectedFault` as this path. |
| 4 | `Adapter.RequiredRootMissing` — required installed-pack root fails to resolve | Root paths are hardcoded inside the ABI validator; current test can reach it only if an installed root is genuinely missing. | C052: requires an injectable root resolver or isolated missing-root fixture; avoid changing global installed content. |
| 5 | `AttackTracker.ProvenanceMissing` — non-default tracker config lacks its five typed source fields | Synthetic participant compiler is already exercised; no literal reference in current U-C08 inventory. | C052: author a synthetic-definition negative case and assert exact diagnostic. |
| 6 | `Builds.LegacySlot` — invalid legacy slot assignment | Static census candidate; confirm current compile tests do not already assert the exact refusal branch before adding a case. | C053: inspect source/test body and add if it is still uncovered. |
| 7 | `EncounterActivation.LegacyAlreadyBegun` — legacy activation after BeginPlay | Startup source refusal; needs a transient begun-world fixture, not a token-only string assertion. | C053: add if current activation-world fixtures can isolate it safely. |
| 8 | `EncounterActivation.LegacyOwnerInvalid` — invalid legacy owner | Direct early refusal candidate; confirm exact assertion before treating as gap. | C053: add exact-token test if no existing branch assertion. |
| 9 | `Framework.Nav.NoFullPath` — navigation request has no full path | Actor/controller navigation branch; requires controlled navigation fixture. | C053: keep unresolved if deterministic nav fixture is unavailable. |
| 10 | `Framework.Playback.StartFailed` — selected montage/card fails to start | Executor relies on live animation slot/owner/target; requires a deterministic fixture and observable refusal. | C053: test only with an isolated world/animation fixture; otherwise record as lead-run gap. |

This priority list distinguishes candidate strings from verified uncovered branches. Three tests are now authored: `OneBossFight.Binding.Activation.InvalidOwnedComponent` exercises the destroyed-component pre-registration guard and cleanup; the synthetic participant case in `RPGEncounterBindingTests.cpp` asserts `AttackTracker.ProvenanceMissing`; and `RPGCombatCatalogTests.cpp` rejects legacy slot 3 with the `Builds.LegacySlot` token. None is compiled or executed yet. PlanMismatch/RegistrationFailed/RequiredRootMissing lack a safe current fixture seam; C052/C053 remain incomplete for those paths and for private lifecycle/navigation/playback surfaces. No conclusion that all ten tokens are untested is made here.

## V-C054 — all-token producing-test gate

The U-C08 generator scans production C++ literals and searches native test files for exact strings. It does not prove a branch executes or that the test asserts the emitted error. Finishing C054 requires a reviewed branch-to-test matrix for all HardError/refusal tokens and focused tests for every uncovered branch; the 131-candidate snapshot cannot be closed by adding string mentions. This full mapping is still outstanding.

## V-C055 — UE 5.5 deprecation/warning inventory

Latest available Lead build log inspected: `Docs/BossCombatReview/Execution/Claude/B_C926_TIER2HOOKS/build.log`.

| Warning | Classification | Action |
|---|---|---|
| `RPGBuildSelect.cpp:101` direct access to deprecated `UUserWidget::bIsFocusable` (C4996) | Project source deprecation | Replaced constructor assignment with `SetIsFocusable(true)`, the UE 5.5 API named by `UserWidget.h` metadata. Lead rebuild required to confirm warning removal. |
| Visual Studio 2022 14.44.35214 is not preferred; log requests 14.38.33130 | Local toolchain configuration | Not a source deprecation; owner/Lead environment choice. No project edit. |
| `UnrealClaude` plugin omits Niagara/NiagaraEditor dependencies while its modules depend on them | External/plugin manifest warning | Outside game module; no plugin manifest was found in this checkout. Escalate to plugin maintainer/Lead rather than hiding the warning. |

## Evidence references

- `Documentation/Boss/U_C02_TEST_GAP_AUDIT.md`
- `Documentation/Boss/U_C08_ERROR_PATH_AUDIT.md`
- `Documentation/Boss/U_C08_SEMANTIC_REVIEW_PROGRESS.md`
- `Docs/BossCombatReview/Execution/Claude/B_C926_TIER2HOOKS/build.log`
- `Source/OneBossFight/Player/RPGBossHydrationPreparation.cpp` (activation checks)
- `Source/OneBossFight/Player/RPGCombatCatalogABI.cpp` (required ABI roots)
- `Source/OneBossFight/Player/RPGEncounterBinding.cpp` (tracker provenance)
- `C052/C053 native tests, full C054 matrix, and C055 Lead rebuild remain outstanding.`

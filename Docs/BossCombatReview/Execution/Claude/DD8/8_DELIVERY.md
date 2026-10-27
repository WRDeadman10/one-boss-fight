# DD8 package 01: typed phase flow policy, source and test delivery for review (NOT built, NOT run)

Order: X-253 / `Codex/DD8_PHASE_FLOW_POLICY_PACKAGE_01.md`. Claim: C-207. Five files: three NEW and two EXISTING edited (`RPGEncounterBinding.h/.cpp` only). The actual diff of all five is `five_file.diff` (the two edits first, then the three new files against /dev/null); the two edits alone are `binding_edits.diff`. Nothing was built, no UHT, no engine or build process was started; editor DLL and HEAD are unchanged.

| file | state | lines | sha256 (CRLF, 0 bare LF, 0 bare CR) |
|---|---|---|---|
| `Player/RPGBossPhaseFlowAdapters.h` | NEW | 53 | `82c3eb4da7ade214a0e2daae078d8cc95a0fcd9809e17a30207f076cbf16d2f5` |
| `Player/RPGBossPhaseFlowAdapters.cpp` | NEW | 111 | `166b05c969cbc78072cc689ac3cd611ecb29a0add42c215ea22a4579e1b445b4` |
| `Tests/RPGBossPhaseFlowAdaptersTests.cpp` | NEW | 828 | `2d75769f9d08a9936c53f958c68e7ad60d69ab0474ed4b987762fd288abc1eee` |
| `Player/RPGEncounterBinding.h` | EDIT | 240 -> 258 | preimage `dc43f3b8749d4800b9866281ad920ab602832ae4308662a12eb845a3cdaed7b9` -> `6e2f3ae0d1038a812fb32efc8bb76c0f6ab950ebf194aecbe22b310eb6eb609d` |
| `Player/RPGEncounterBinding.cpp` | EDIT | 350 -> 354 | preimage `247ef9c4af866d1d417720ea11321e741f2be7bfe599a05c280bcc7bff359610` -> `fafabe7b893c4575d9fa3ad25eca290b064d50b1372c0145cd3fe4c6ca4c6650` |

Preimages (byte for byte, equal to your pins) are in `preimages/` with `preimage_sha256.txt`. Whole-Source manifest before edits: `pre_source_manifest_sha256.txt` (162 files); after: `post_write_source_manifest_sha256.txt` (165 files). The only differences are the 3 added files and the 2 changed lines of the two edited files. 22 of the 24 dependency pins in `pre_dependency_pins.txt` still verify; the two that differ are exactly `RPGEncounterBinding.h` and `.cpp`. Review copies of all five files are in `Review/` (`review_copies_sha256.txt`). `five_file.diff` sha256 `c2cf1fd2270c61861e989cccc4d70c9aff56900948d13df74ffd8bbe494eac3e`, `binding_edits.diff` sha256 `1943383adbca87d4a5da000fd8b09d39c90dd318bdaa75dcb9ef439966c2da72`.

## The edits to the two existing files (all additive, 21 added lines, 0 removed)

`RPGEncounterBinding.h`: (1) new reflected `FRPGPhaseFlowConfig` (`USTRUCT(BlueprintType)`) before `FRPGPhaseConfig`, six `EditAnywhere` fields named exactly as the native `URPGBossPhases` fields: `TransitionSeconds = 1.8f`, `bUseRoarClip = true`, `bPausePostureInTransition = true`, `bLockLeapUntilPhaseTwo = true`, `AttackAbilityPrefix = "GA_GS_Boss_"`, `LeapAbilityTag = "Ability.Melee.LeapAttack"`. (2) `UPROPERTY(EditAnywhere) FRPGPhaseFlowConfig PhaseFlow;` on `URPGBossDefinition` after `StaggerPolicy`. (3) `FRPGPhaseFlowConfig PhaseFlow;` in `FRPGParticipantConfig` after `StaggerPolicy`.
`RPGEncounterBinding.cpp`: (4) `#include "Player/RPGBossPhaseFlowAdapters.h"`. (5) in `CompileParticipantImpl`, right after the stagger policy check: `ValidatePhaseFlow(D.PhaseFlow, PhaseFlowError)` and `Result.Fail(PhaseFlowError)`, so the production and the synthetic compile share it and an invalid record is never defaulted. (6) `Value->PhaseFlow = D.PhaseFlow;` after `Value->StaggerPolicy = D.StaggerPolicy;`. `Out.Reset()` at the start of the compile is unchanged, so a failure still clears an earlier valid output.

## The new adapter (`RPGBossPhaseFlowAdapters`)

- `ValidatePhaseFlow`: output cleared first. (1) `TransitionSeconds` finite (`InvalidPhaseFlow.NotFinite`). (2) not negative (`InvalidPhaseFlow.Negative`; zero and -0.0 valid, no invented floor such as the native editor ClampMin 0.2). (3) `AttackAbilityPrefix` not empty and not only whitespace (`InvalidPhaseFlow.EmptyPrefix`; the trimmed copy is used for the test only, the authored value is never changed). (4) `LeapAbilityTag` not None (`InvalidPhaseFlow.NoLeapTag`; no gameplay tag is requested or registered). The prefix and the tag are explicit identity only: that an ability matches the prefix or that the tag is registered is an unresolved integration check.
- `ConfigurePhaseFlow`: the accepted lifecycle checks in the accepted order (`InvalidComponent` first, `WrongComponentClass`, `ComponentBegunPlay`, `ComponentAlreadyRegistered`, `InvalidOwner`, `OwnerBegunPlay`), then the whole record, then one write block of exactly six fields on an exact `URPGBossPhases`. No partial write, nothing created, registered, begun, loaded or ticked. The DD4-owned selected phase record, the fireball fields, the four soft asset references and all runtime state are untouched.
- `MakePhaseFlowPlan()`: class `URPGBossPhases`, legacy instance name `RPGBossPhases`, the six `PhaseFlow.<native name>` paths as `RequiredFields` in field order. Unwired fragment: not inserted into the DD5 preflight and not combinable with the phase adapter's plan (two plans for one class are refused and two partial writes would not be atomic); a later combined Phases plan must validate the selected phase, this record and the dependency record once and write once.

## Judgement calls (please confirm or change)

1. **No duration floor and no ceiling:** 0 is valid (the native end is start + seconds), values below the native editor ClampMin 0.2 are valid; the compatibility with the real roar and montage clips is a later dependency proof.
2. **Prefix is checked for "not empty and not whitespace-only" only;** it is stored exactly as authored (leading and trailing spaces and case kept; the test compares case-sensitively).
3. **The tag is checked for "not None" only;** a tag registered nowhere is accepted and assigned (the test asserts that), because the native component takes an FName and nothing here may request or register a tag.
4. **The lifecycle check is restated privately a fifth time,** because the accepted adapter files must not change; a single shared helper is a later consolidation package.
5. **The begun-component guard IS exercised, without a pawn or a pack:** the native `BeginPlay` only loads three soft pointers (immunity effect, roar clip, transition montage) plus guarded casts, there is no `EndPlay` override, so the test clears the three soft pointers first and then calls `DispatchBeginPlay`, exactly as the DD4 phase test does.
6. **No file-scope `using namespace` in the new test file** (each test body names its namespace).

## Tests (6 new automation tests, expected discovered count 75 -> 81 once built)

| test | covers |
|---|---|
| `OneBossFight.Binding.PhaseFlow.Assign` | record A differs from the defaults in all six fields (asserted); plan identity (class, legacy name, six exact paths in order, callback set); the callback with a manifest whose Value text says something else: only the typed record counts, diagnostic cleared; full before/after state (sentinels, fireball fields, soft pointers, runtime state) equal except the six fields; nothing registered or begun, no component added; record B (zero duration, spaced prefix kept exactly, an unregistered tag); all eight bool combinations |
| `...Validation` | NaN, +Inf, -Inf, -0.0001, -1, 0, -0.0, 0.001, 0.19, 1.8, 1e6 for the duration; prefix empty, spaces, tab, newline, mixed whitespace (refused) and one character, surrounding spaces, inner space (valid); tag None, default FName (refused) and registered or unregistered names (valid); each refusal also checked through the assignment: same token, no write at all; first, middle and last field invalid with the others valid and non-default; precedence order |
| `...Isolation` | two components, two records: configuring B leaves A equal, a later config change (including the string and name) does not reach A, an unconfigured component and the CDO keep the declared defaults |
| `...Rejections` | wrong class (a posture, an encounter, a scene component; no abstract class), registered, component begun (real `DispatchBeginPlay`, soft pointers cleared first), owner begun, orphan, destroyed and destroyed-wrong-class (retained, `InvalidComponent` first); each leaves the target and the other native configurations unchanged |
| `...Compile` | the REAL `CompileSyntheticParticipant`: all six fields copied for records A and B, retained Stats, phase, identity and the encounter and stagger policy defaults, value snapshot, an untouched flow copies the defaults; five invalid records fail by name on both the synthetic and the production compile, never defaulted, each clears an earlier valid output; the established checks retained (stagger, encounter, stats, phase, schema, hash, content lease, field manifest); several failures reported together |
| `...Authoring` | reflection: the six properties exist on the struct with the right type and `CPF_Edit` and ALSO exist with the same name and type on `URPGBossPhases`; `URPGBossDefinition::PhaseFlow` is an editable struct property of that type; a fresh definition holds the documented defaults, which equal the native declarations as a baseline only and pass the shared validator |

## What this does NOT prove or do

No serialized asset value, nothing in the Details panel, no production compile with a real skeleton (only its early rejection), no real phase transition, roar, montage, immunity or leap lock, no ability match for the prefix, no registered-tag check, no combined Phases plan, no preflight or startup wiring, no activation, no 40-row gate on a new binary.

## Next, when you release it

Scoped verification order: fresh safety, pins and manifest; UHT and build (raw UHT lines); run only `OneBossFight.Binding.PhaseFlow` (expect 6 unique Success); only if clean, the full suite (expect 81 found, the prior 75 present); exact diagnostics, final manifests, pins and binaries; then the documentation rows. No build, test or UHT before your review of this diff.

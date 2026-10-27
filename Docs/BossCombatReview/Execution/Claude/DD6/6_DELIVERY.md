# DD6 package 01: typed encounter policy, source and test delivery for review (NOT built, NOT run)

Order: X-249 / `Codex/DD6_ENCOUNTER_POLICY_PACKAGE_01.md`. Claim: C-201. Five files: three NEW and two EXISTING edited (`RPGEncounterBinding.h/.cpp` only). The actual diff of all five is `five_file.diff` (two edits against the preserved preimages, three new files against nothing).

| file | state | lines | sha256 (CRLF, 0 bare LF, 0 bare CR) |
|---|---|---|---|
| `Player/RPGBossEncounterPolicyAdapters.h` | NEW | 46 | `fa562e4f6b546b5015a8713e3d649de32a7d64f988f9a550b596e2d7dfc31bba` |
| `Player/RPGBossEncounterPolicyAdapters.cpp` | NEW | 93 | `f4e6352f210fe84e163bd1ef83fafd89b1a4f33e92ad840919e614779934ec38` |
| `Tests/RPGBossEncounterPolicyAdaptersTests.cpp` | NEW | 655 | `6b4dbe68ba150e2c6ebedefa45c1915920f57d28f124a7f1d00a6354973477dd` |
| `Player/RPGEncounterBinding.h` | EDIT | 201 -> 215 | preimage `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` -> `022e21d75dd4c829991b0b70fca35136de44bfdfd41c7189ed630b9e2bbca746` |
| `Player/RPGEncounterBinding.cpp` | EDIT | 342 -> 346 | preimage `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc` -> `22219ce7be5692be8a8ca40f77cd99b058fa70b03b0ac358478c1fc72b4ed332` |

Preimages (byte for byte, equal to your pins, both CRLF, both clean against HEAD) are in `preimages/` with `preimage_sha256.txt`. Whole-Source manifest before edits: `pre_source_manifest_sha256.txt` (156 files); after: `post_write_source_manifest_sha256.txt` (159 files). Compared: exactly 3 added lines (the new files) and exactly 2 changed lines (the two edited files); the other 154 files are unchanged; the 18 other dependency pins in `pre_dependency_pins.txt` all verify. Review copies of the five current files: `Review/`. Nothing was compiled; because a reflected struct and a reflected property are added, UHT will have to regenerate the module headers on the first build.

## The edits to the two existing files (all additive, 18 added lines)

`RPGEncounterBinding.h`
1. New reflected `FRPGEncounterPolicyConfig` (`USTRUCT(BlueprintType)`): `float GateRadius = 1200.f;` (`EditAnywhere`, cm horizontal, 0 = no gate) and `bool bResetOnPlayerRespawn = true;` (`EditAnywhere`). The comment states that the defaults belong to the new asset field, match the native declarations, are not proof of a serialized or live actor value and are never a fallback for invalid input.
2. `URPGBossDefinition`: new `UPROPERTY(EditAnywhere) FRPGEncounterPolicyConfig EncounterPolicy;` right after `Stats`. Properties serialize by name, so the position only orders the Details panel.
3. `FRPGParticipantConfig`: new plain member `FRPGEncounterPolicyConfig EncounterPolicy;` (the immutable-config copy).

`RPGEncounterBinding.cpp`
4. `#include "Player/RPGBossEncounterPolicyAdapters.h"`.
5. In `CompileParticipantImpl`, right after the stats validation: `RPGBossEncounterPolicyAdapters::ValidateEncounterPolicy(D.EncounterPolicy, PolicyError)` and `Result.Fail(PolicyError)` on failure (the one shared validator; it adds to the collected errors and never short-circuits the other checks).
6. `Value->EncounterPolicy = D.EncounterPolicy;` next to the existing Stats, Phases and Fields copies. `CompileParticipantImpl` is the single implementation behind both `CompileParticipant` (production) and `CompileSyntheticParticipant`, so both paths copy the policy; an invalid policy returns with the other validation errors before the production path loads any skeleton or animation. `Out.Reset()` at the top of the function (existing) already clears a previous output on every compile.

Preserved unchanged: identity, Stats, Phase and manifest validation, the skeleton and animation dependency check, the synthetic contract, `BindEncounter`, `CreateConfigureRegister`, every other line. No schema bump, no asset migration or save: I looked, and no `URPGBossDefinition` asset exists in the project content (byte search of `Content/OneBossFight`), so the additive defaults reach no saved asset today; the only source users of the class are the binding files and tests (the existing binding and preflight tests build definitions that now simply carry the default policy 1200 and true, which is valid).

## The new adapter (`RPGBossEncounterPolicyAdapters`)

- `ValidateEncounterPolicy(const FRPGEncounterPolicyConfig&, FString&)`: output cleared first; GateRadius finite (`InvalidPolicy.NotFinite`) and not negative (`InvalidPolicy.Negative`); 0 valid (no gate), -0.0 is 0, fractional valid, no maximum or floor. An invalid value is refused, never replaced by 1200 or true.
- `ConfigureEncounterPolicy(UActorComponent&, const FRPGParticipantConfig&, FString&)`: the accepted lifecycle checks in the accepted order (`InvalidComponent` first, `WrongComponentClass`, `ComponentBegunPlay`, `ComponentAlreadyRegistered`, `InvalidOwner`, `OwnerBegunPlay`), then the whole policy, then the one write block that assigns ONLY `GateRadius` and `bResetOnPlayerRespawn` on the exact `URPGBossEncounter`. `BossMaxHealth`, `bTestFreeze`, the tracked pawn, home transform, generation, dormant, held and waking state, counters, cached attributes and clocks are never written.
- `MakeEncounterPolicyPlan()`: class `URPGBossEncounter`, instance name `RPGBossEncounter`, `RequiredFields` = `EncounterPolicy.GateRadius`, `EncounterPolicy.bResetOnPlayerRespawn` (membership metadata only). Typed values only: never `FRPGParityField.Value`, never ImportText.
- **Unwired fragment.** It is NOT inserted into the DD5 preflight and the header says it must not be listed together with the stats adapter's encounter plan (the hydration mechanism refuses two plans for one component class); a future combined plan applies stats and policy to the one component once, after complete validation. No creation, registration or Configure execution at compile, no actor discovery, no hooks, no Ready or suppression claim.

## Judgement calls (please confirm or change)

1. **The compiler adds the policy error to the collected errors** (like the stats error) and does not return early, so one compile reports every problem; the existing early return after the field manifest is unchanged.
2. **The lifecycle check is restated privately** in the new cpp (a third copy, after the stats and phase adapters) because the accepted adapter files must not change. A single shared helper is a later consolidation package, not this one.
3. **The fragment's instance name equals the stats encounter plan's** on purpose (the legacy component name); the two fragments are alternatives for one component until the combined plan exists.
4. **`EncounterPolicy` sits right after `Stats`** in the definition; it only affects Details order.
5. **The reflection test asserts exposure** (both fields and the definition property exist, are editable, have the struct type) because exposure is what makes the Data Asset field authorable; it says nothing about the Details panel itself.

## Tests (6 new automation tests, expected discovered count 63 -> 69 once built)

| test | covers |
|---|---|
| `OneBossFight.Binding.EncounterPolicy.Assign` | plan identity (class, legacy name, the two exact paths); non-default 731.25 and false applied through the plan callback while the manifest `Value` TEXT says 9999 and true (typed values win); stale diagnostic cleared on success; health and test-freeze sentinels (777, true) and every other state equal; unregistered, owner not begun, owner gained no component; zero gate with reset true and fractional 0.5 with reset false through the direct helper |
| `...Validation` | 11 rows (0, -0.0, 0.001, 731.25, 1200, 1e9 valid; -0.0001, -1, NaN, +Inf, -Inf rejected with the named token); each rejected row also run through the assignment with reset true and false: refused, same token, NO write (full state incl. sentinels); valid rows clear a stale diagnostic; a valid policy still configures afterwards |
| `...Isolation` | two owners, two configs (731.25/false and 0/true): configuring B leaves A equal; a later config change does not reach A; an unconfigured component and the CDO keep 1200 and true |
| `...Rejections` | wrong class (a posture, a scene component; no abstract class), registered, component begun (real `DispatchBeginPlay`, gate radius 0 first), owner begun, orphan, destroyed and destroyed-wrong-class (`InvalidComponent` outranks the class check); each asserts the token and unchanged state with sentinels; unreachable preconditions are `AddError` |
| `...Compile` | the REAL `CompileSyntheticParticipant`: policy copied (731.25/false, 0/true), established Stats, phase and identity values retained, config is a value snapshot, an untouched policy copies the authoring defaults; invalid policy (negative, NaN, +Inf, -Inf) fails by name through the synthetic compile AND through the production `CompileParticipant` (refused before any asset load), never defaulted, and clears a previously valid output; the established failures (negative posture, phase threshold above 1, schema 2, a hash that is not 64 hex, no content lease, no field manifest) still fail with a valid policy and clear the output; policy and stats failures are both reported |
| `...Authoring` | reflection: the struct and both properties exist with the right types and `CPF_Edit`; `URPGBossDefinition::EncounterPolicy` is an editable property of exactly that struct; a fresh struct and a fresh definition hold 1200 and true (compared with the native declarations only as a baseline); the stats record keeps its own defaults |

## What this does NOT prove or do

No serialized asset value, nothing in the Details panel, no production compile with a real skeleton (only its early rejection), no live gate or reset behavior, no duel, no wiring, no change to the preflight, no combined Stats and policy plan, no claim that the policy makes an encounter ready or suppresses legacy components. Next missing cluster fields (stagger, phase presentation, wake) are not completed here.

## Next, when you release it

Scoped verification order: build (UHT will run, a reflected struct and property are new), run only `OneBossFight.Binding.EncounterPolicy`, then the full suite (expect 69 found, the prior 63 present), with raw logs, hashes, manifests and exact warning diagnostics (UBT Warning: lines reported as such). No build or automation has been run for this package.

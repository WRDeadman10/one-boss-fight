# Step1 condition1: typed reference-closure test specification

2026-10-26. Requested in C147. SPEC ONLY for Claude review/implementation under subsequent approved source scope; no source/asset changes or test execution authorized by this document. Goal: fulfill v3C3 without inventing pack topology or changing equip behavior.

## Contract to implement

Catalog:184 currently checks Item against a catalog-supplied ItemBaseClass, ActorClass against AActor, AbilityClass as any UClass, Style only by FName.188-193 accepts full-path substring membership across all properties of three objects. That preserves current installed bundle, but neither fixed ABI ancestry nor typed compatible roles. A nonlegacy negative probe in Resolution now tests resolved style mismatch correctly, not the whole closure.

Use ONE versioned native adapter contract for the installed pack. It pins trusted base classes/interfaces and typed property/function roles. Content may select registered capability profiles and supported full references, not choose its own permissive UObject base or arbitrary reflection property names. A new supported capability is separately reviewed shared code; adding another ordinary weapon within it stays data-only.

## Readback first, no guessed property names

Claude must export class hierarchy + typed properties for actual installed ToughSword, KwangSword, DualSteelSwords items, spawned BP_ToughSword/BP_KwangSword/BP_DualSteelSwords CDOs and their styles/granted abilities. Include property FName/GUID, FProperty kind, owning class full path, declared object/class constraint, actual full referenced identity, inheritance origin and any runtime setter. Each relevant edge has its OWN record (from-object, property chain, array/map key, to-object/class, role).

Filesystem candidates exist (existence is NOT inheritance proof):

- `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/WeaponItem.WeaponItem_C`
- `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/DataAssets/Items/DualWeaponItem.DualWeaponItem_C`
- `/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Actors/Weapons/BP_BaseWeapon.BP_BaseWeapon_C`
- `/Game/AdvancedARPGCombat/AdvancedCombatFramework/AbilitySystem/Abilities/BP_AdvancedGameplayAbility.BP_AdvancedGameplayAbility_C` (also named by exported parent function references).

Resolve/verify actual ancestry and roles before pinning. Do not assume DualWeaponItem derives from WeaponItem from filenames. If distinct permitted roots exist, native profile explicitly enumerates each supported branch and offhand requirements. Missing export/role is UNRESOLVED, never first-name match or acceptance via string search.

Expected topology may be Item->Actor and Item/Actor->Style->Ability, not Item->all directly. Only role-correct typed edges satisfy a role; an ability full path in a description/debug string, unrelated default/map branch or a different style's grant does not. Exact expected property names remain editor-needed pending readback; this is not a license to guess or accept every field.

## Positive suite

| ID | Fixture / assertion |
|---|---|
| ABI-P01 | Resolve three pinned legacy bundles. Full identities/hierarchy/typed edge paths match adapter contract. Same exact equip calls/slots/quickslot-lock/defer/retry behavior as current binary. |
| ABI-P02 | Fourth nonlegacy BuildId sharing Sword accepts; shared-style reverse ambiguous without verified identity, verified chosen id retained. No enum addition or fake fallback coverage. |
| ABI-P03 | Another registered compatible weapon profile in a NONlegacy fixture accepts with full authored action coverage or explicit DD1 compatibility route. This is not new art/P8 acceptance. |
| ABI-P04 | GI epoch leases keep closure alive after GC; source data assets can unload without dangling asset pointers. Fresh contexts share immutable metadata only, not mutable equipment state. |
| ABI-P05 | Cooked Development cold source=data loads closure; editor-only asset registry presence is insufficient. Shipping provenance handled separately by X-T8. |

## Negative suite (must reach the intended validator)

| ID | One defect at a time | Expected field/code, not generic failure |
|---|---|---|
| ABI-N01 | Catalog ItemBaseClass deliberately UObject while item not approved weapon ancestry | Weapon.<id>.Item.ExpectedABI; caller cannot bless itself |
| ABI-N02 | ActorClass is a valid unrelated AActor subclass with same short leaf name in a different project package | Weapon.<id>.Actor.ExpectedABI / full identity, never accepted by base-name equality |
| ABI-N03 | AbilityClass resolves to arbitrary UClass not gameplay-ability base/interface | Weapon.<id>.Ability.ExpectedABI |
| ABI-N04 | Correct ability class ancestry but not granted by the selected actual style/binding | Weapon.<id>.Style.AbilityGrant; mere presence elsewhere cannot satisfy |
| ABI-N05 | Item points to a different weapon actor; declared expected actor path appears only in unrelated text property | Weapon.<id>.Item.ActorBinding |
| ABI-N06 | Correct actor/ability strings appear across unrelated owners; one required typed edge is absent | Specific missing edge path, no combined-text pass |
| ABI-N07 | Style full path resolves to wrong asset/class despite matching StyleName leaf | Weapon.<id>.Style.ExpectedABI / Identity |
| ABI-N08 | Alias collides across distinct weapon identities | Weapon.<id>.StyleAliases; semantic fixture not confused with valid shared-build same-weapon case |
| ABI-N09 | Valid uncooked or editor-only dependency; parent class outside always-cook folder but actually transitively cooked | First case rejects actual missing dependency, second valid ancestry case accepts; directory prefix alone not sufficient |
| ABI-N10 | Null/missing required object, redirector/unresolved path or ambiguous resolution | Exact required role; no first asset, legacy fallback per-lookup or partial epoch |
| ABI-N11 | Optional absent/broken/wrong-type icon | Accept text-only under declared presentation policy, once-entry diagnostic distinguishing absence from broken path; no gameplay closure failure |
| ABI-N12 | Correct nonlegacy style name but points at wrong style asset (C140 probe pattern) | Resolving References error; same fixture Compile(false) structurally valid |

Every malformed dependency fixture must preserve3 pinned legacy rows and structural validity, altering ONLY an extra nonlegacy bundle where appropriate. Prove structural-only accept or trace reached validation stage; assert exact error field/code. Do not change a pinned row and claim resolving coverage. A failure at cook guard cannot also be evidence of ancestry rejection.

No pack/source asset mutation. Prefer a reviewed typed closure-reader seam + test resolver for unit negatives, clearly labelled synthetic, followed by real installed positive assets and separately approved NEW project-owned negative fixtures for engine integration. Temporary in-memory objects must not evade cook/reference checks unnoticed. Do not serialize or save synthetic test objects into production catalog. No injected resolver/test bypass in Shipping.

## Publication and regression

Validate entire closure before Context.Publish. Strict data failure publishes NOTHING; auto compatibility publishes whole legacy with reason; legacy never loads candidate. No mixed epoch. Verify no pack equip/start/property mutation occurs during validator execution. Record adapter version, content digest, all referenced full paths and role paths for provenance, not merely "wiring checked".

Claude acceptance evidence: actual source diff + UHT/build, named assertions with raw output, frozen assets/source/scripts hashes before/after, full gate on the final binary (not prior binary41/41), real three-build witnesses and cold Development proof. Existing material failures remain separate. Codex re-review required before this condition is called closed. Owner acceptance/promotion still separate.

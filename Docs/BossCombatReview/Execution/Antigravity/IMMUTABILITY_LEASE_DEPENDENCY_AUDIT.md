# AG13: Immutability, Lease, and Dependency Assurance Audit (Rev 02)

**Document Date:** 2026-10-27  
**Author:** Antigravity (Pair Programming AI Assistant)  
**Task Classification:** Work Order 13 (AG13) — Focused Immutability, Lease, and Dependency Assurance Audit (Revision 02)  
**Governing Inputs:**
- Acceptance: [`Docs/BossCombatReview/Execution/Codex/AG12_A136_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG12_A136_ACCEPTANCE.md) (`SHA256: 5b1f661eb4504546c21850e30a313e91916670fb29449d619359eca62e49356d`)
- Review Feedback: [`Docs/BossCombatReview/Execution/Codex/AG13_A137_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG13_A137_REVIEW.md) (`SHA256: 9fec91b68def3142ebb25b01d61a9fb3d35fb722ae7c40383274d336ed4291c3`)
- Mailbox Directives: `[X-208]`, `[X-209]`, and `[X-210]` (2026-10-27 05:59:55 +05:30)

---

## 1. Executive Summary & Audit Mandate (Rev 02)

Per Codex directives `[X-208]`, `[X-210]`, and [`AG13_A137_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG13_A137_REVIEW.md), Antigravity conducted a rigorous, offline, source-grounded revision of the immutability, lease, and dependency assurance audit across:
1. Catalog `FEpoch` storage, `Compile` mechanics, and lease lifetimes (`RPGCombatCatalog.h` / `.cpp`).
2. Participant config compilation and strong reference tracking (`RPGEncounterBinding.h` / `.cpp`).
3. Staged `ShadowCompare` content/artifact leases and generation handling (`RPGShadowCompare.h` / `.cpp`).
4. Actual native mutation sites (`RPGBossPhases.cpp`, `RPGBossEncounter.cpp`, `RPGBossPosture.cpp`, `RPGBlueprintCall.h`).

### Key Findings & Corrections (Rev 02):
- **Direct Write Targets vs Unverified Ownership Invariants:** `RPGBossPhases.cpp:397-449` (`ScaleAttackRates`) directly mutates reflected `PlayRate` numeric fields on `UObject*` pointers retrieved from the `CreatedAbilities` array on `BP_AdvancedAbilitySystemComponent_C`. It contains **no direct montage setter calls** and **no direct `GetDefaultObject()` calls**. However, local source alone **does not prove** every entry in `CreatedAbilities` is a distinct runtime `UGameplayAbility` instance strictly exclusive to one actor, nor that it is free of shared CDO/sub-object references. Without wider pack instantiation evidence, graph exclusivity and ancestry remain **unverified/unknown invariants**. No shared-asset disk/CDO corruption is claimed or proven.
- **Ordinary GC Retention != Deep Const or Thread Safety:** `TStrongObjectPtr<UObject>` guarantees garbage collection prevention for the specific valid object pointer held while the guard remains in scope. It does **not** provide deep const, does **not** freeze interior properties of objects reached via `Get()` or external aliases, does **not** grant immunity from explicit engine destruction/unload, and does **not** imply thread safety. It is not an assertion of a specific `AddToRoot` or `RF_RootSet` implementation.
- **Existing Reset and Health Guards:** In `RPGBossEncounter.cpp:90-108`, health application is gated behind `!bMaxHealthApplied`. Once applied, modifying `BossMaxHealth` does **not** automatically trigger re-scaling on subsequent ticks. Furthermore, `RPGBossEncounter::ResetEncounter()` calls `Phases->ResetPhases()`, which calls `RemovePhaseTwoBuffs()`. Reusing an actor across fights is not an automatic compounding speed failure. Floating-point inverse multiplication (`* Factor` then `* 1/Factor`) may incur rounding error, but does not necessarily drift monotonically across all inputs/cycles. Suppression of pack poise regeneration (`1.0e9` s cooldown) in `RPGBossPosture.cpp` is intentional existing design to transfer posture authority to `URPGBossPosture`, not a pooled-actor defect.
- **Generation Advance vs Content Reassociation:** Phase transitions do **not** trigger context generation increments. Ordinary encounter resets can advance generation with the **same** content/artifacts legitimately; a generation bump alone does not render existing compiled timelines obsolete. True reassociation gaps arise when participants are reconfigured with different definitions or epochs without updating observer artifacts. Blanket invalidation on every generation bump is an alternative candidate proposal with trade-offs, not required parity or an automatic bug fix.
- **Non-Masking GC Witness Specification:** Replaced procedural calls to `TryLoad()` post-GC (which could reload assets from disk and mask retention failures) with non-owning `TWeakObjectPtr<UObject>` inspection and loaded-state metadata verification without reload.
- **Separation of Deterministic Digest from Lifetime GUID:** Deterministic content digests (for canonical artifact keying) complement, but do not replace, per-compilation lifetime GUIDs (`FEpoch::Id`), which serve distinct roles in distinguishing game-instance sessions and detecting stale instances.

---

## 2. Inspected Input Receipts

All inspected files were verified on disk via exact SHA256 hashing and byte counts:

| File Path | SHA256 Hash | Bytes | Role / Stage in Review |
|:---|:---|:---:|:---|
| [`Source/OneBossFight/Player/RPGCombatCatalog.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.h) | `e7d5296833cfa5bec4101e608a98ab336a5b8c7a5c476e0d3b17eae57279dbb5` | 7,427 | Catalog `FEpoch`, `FContext`, `FDiagnosticLedger` declarations |
| [`Source/OneBossFight/Player/RPGCombatCatalog.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatCatalog.cpp) | `f6f71036804f60f0e4c8b3cf455f2a04a7bc4cf379760334903a2d9d613de59d` | 23,675 | `Compile` implementation, conditional asset resolution, `Leases` emplace |
| [`Source/OneBossFight/Player/RPGEncounterBinding.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.h) | `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` | 7,338 | `FRPGParticipantConfig`, `URPGCombatContextSubsystem` |
| [`Source/OneBossFight/Player/RPGEncounterBinding.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.cpp) | `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc` | 14,964 | `CompileParticipantImpl`, strong refs to Skeleton / Anims |
| [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.h) | `95da9c0c6a72a302ed16cc1d9c3b0d5f7fd8e758f573dd65bda0bc4b13ca00ab` | 2,690 | Staged `URPGCombatTimelineShadow` component declaration |
| [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGShadowCompare.cpp) | `f6a0274c3bad8d5221981fa10dc529a284aa3285eb1220ba3e4f991a07363924` | 15,190 | `Configure`, `BindTracker`, `OnSnapshot` lease handling |
| [`Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Drafts/Source/OneBossFight/Boss/RPGTimelineCompiler.h) | `5bf162ff250469cf6b80f2edaad5cfc39e969ed4eb6e8d6256cf56b640fe119e` | 3,137 | Staged `RPGTimeline::FKey` declaration and compiler types (receipt corrected) |
| [`Source/OneBossFight/Player/RPGBossPhases.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.h) | `0887f37564a28564261b81ad21a1baf2a4c6f6adae99a3a49c3c15622225a69a` | 8,607 | Phase component declaration, `PhaseTwoHealthFraction` |
| [`Source/OneBossFight/Player/RPGBossPhases.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp) | `c43615412e1f345d6ed75cc6d6a6b0d9ece6acaaac612e545b42cc24087f7a06` | 21,965 | `ScaleAttackRates`, `CreatedAbilities` mutation, `ResetPhases` |
| [`Source/OneBossFight/Player/RPGBossEncounter.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h) | `4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6` | 5,359 | Boss encounter manager, `BossMaxHealth` default 2000 |
| [`Source/OneBossFight/Player/RPGBossEncounter.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp) | `dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d` | 12,526 | Tick health mutation, `WriteMaxAttribute` call, `ResetEncounter` |
| [`Source/OneBossFight/Player/RPGBossPosture.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.h) | `bca70f5816a45733f0ea2d5550651da7192ba179a5e31d736eab90fd46cd3ff8` | 7,551 | Posture component declaration, `Hold()`, `Posture` |
| [`Source/OneBossFight/Player/RPGBossPosture.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.cpp) | `b26e184b0410e858d1c504e0b374dbc9e8f4c6b6399b05617559bb6909e88e41` | 7,435 | `ConfigureAttribute`, `BP_PoiseExtendedAttribute_C` |
| [`Source/OneBossFight/Pack/RPGBlueprintCall.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Pack/RPGBlueprintCall.h) | `08ca6403cb85eef36ed15c755a2163fb17f8bcfdb81043b640765d5145b8e19c` | 10,962 | `WriteAttribute`, `WriteMaxAttribute` reflected calls |
| [`Docs/BossCombatReview/Execution/Codex/AG12_A136_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG12_A136_ACCEPTANCE.md) | `5b1f661eb4504546c21850e30a313e91916670fb29449d619359eca62e49356d` | 3,976 | Codex AG12 acceptance and AG13 assignment terms |
| [`Docs/BossCombatReview/Execution/Codex/AG13_A137_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG13_A137_REVIEW.md) | `9fec91b68def3142ebb25b01d61a9fb3d35fb722ae7c40383274d336ed4291c3` | 6,058 | Codex A137 review and AG13 Rev 2 correction instructions |
| [`Docs/BossCombatReview/Execution/Codex/Step2Preparation/native_capability_contract_model.mjs`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/Step2Preparation/native_capability_contract_model.mjs) | `41a76da11907291bdeb627e1abc8bed6eaaf4107e08422488f6b038342eccf33` | 5,248 | Codex candidate scalar proposal contract model |

---

## 3. Comprehensive Assurance Table: Lifecycle Stages, Types, and Guarantees

The following table distinguishes between source-observable facts, expected engine/pack invariants, and unverified/unknown risks across the four lifecycle stages:

| Lifecycle Stage | Entity / Field | Representation Category | Owner & Lifetime | Source-Observable Assurance | What Reference/Lease Does NOT Guarantee (Limits) | Identity / Provenance Status |
|:---|:---|:---|:---|:---|:---|:---|
| **1. Generic Compilation** | `FEpoch::Builds`, `Weapons`, `Coverage` | Copied immutable value (structs, arrays) | Owned by `FEpoch` instance (`TSharedPtr<const FEpoch>`). Lives while any shared pointer is held. | Callers holding `TSharedPtr<const FEpoch>` cannot mutate struct fields through that pointer. | Does NOT guarantee referenced asset paths on disk exist or remain unchanged unless resolved. | Ephemeral `FGuid::NewGuid()`. Not a deterministic content digest. |
| **1. Generic Compilation** | `FEpoch::Leases` (`TStrongObjectPtr<UObject>`) | Retained strong UObject references | Owned by `FEpoch`. Pinned in Unreal GC root set while the guard/container is in scope. | Prevents garbage collection of the specific valid `UObject*` instances held under normal GC. | **NO deep const.** Does NOT freeze interior properties of the UObjects. Does NOT prevent mutation via other aliases or explicit engine destruction. No thread-safety guarantee. | None. Object pointers reflect memory residency only. |
| **1. Generic Compilation** | `FContext::Epoch` | Shared pointer lease (`TSharedPtr<const FEpoch>`) | Owned by `URPGCombatCatalogSubsystem` (`UGameInstanceSubsystem`). Single publication per session. | Guarantees single latched publication per game instance. | Does NOT isolate across distinct PIE instances or process restarts. | Epoch GUID. |
| **2. Native-Plan Compilation** | `FRPGParticipantConfig::Stats`, `Phases`, `Fields` | Copied immutable value (structs, arrays) | Owned by `FRPGParticipantConfig` (`TSharedPtr<const FRPGParticipantConfig>`). | Deep copy of authored data asset fields; isolated from subsequent edits to the source `URPGBossDefinition`. | Does NOT guarantee runtime values on actor components will match these if components mutate them. | Syntax-checked SHA-shaped text (`IsSHA256(Hash)`); validated `FGuid` on `Content`. |
| **2. Native-Plan Compilation** | `FRPGParticipantConfig::Content` | Shared pointer lease (`TSharedPtr<const FEpoch>`) | Held by `FRPGParticipantConfig`. | Keeps referenced catalog epoch resident while config is held. | Does NOT guarantee the catalog epoch was compiled from assets compatible with this participant. | References `Content->Id` (GUID). |
| **2. Native-Plan Compilation** | `FRPGParticipantConfig::Skeleton`, `Animations` | Retained strong UObject references (`TStrongObjectPtr`) | Held by `FRPGParticipantConfig`. | Prevents GC collection of the specific Skeleton and AnimSequence objects held while config is resident. | Does NOT freeze animation curve data, bone hierarchies, or notifies if modified in editor/runtime. | Asset pointer comparison (`Animation->GetSkeleton() == Skeleton.Get()`). |
| **3. Pre-BeginPlay Config** | `URPGCombatParticipant::Snapshot` | Shared pointer lease | Held by `URPGCombatParticipant` component on actor. | Read-only access to immutable participant configuration struct. | Does NOT prevent actor from acquiring other components or mutating its own properties. | `FRPGParticipantKey` (`WorldSession`, `EncounterInstance`, `Slot`, `Generation`). |
| **3. Pre-BeginPlay Config** | `URPGCombatTimelineShadow::Timelines` | Array of shared pointers (`TSharedPtr<const FCompiled>`) | Held by `URPGCombatTimelineShadow` component. | Compiled timeline artifact structs are const and cannot be modified through the pointer. | Does NOT verify whether timelines correspond to the currently active actor mesh or animation set. | `RPGTimeline::FKey` (`AssetPath`, `AssetSHA256`, `Move`, `Variant`, `Section`). |
| **3. Pre-BeginPlay Config** | `URPGCombatTimelineShadow::ContentLease` | Shared pointer lease (`TSharedPtr<const FEpoch>`) | Held by `URPGCombatTimelineShadow`. | Keeps catalog epoch resident during shadow observation while component holds lease. | **Does NOT verify match** with bound participant's `Config->Content`. Shared pointer reset can release lease before component destruction. | `FEpoch::Id` (GUID). |
| **4. Runtime Observation** | `FPassiveSnapshot` | Value-copied transient sample | Stack allocated in `CaptureAfterTracker`; discarded after processing. | Snapshot values are point-in-time copies of tracker and montage state. | Does not prevent underlying montage or tracker from changing on subsequent instructions. | `GameTime`, `Position` (Sequence belongs to `FPlaybackAdapter`). |
| **4. Runtime Execution** | Reflected objects in `CreatedAbilities` | Reflected `UObject*` pointers | Owned by actor's `BP_AdvancedAbilitySystemComponent_C`. | Direct write target of `ScaleAttackRates` is the reflected numeric property on these pointers. | **Not proven exclusive per-actor runtime instances.** Local source has no CDO/outer checks; graph exclusivity is unverified. Mutated by `ScaleAttackRates`. | Class name prefix (`AttackAbilityPrefix`). |
| **4. Runtime Execution** | Reflected objects in `ExtendedAttributeInstances` | Reflected `UObject*` pointers | Owned by actor's `BP_AttributesComponent_C`. | Direct write target of `ConfigureAttribute` (`StatRegenCoolDown = 1.0e9`). | Indirect global/asset side effects unverified from local call site alone. | Tag name (`BP_PoiseExtendedAttribute_C`). |
| **4. Runtime Execution** | `URPGBossPosture::Posture` | Primitive float variable | Private member of `URPGBossPosture` component on actor. | Component-local tracking only. | Isolated to component instance; no global side effects. | None (local state). |

---

## 4. Source-Grounded Audit of Actual Native Mutation Sites

### 4.1. Attack Rate Scaling: `RPGBossPhases.cpp:397-450`

```cpp
// RPGBossPhases.cpp:397-415 (abbreviated source excerpt)
void URPGBossPhases::ScaleAttackRates(float Factor)
{
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	const FArrayProperty* Created = Asc ? FindFProperty<FArrayProperty>(Asc->GetClass(), TEXT("CreatedAbilities")) : nullptr;
	const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
	if (!Inner) { return; }
	FScriptArrayHelper Abilities(Created, Created->ContainerPtrToValuePtr<void>(Asc));
	for (int32 Index = 0; Index < Abilities.Num(); ++Index)
	{
		UObject* Ability = Inner->GetObjectPropertyValue(Abilities.GetRawPtr(Index));
		const FString Name = Ability ? Ability->GetClass()->GetName() : FString();
		if (!Ability || !Name.StartsWith(AttackAbilityPrefix) || ...) { continue; }
```

```cpp
// RPGBossPhases.cpp:416-447 (abbreviated source excerpt)
		// Every array of the pack's F_AbilityMontage structs on the ability (AttackMontages): scale the play rate field of each element.
		for (TFieldIterator<FArrayProperty> It(Ability->GetClass()); It; ++It)
		{
			const FStructProperty* Element = CastField<FStructProperty>(It->Inner);
			if (!Element || !Element->Struct || !Element->Struct->GetName().Contains(TEXT("AbilityMontage"))) { continue; }
			const FNumericProperty* RateField = nullptr;
			for (TFieldIterator<FProperty> Field(Element->Struct); Field; ++Field)
			{
				if (const FNumericProperty* Number = CastField<FNumericProperty>(*Field))
				{
					if (Number->IsFloatingPoint() && Number->GetName().StartsWith(TEXT("PlayRate"))) { RateField = Number; break; }
				}
			}
			if (!RateField) { continue; }
			FScriptArrayHelper Entries(*It, It->ContainerPtrToValuePtr<void>(Ability));
			for (int32 E = 0; E < Entries.Num(); ++E)
			{
				void* Value = RateField->ContainerPtrToValuePtr<void>(Entries.GetRawPtr(E));
				RateField->SetFloatingPointPropertyValue(Value, RateField->GetFloatingPointPropertyValue(Value) * Factor);
				++Scaled;
			}
		}
```

#### Grounded Verdict & Ownership Boundaries:
1. **Direct Write Target:**
   - The direct target of the mutation is the reflected floating-point property `RateField` located inside elements of struct arrays on the `UObject*` pointers retrieved from `CreatedAbilities`.
2. **Untouched Direct Targets:**
   - **No direct montage setter:** The function does not call `UAnimMontage` setter methods or modify asset disk bytes.
   - **No direct CDO call:** The function does not call `GetDefaultObject()` or explicitly target class default objects.
3. **Explicit Limits & Unknown Invariants:**
   - Local source contains **no guards verifying outer ownership or CDO exclusion**.
   - Whether entries in `CreatedAbilities` are strictly unique per-actor runtime instances, share sub-objects, or reference shared class templates depends on the pack's internal instantiation policy (e.g. `BP_AdvancedAbilitySystemComponent_C`'s ability granting pipeline).
   - Because this pack creation pipeline was not audited, unique per-actor exclusivity remains an **unverified invariant**, not a proven source fact.
   - No shared-object or CDO corruption is claimed or proven.
4. **Conditional Risks:**
   - **Inverse Multiplication Rounding:** `RemovePhaseTwoBuffs()` (`RPGBossPhases.cpp:388`) applies `ScaleAttackRates(1.f / AttackRateScale)`. In floating-point arithmetic, multiplying by `Factor` then `1.f / Factor` can incur rounding errors; however, this is a conditional risk dependent on specific values and iterations, not a guaranteed monotonic drift.
   - **Reset Invariants:** In `RPGBossEncounter.cpp:297-325`, `ResetEncounter()` explicitly invokes `Phases->ResetPhases()`, which calls `RemovePhaseTwoBuffs()`. Reusing an actor across encounters does **not** automatically cause compounding speedups unless the reset pathway is bypassed or fails.

---

### 4.2. Health Mutation: `RPGBossEncounter.cpp:90-108` & `RPGBlueprintCall.h:243-268`

```cpp
// RPGBossEncounter.cpp:90-108 (abbreviated source excerpt)
if (!bMaxHealthApplied && BossMaxHealth > 1.f)
{
	double Max = 0.0, Current = 0.0;
	if (ReadAttribute(GetOwner(), HealthTag, true, Max) && ReadAttribute(GetOwner(), HealthTag, false, Current) && Max > 0.0 && Current > 0.0)
	{
		double NewMax = 0.0;
		if (FMath::Abs(Max - BossMaxHealth) <= 0.5) { bMaxHealthApplied = true; }
		else if (WriteMaxAttribute(GetOwner(), HealthTag, BossMaxHealth) && ReadAttribute(GetOwner(), HealthTag, true, NewMax) && FMath::Abs(NewMax - BossMaxHealth) <= 0.5)
		{
			bMaxHealthApplied = true;
			WriteAttribute(GetOwner(), HealthTag, Current * BossMaxHealth / Max);
			UE_LOG(LogRPGEncounter, Log, TEXT("%s: boss maximum health %.0f -> %.0f (health %.0f -> %.0f)"), *GetOwner()->GetName(), Max, static_cast<double>(BossMaxHealth), Current, Current * BossMaxHealth / Max);
		}
	}
}
```

#### Grounded Verdict & Operational Guards:
1. **Application Gating (`!bMaxHealthApplied`):**
   - Health scaling occurs strictly when `!bMaxHealthApplied`. Once set to `true` (lines 99 or 104), this block does not execute on subsequent ticks.
   - Consequently, changing `BossMaxHealth` after initial application does **not** automatically trigger re-scaling on every tick.
2. **Direct Dispatch:**
   - Calls dynamic Blueprint function `Set Max Attribute Value` on the actor's `BP_AttributesComponent_C`.
   - Modifies runtime attribute state; whether this produces indirect side-effects across broader pack graphs remains unverified from the call site alone.

---

### 4.3. Posture Configuration & Local State: `RPGBossPosture.cpp:42-65`

```cpp
// RPGBossPosture.cpp:42-65 (abbreviated source excerpt)
bool URPGBossPosture::ConfigureAttribute()
{
	UObject* Attributes = FindComponentByClassName(GetOwner(), TEXT("BP_AttributesComponent_C"));
	const FArrayProperty* Instances = Attributes ? FindFProperty<FArrayProperty>(Attributes->GetClass(), TEXT("ExtendedAttributeInstances")) : nullptr;
	const FObjectProperty* Inner = Instances ? CastField<FObjectProperty>(Instances->Inner) : nullptr;
	if (!Inner) { return false; }
	FScriptArrayHelper Array(Instances, Instances->ContainerPtrToValuePtr<void>(Attributes));
	for (int32 Index = 0; Index < Array.Num(); ++Index)
	{
		UObject* Object = Inner->GetObjectPropertyValue(Array.GetRawPtr(Index));
		if (Object && Object->GetClass()->GetName() == TEXT("BP_PoiseExtendedAttribute_C"))
		{
			SetDouble(Object, TEXT("StatRegenCoolDown"), 1.0e9);
			SetDouble(Object, TEXT("InitialRegenRate"), 0.0);
			SetDouble(Object, TEXT("CurrentRegenRate"), 0.0);
			return true;
		}
	}
	return false;
}
```

#### Grounded Verdict & Intentional Design:
1. **Target of Mutation:**
   - Mutates `StatRegenCoolDown`, `InitialRegenRate`, and `CurrentRegenRate` directly on the `BP_PoiseExtendedAttribute_C` instance within `ExtendedAttributeInstances`.
2. **Intentional Suppression:**
   - Suppressing pack poise regeneration (`1.0e9` s cooldown) is an intentional architectural choice to transfer posture management entirely to `URPGBossPosture`, not an unhandled pooled-actor bug.

---

## 5. Staged `ShadowCompare` Lease and Reassociation Audit

### 5.1. The Scope of `ContentLease` in `URPGCombatTimelineShadow`
```cpp
// RPGShadowCompare.cpp:92-103 (abbreviated source excerpt)
bool URPGCombatTimelineShadow::Configure(const TArray<TSharedPtr<const RPGTimeline::FCompiled>>& Values,
	const FRPGParticipantKey& Key, TSharedPtr<const RPGCombatRegistry::FEpoch> Lease)
{
	if (!Timelines.IsEmpty() || IsRegistered() || Values.IsEmpty() || !Lease || !Key.WorldSession.IsValid() || !Key.EncounterInstance.IsValid()
		|| Key.Slot.IsNone() || Key.Generation == 0) { return false; }
	...
	Timelines = Values; Participant = Key; ContentLease = MoveTemp(Lease); return true;
}
```
- **What `ContentLease` Guarantees:**
  - Holding `TSharedPtr<const FEpoch>` ensures the catalog `FEpoch` struct remains allocated while the shared pointer is held.
  - Keeps valid UObjects in `FEpoch::Leases` referenced under normal GC during that lifetime.
  - Does **not** provide deep const, does **not** protect against explicit destruction/unload, and does **not** verify that `Lease->Id` matches the bound participant's `Config->Content->Id`.
  - Shared pointer reset can release the lease prior to component destruction.

### 5.2. Generation Advance vs Changed Content
```cpp
// RPGShadowCompare.cpp:119-127 (abbreviated source excerpt)
void URPGCombatTimelineShadow::OnSnapshot(const RPGTimeline::FPassiveSnapshot& Sample)
{
	if (!Context.IsValid() || !GetOwner()) { Cursor.Close(); return; }
	const auto CurrentKey = Context->FindParticipant(*GetOwner());
	if (!CurrentKey.IsSet()) { Cursor.Close(); return; }
	if (!(Participant == CurrentKey.GetValue())) { Cursor.Close(); Participant = CurrentKey.GetValue(); }
	if (auto Observation = Playback.Observe(Sample, Participant, Timelines)) { ObserveAfterTracker(Observation.GetValue()); }
	else if (Sample.Position.IsSet()) { ++Dropped; }
}
```
- **Generation Invariants:**
  - Phase transitions do **not** trigger context generation increments (`URPGCombatContextSubsystem::OnGenerationChanged`).
  - An encounter reset can legitimately advance `Generation` while retaining the **exact same** participant content and timeline artifacts.
  - Therefore, a generation bump alone does **not** mean retained timelines are obsolete. Retaining existing timelines across a reset with identical content is legitimate observer continuity.
  - **The Real Reassociation Gap:** If an actor is reconfigured with a **different** participant definition or content epoch, `OnSnapshot` adopts the new `FRPGParticipantKey` without re-verifying whether `Timelines` and `ContentLease` match the new configuration. Blanket invalidation on every generation change is an alternative candidate proposal with trade-offs, not an automatic bug fix.

---

## 6. Concrete Unrun Witnesses & Test Proposals (Non-Masking)

To verify immutability, mutation isolation, and lease integrity without modifying production code or executing intrusive runs, the following concrete unrun witnesses are specified:

### Witness 1: Direct Write Target Verification (CDO & Asset Invariance)
- **Objective:** Verify whether `ScaleAttackRates` directly modifies runtime ability instances versus class defaults.
- **Procedure (Unrun Proposal):**
  1. Record property values of the Class Default Object (CDO) for `BP_AdvancedAbilitySystemComponent_C` and the specific attack ability classes prior to scaling.
  2. Execute `ScaleAttackRates(1.5f)` on a live actor.
  3. Re-read CDO properties and verify they are unchanged.
  4. Inspect the reflected struct properties on the actor's `CreatedAbilities` instances to verify the direct write was applied to the instance.

### Witness 2: Floating-Point Rounding & Reset Continuity Verification
- **Objective:** Measure potential precision degradation across repeated phase transitions and verify reset buff removal.
- **Procedure (Unrun Proposal):**
  1. Record baseline `PlayRate` on an ability instance.
  2. Execute N illustrative cycles of `ScaleAttackRates(Factor)` followed by `ScaleAttackRates(1.f / Factor)`.
  3. Measure delta `|PlayRate_final - PlayRate_baseline|` to quantify floating-point rounding.
  4. Trigger `ResetEncounter()` and verify `RemovePhaseTwoBuffs()` restores baseline values without compounding across runs.

### Witness 3: Non-Masking GC Retention Across Purge
- **Objective:** Verify that `FEpoch::Leases` retains referenced assets under GC without masking failures via reloads.
- **Procedure (Unrun Proposal):**
  1. Compile a catalog epoch referencing a test data asset.
  2. Capture a non-owning `TWeakObjectPtr<UObject>` pointing to the loaded asset; verify `WeakPtr.IsValid() == true` and record memory address.
  3. Release external raw/soft pointers, retaining only `TSharedPtr<const FEpoch>`. Ensure unrelated roots are controlled.
  4. Invoke `CollectGarbage(GARBAGE_COLLECTION_KEEPFLAGS)`.
  5. **Without calling `TryLoad()` or `LoadSynchronous()`**, inspect `WeakPtr.IsValid()`. If valid, verify memory address matches pre-GC record. If invalid, the test fails, confirming retention was not maintained.

### Witness 4: Shadow Observer Reset Continuity vs Reassociation Rejection
- **Objective:** Distinguish legitimate same-content reset continuity from stale-timeline reassociation.
- **Procedure (Unrun Proposal):**
  1. Configure `URPGCombatTimelineShadow` with Generation 1 key and artifacts.
  2. Advance encounter generation to Generation 2 with **unchanged** content; verify observer successfully continues tracking without false timeline rejection.
  3. Reconfigure encounter with a **different** participant definition or epoch without updating shadow timelines; dispatch `OnSnapshot` and verify whether the component detects definition/epoch mismatch and explicitly marks observation stale.

---

## 7. Options for Snapshot, Version, and Identity Boundaries (Proposals Only)

The following architectural options are proposed for future design consideration:

1. **Separation of Deterministic Content Digest and Lifetime GUID:**
   - **Deterministic Content Digest:** A hash computed from sorted canonical definitions (builds, weapons) can serve as an immutable content address for caching and cross-build equivalence checks.
   - **Lifetime Epoch GUID:** `FEpoch::Id` (`FGuid::NewGuid()`) must be preserved as an ephemeral per-compilation/per-session token. Collapsing lifetime GUIDs into pure content digests would weaken stale-instance detection across process/PIE restarts.
2. **Explicit Observer Reassociation Contract:**
   - Define explicit observer behavior for generation increments: permit continued observation when participant definition and epoch GUID match; reject or transition to unconfigured when definition/epoch changes.
3. **Derived Multipliers vs In-Place Struct Mutation:**
   - Consider storing base rates immutably and deriving effective play rate dynamically (`BasePlayRate * Multiplier`) rather than repeatedly mutating struct fields in-place.

---

## 8. Conclusion & Scope Verification

- **Offline Audit Complete:** Conducted entirely through static source analysis, hash verification, and architectural review.
- **Zero Forbidden Edits:** No modifications were made to `Source/`, `Config/`, `Scripts/`, Unreal assets, or Codex drafts.
- **Zero Prohibited Executions:** No Unreal Editor, PIE, build, packaging, or `UnrealPak` commands were executed.
- **Git Authority Preserved:** In strict adherence to `RULE[c:\UnrealProject\OneBossFight\AGENTS.md]`, no git commits or pushes were performed.

// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossLook.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "TimerManager.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGBossLook, Log, All);

URPGBossLook::URPGBossLook()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostUpdateWork;
	Body = TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body.SK_Boss01_Body")));
	Pieces = {
		TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Body/SK_Boss01_Crown.SK_Boss01_Crown"))),
		TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Body/SK_Boss01_Mantle.SK_Boss01_Mantle"))),
		TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Body/SK_Boss01_BrazierGauntlet.SK_Boss01_BrazierGauntlet"))),
	};
	Sword = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword")));
}

void URPGBossLook::BeginPlay()
{
	Super::BeginPlay();
	if (bEnabled && GetWorld())
	{
		GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateUObject(this, &URPGBossLook::Apply));
	}
}

void URPGBossLook::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Revert();
	Super::EndPlay(EndPlayReason);
}

void URPGBossLook::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (bApplied && bEnabled)
	{
		HidePackWeapons();
	}
}

void URPGBossLook::SetEnabledForTest(bool bOn)
{
#if !UE_BUILD_SHIPPING
	bEnabled = bOn;
	if (bOn)
	{
		Apply();
	}
	else
	{
		Revert();
	}
#endif
}

void URPGBossLook::Apply()
{
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	USkeletalMeshComponent* Leader = Character ? Character->GetMesh() : nullptr;
	if (bApplied || !bEnabled || !Leader)
	{
		return;
	}
	USkeletalMesh* BodyMesh = Body.LoadSynchronous();
	if (!BodyMesh)
	{
		UE_LOG(LogRPGBossLook, Warning, TEXT("%s: the boss body %s did not load: the pack's mesh stays"), *GetOwner()->GetName(), *Body.ToString());
		return;
	}
	auto MakeFollower = [&](USkeletalMesh* Mesh, const TCHAR* Name) -> USkeletalMeshComponent*
	{
		USkeletalMeshComponent* Follower = NewObject<USkeletalMeshComponent>(GetOwner(), Name);
		Follower->SetSkeletalMesh(Mesh);
		Follower->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Follower->SetGenerateOverlapEvents(false);
		Follower->RegisterComponent();
		// Same place and scale as the pack mesh: location and rotation snap to it, the scale stays RELATIVE (1), so the parent's scale is inherited (SnapToTargetNotIncludingScale would keep the world scale of 1 and shrink the body by the mesh's scale); the pose comes from the pack mesh.
		Follower->AttachToComponent(Leader, FAttachmentTransformRules(EAttachmentRule::SnapToTarget, EAttachmentRule::SnapToTarget, EAttachmentRule::KeepRelative, false));
		Follower->SetLeaderPoseComponent(Leader);
		return Follower;
	};
	// The pack mesh keeps driving the fight: its pose must be updated every frame although it is no longer drawn (the followers read it, the pack's weapon trace reads its sockets).
	SavedTickOption = static_cast<uint8>(Leader->VisibilityBasedAnimTickOption);
	Leader->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
	bSavedHidden = Leader->bHiddenInGame;
	Leader->SetHiddenInGame(true, /*bPropagateToChildren=*/false);
	// Keep the pack's Weapon Mesh component and sockets alive for the trace fallback;
	// the active tick reasserts its render-hidden state after pack wake/equip events.
	HiddenPackWeapons.Reset();
	PackWeaponWasHidden.Reset();
	PackWeaponWasVisible.Reset();
	HidePackWeapons();
	if (HiddenPackWeapons.Num() == 0)
	{
		UE_LOG(LogRPGBossLook, Warning, TEXT("%s: no pack weapon mesh (a static mesh named Weapon... on the pack mesh) was found during Apply; will keep searching while the look is active"), *GetOwner()->GetName());
	}

	BodyComponent = MakeFollower(BodyMesh, TEXT("RPGLookBody"));
	PieceComponents.Reset();
	for (const TSoftObjectPtr<USkeletalMesh>& Piece : Pieces)
	{
		if (USkeletalMesh* Mesh = Piece.LoadSynchronous())
		{
			PieceComponents.Add(MakeFollower(Mesh, *FString::Printf(TEXT("RPGLookPiece_%s"), *Mesh->GetName())));
		}
		else
		{
			UE_LOG(LogRPGBossLook, Warning, TEXT("%s: the piece %s did not load and is missing from the look"), *GetOwner()->GetName(), *Piece.ToString());
		}
	}
	PieceCount = PieceComponents.Num();
	if (UStaticMesh* SwordMesh = Sword.LoadSynchronous())
	{
		SwordComponent = NewObject<UStaticMeshComponent>(GetOwner(), TEXT("RPGLookSword"));
		SwordComponent->SetStaticMesh(SwordMesh);
		SwordComponent->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		SwordComponent->SetGenerateOverlapEvents(false);
		SwordComponent->RegisterComponent();
		// Attach by the configured socket or bone name. Fall back to the hand, then the
		// legacy pack socket; report any fallback instead of silently changing the pose.
		FName AttachName = SwordSocket;
		if (!BodyComponent->DoesSocketExist(AttachName))
		{
			UE_LOG(LogRPGBossLook, Warning, TEXT("%s: body has no bone/socket %s; trying fallback bones/sockets"), *GetOwner()->GetName(), *SwordSocket.ToString());
			AttachName = NAME_None;
			for (const FName FallbackName : {FName(TEXT("hand_r")), FName(TEXT("HeavySwordSocket_R"))})
			{
				if (BodyComponent->DoesSocketExist(FallbackName))
				{
					AttachName = FallbackName;
					break;
				}
			}
			if (AttachName.IsNone())
			{
				UE_LOG(LogRPGBossLook, Warning, TEXT("%s: body has no hand_r or HeavySwordSocket_R fallback; sword attaches to body root"), *GetOwner()->GetName());
			}
		}
		SwordComponent->AttachToComponent(BodyComponent, FAttachmentTransformRules(EAttachmentRule::SnapToTarget, EAttachmentRule::SnapToTarget, EAttachmentRule::KeepRelative, false), AttachName);
		SwordComponent->SetRelativeTransform(SwordAttachOffset);
	}
	else
	{
		UE_LOG(LogRPGBossLook, Warning, TEXT("%s: the sword %s did not load: the boss has no sword"), *GetOwner()->GetName(), *Sword.ToString());
	}
	bApplied = true;
	UE_LOG(LogRPGBossLook, Log, TEXT("%s: the boss look is on: body %s, %d of %d pieces, sword %s on %s, the pack mesh and %d pack weapon mesh(es) are hidden and the pack mesh still drives the pose"), *GetOwner()->GetName(), *BodyMesh->GetName(), PieceCount, Pieces.Num(), SwordComponent ? *SwordComponent->GetStaticMesh()->GetName() : TEXT("none"), SwordComponent ? *SwordComponent->GetAttachSocketName().ToString() : TEXT("-"), HiddenPackWeapons.Num());
}

void URPGBossLook::HidePackWeapons()
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	USkeletalMeshComponent* Leader = Character ? Character->GetMesh() : nullptr;
	if (!Leader || !GetOwner())
	{
		return;
	}
	TInlineComponentArray<UStaticMeshComponent*> StaticMeshes(GetOwner());
	for (UStaticMeshComponent* Candidate : StaticMeshes)
	{
		if (!Candidate || Candidate->GetAttachParent() != Leader || !Candidate->GetName().Contains(TEXT("Weapon")))
		{
			continue;
		}
		const int32 ExistingIndex = HiddenPackWeapons.IndexOfByKey(Candidate);
		if (ExistingIndex == INDEX_NONE)
		{
			HiddenPackWeapons.Add(Candidate);
			PackWeaponWasHidden.Add(Candidate->bHiddenInGame);
			PackWeaponWasVisible.Add(Candidate->IsVisible());
		}
		// The pack's wake/equip path can call visibility setters after Apply. Reassert
		// both states late each frame; never clear the mesh, since trace fallback reads sockets.
		Candidate->SetVisibility(false, /*bPropagateToChildren=*/true);
		Candidate->SetHiddenInGame(true, /*bPropagateToChildren=*/true);
	}
}

void URPGBossLook::Revert()
{
	if (!bApplied)
	{
		return;
	}
	bApplied = false;
	if (SwordComponent)
	{
		SwordComponent->DestroyComponent();
		SwordComponent = nullptr;
	}
	for (USkeletalMeshComponent* Piece : PieceComponents)
	{
		if (Piece)
		{
			Piece->DestroyComponent();
		}
	}
	PieceComponents.Reset();
	PieceCount = 0;
	if (BodyComponent)
	{
		BodyComponent->DestroyComponent();
		BodyComponent = nullptr;
	}
	for (int32 Index = 0; Index < HiddenPackWeapons.Num(); ++Index)
	{
		if (UStaticMeshComponent* Weapon = HiddenPackWeapons[Index])
		{
			Weapon->SetVisibility(PackWeaponWasVisible.IsValidIndex(Index) && PackWeaponWasVisible[Index], true);
			Weapon->SetHiddenInGame(PackWeaponWasHidden.IsValidIndex(Index) && PackWeaponWasHidden[Index], true);
		}
	}
	HiddenPackWeapons.Reset();
	PackWeaponWasHidden.Reset();
	PackWeaponWasVisible.Reset();
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (USkeletalMeshComponent* Leader = Character->GetMesh())
		{
			Leader->SetHiddenInGame(bSavedHidden, false);
			Leader->VisibilityBasedAnimTickOption = static_cast<EVisibilityBasedAnimTickOption>(SavedTickOption);
		}
	}
}

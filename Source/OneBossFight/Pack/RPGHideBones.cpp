// Copyright One Boss Fight. All Rights Reserved.

#include "Pack/RPGHideBones.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"

void URPGHideBones::BeginPlay()
{
	Super::BeginPlay();

	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	if (!Mesh)
	{
		return;
	}
	for (const FName& Bone : BoneNames)
	{
		Mesh->HideBoneByName(Bone, PBO_None);
	}
}

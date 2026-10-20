// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGSkeletonUtils.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/SkeletalMeshSocket.h"
#include "Animation/Skeleton.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGSkeletonUtils, Log, All);

int32 URPGSkeletonUtils::CopySockets(USkeletalMesh* Source, USkeletalMesh* Target, bool bToSkeleton)
{
#if WITH_EDITOR
	if (!Source || !Target)
	{
		return 0;
	}

	int32 Copied = 0;
	for (USkeletalMeshSocket* Socket : Source->GetActiveSocketList())
	{
		if (!Socket)
		{
			continue;
		}
		if (Target->FindSocket(Socket->SocketName))
		{
			continue;
		}
		if (Target->GetRefSkeleton().FindBoneIndex(Socket->BoneName) == INDEX_NONE)
		{
			UE_LOG(LogRPGSkeletonUtils, Warning, TEXT("Skipped %s: bone %s is not on %s"), *Socket->SocketName.ToString(), *Socket->BoneName.ToString(), *Target->GetName());
			continue;
		}

		UObject* Outer = (bToSkeleton && Target->GetSkeleton()) ? static_cast<UObject*>(Target->GetSkeleton()) : static_cast<UObject*>(Target);
		USkeletalMeshSocket* Copy = NewObject<USkeletalMeshSocket>(Outer);
		Copy->SocketName = Socket->SocketName;
		Copy->BoneName = Socket->BoneName;
		Copy->RelativeLocation = Socket->RelativeLocation;
		Copy->RelativeRotation = Socket->RelativeRotation;
		Copy->RelativeScale = Socket->RelativeScale;
		Copy->bForceAlwaysAnimated = Socket->bForceAlwaysAnimated;
		Target->AddSocket(Copy, bToSkeleton);
		UE_LOG(LogRPGSkeletonUtils, Display, TEXT("Copied socket %s on %s"), *Copy->SocketName.ToString(), *Copy->BoneName.ToString());
		++Copied;
	}
	if (Copied > 0)
	{
		Target->MarkPackageDirty();
		if (bToSkeleton && Target->GetSkeleton())
		{
			Target->GetSkeleton()->MarkPackageDirty();
		}
	}
	return Copied;
#else
	return 0;
#endif
}

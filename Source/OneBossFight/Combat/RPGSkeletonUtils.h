// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RPGSkeletonUtils.generated.h"

class USkeletalMesh;

/**
 * Authoring helpers for editor scripts. Python cannot set a skeletal mesh socket's name (read-only property), so sockets
 * are copied here. Used to give Greystone the weapon sockets of the Advanced ARPG pack's mannequin.
 */
UCLASS()
class ONEBOSSFIGHT_API URPGSkeletonUtils : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Copies every socket of Source that Target does not have yet, under the same name, bone and transform. Sockets on bones
	 * Target lacks are skipped. bToSkeleton adds them to the target's skeleton (shared by all meshes of it), otherwise only
	 * to the mesh. Returns the number copied; logs each socket copied or skipped.
	 */
	UFUNCTION(BlueprintCallable, Category = "RPG|Authoring")
	static int32 CopySockets(USkeletalMesh* Source, USkeletalMesh* Target, bool bToSkeleton);
};

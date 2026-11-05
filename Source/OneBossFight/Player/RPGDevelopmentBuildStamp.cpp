// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGDevelopmentBuildStamp.h"

#if UE_BUILD_DEVELOPMENT
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HAL/PlatformApplicationMisc.h"
#include "Misc/App.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

namespace RPGDevelopmentBuildStamp
{
	void ShowIfAvailable(const UWorld& World)
	{
		static bool bShown = false;
		if (bShown || !World.IsGameWorld() || !FApp::IsGame() || !GEngine)
		{
			return;
		}
		bShown = true;

		FString BuildId;
		const FString StampPath = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("BuildStamp.txt"));
		FFileHelper::LoadFileToString(BuildId, *StampPath);
		BuildId.TrimStartAndEndInline();
		if (BuildId.IsEmpty())
		{
			BuildId = TEXT("UNSTAMPED");
		}
		GEngine->AddOnScreenDebugMessage(
			-1, 30.0f, FColor::Cyan,
			FString::Printf(TEXT("One Boss Fight | DEVELOPMENT BUILD %s"), *BuildId));
	}
}
#else
namespace RPGDevelopmentBuildStamp
{
	void ShowIfAvailable(const UWorld&) {}
}
#endif

// Copyright One Boss Fight. All Rights Reserved.
#include "RPGBossCardValidationLibrary.h"

#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGBossMoveCard.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimSequenceBase.h"
#include "UObject/StrongObjectPtr.h"

bool URPGBossCardValidationLibrary::ValidateMoveCardMetadata(const FRPGBossMoveCardSpec& Spec,
	const FRPGBossMoveMetadata& Metadata, TArray<FString>& OutDiagnostics)
{
	OutDiagnostics.Reset();
	const FRPGBossMoveIssues Issues = RPGBossMoveCards::Validate(Spec, Metadata);
	OutDiagnostics = Issues.Errors;
	if (Issues.IsValid())
	{
		TSharedPtr<const FRPGCompiledBossMoveCard> Preview;
		const FRPGBossMoveIssues CompileIssues = RPGBossMoveCards::CompileMetadata(Spec, Metadata, Preview);
		OutDiagnostics.Append(CompileIssues.Errors);
		return CompileIssues.IsValid() && Preview.IsValid();
	}
	return false;
}

bool URPGBossCardValidationLibrary::ValidateMoveCard(URPGBossMoveCard* Card, USkeletalMesh* Mesh,
	TArray<FString>& OutDiagnostics)
{
	OutDiagnostics.Reset();
	if (!IsInGameThread())
	{
		OutDiagnostics.Add(TEXT("MoveCard.NotGameThread[ValidateMoveCard]"));
		return false;
	}
	if (!IsValid(Card) || !IsValid(Mesh))
	{
		OutDiagnostics.Add(TEXT("MoveCard.ResolvedObject[card/mesh]"));
		return false;
	}

	const FRPGBossMoveCardSpec& Spec = Card->Spec;
	USkeleton* Skeleton = Spec.Skeleton.LoadSynchronous();
	UAnimSequenceBase* Animation = Spec.Sequence.IsNull()
		? Cast<UAnimSequenceBase>(Spec.Montage.LoadSynchronous())
		: Cast<UAnimSequenceBase>(Spec.Sequence.LoadSynchronous());
	TSharedPtr<const FRPGCompiledBossMoveCard> Resolved;
	const FRPGBossMoveIssues Issues = RPGBossMoveCards::CompileResolved(Spec, Skeleton, Animation, Mesh, Resolved);
	OutDiagnostics = Issues.Errors;
	return Issues.IsValid() && Resolved.IsValid() && Resolved->HasResolvedAssets();
}

bool URPGBossCardValidationLibrary::ValidateFrameworkProfile(URPGBossFrameworkProfile* Profile,
	TArray<FString>& OutDiagnostics)
{
	OutDiagnostics.Reset();
	FString Error;
	TUniquePtr<FRPGFrameworkDependencies> Dependencies;
	if (!RPGFramework::ResolveProfile(Profile, Dependencies, Error))
	{
		OutDiagnostics.Add(Error.IsEmpty() ? TEXT("Framework.Profile.Resolve") : Error);
		return false;
	}
	return true;
}

FString URPGBossCardValidationLibrary::ValidateMoveCardReport(URPGBossMoveCard* Card, USkeletalMesh* Mesh)
{
	TArray<FString> Diagnostics;
	if (ValidateMoveCard(Card, Mesh, Diagnostics)) return TEXT("PASS");
	if (Diagnostics.IsEmpty()) Diagnostics.Add(TEXT("MoveCard.ValidatorReturnedFalseWithoutDiagnostic"));
	return TEXT("FAIL|") + FString::Join(Diagnostics, TEXT(";"));
}

FString URPGBossCardValidationLibrary::ValidateFrameworkProfileReport(URPGBossFrameworkProfile* Profile)
{
	TArray<FString> Diagnostics;
	if (ValidateFrameworkProfile(Profile, Diagnostics)) return TEXT("PASS");
	if (Diagnostics.IsEmpty()) Diagnostics.Add(TEXT("Framework.Profile.ValidatorReturnedFalseWithoutDiagnostic"));
	return TEXT("FAIL|") + FString::Join(Diagnostics, TEXT(";"));
}

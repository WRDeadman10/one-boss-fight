// Copyright One Boss Fight. All Rights Reserved.
#include "Scratch/RPGScratchRouteA.h"

#include "AIController.h"
#include "Animation/AnimInstance.h"
#include "BehaviorTree/BehaviorTree.h"
#include "BehaviorTree/BehaviorTreeComponent.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "BehaviorTree/BlackboardData.h"
#include "BehaviorTree/Composites/BTComposite_Selector.h"
#include "BehaviorTree/Composites/BTComposite_Sequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"

#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/PackageName.h"
#include "UObject/Package.h"
#include "UObject/SavePackage.h"
#endif

DEFINE_LOG_CATEGORY_STATIC(LogRPGScratch, Log, All);

namespace
{
	// Scratch state: one ordered report for the whole test, never read by gameplay code.
	TArray<FString>& Report()
	{
		static TArray<FString> Lines;
		return Lines;
	}
	int32 NextSequence = 0;
	int32 NextReservation = 0;

	void Note(const FString& Text)
	{
		const FString Line = FString::Printf(TEXT("#%d %s"), ++NextSequence, *Text);
		Report().Add(Line);
		UE_LOG(LogRPGScratch, Display, TEXT("[ScratchRouteA] %s"), *Line);
	}

	FString CurrentMontageName(const APawn* Pawn)
	{
		const ACharacter* Character = Cast<ACharacter>(Pawn);
		const UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
		const UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
		return Montage ? Montage->GetName() : FString(TEXT("none"));
	}
}

EBTNodeResult::Type URPGScratchRouteATask::ExecuteTask(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory)
{
	AAIController* Controller = OwnerComp.GetAIOwner();
	APawn* Pawn = Controller ? Controller->GetPawn() : nullptr;
	Note(FString::Printf(TEXT("ENTRY task=%s deny=%d pawn=%s controller=%s"), *GetName(), bDenyReservation ? 1 : 0,
		Pawn ? *Pawn->GetName() : TEXT("none"), Controller ? *Controller->GetClass()->GetName() : TEXT("none")));
	if (!Pawn)
	{
		return EBTNodeResult::Failed;
	}

	const int32 Reservation = ++NextReservation;
	Note(FString::Printf(TEXT("RESERVATION id=%d allocated before any pack call (montage now=%s)"), Reservation, *CurrentMontageName(Pawn)));
	if (bDenyReservation)
	{
		Note(FString::Printf(TEXT("REJECTED id=%d: the pack was not called (montage now=%s)"), Reservation, *CurrentMontageName(Pawn)));
		return EBTNodeResult::Failed;
	}

	const FString BeforeMontage = CurrentMontageName(Pawn);
	Note(FString::Printf(TEXT("PACK_CALL id=%d tag=%s montage before=%s"), Reservation, *AbilityTag.ToString(), *BeforeMontage));
	const bool bActivated = RPGPack::TryActivateByTag(Pawn, *AbilityTag.ToString(), false);
	Note(FString::Printf(TEXT("PACK_RESULT id=%d activated=%d montage right after the call=%s"), Reservation, bActivated ? 1 : 0, *CurrentMontageName(Pawn)));
	return bActivated ? EBTNodeResult::Succeeded : EBTNodeResult::Failed;
}

FString URPGScratchRouteATask::GetStaticDescription() const
{
	return FString::Printf(TEXT("Scratch route (a): %s deny=%d"), *AbilityTag.ToString(), bDenyReservation ? 1 : 0);
}

bool URPGScratchRouteALibrary::CreateScratchBehaviorTree(const FString& PackagePath, const FString& BlackboardPath, FString& OutError)
{
#if WITH_EDITOR
	if (!PackagePath.StartsWith(TEXT("/Game/OneBossFight/Scratch/")))
	{
		OutError = TEXT("refused: scratch trees only under /Game/OneBossFight/Scratch/");
		return false;
	}
	if (FPackageName::DoesPackageExist(PackagePath))
	{
		OutError = TEXT("refused: package exists, never overwritten");
		return false;
	}
	UBlackboardData* Blackboard = LoadObject<UBlackboardData>(nullptr, *BlackboardPath);
	if (!Blackboard)
	{
		OutError = TEXT("blackboard asset not found: ") + BlackboardPath;
		return false;
	}
	UPackage* Package = CreatePackage(*PackagePath);
	const FString Name = FPackageName::GetShortName(PackagePath);
	UBehaviorTree* Tree = NewObject<UBehaviorTree>(Package, *Name, RF_Public | RF_Standalone);
	Tree->BlackboardAsset = Blackboard;

	auto MakeTask = [Tree](bool bDeny)
	{
		URPGScratchRouteATask* Task = NewObject<URPGScratchRouteATask>(Tree);
		Task->bDenyReservation = bDeny;
		Task->NodeName = bDeny ? TEXT("ScratchDenied") : TEXT("ScratchAllowed");
		return Task;
	};
	auto MakeSequence = [Tree](URPGScratchRouteATask* Task, const TCHAR* Label)
	{
		UBTComposite_Sequence* Sequence = NewObject<UBTComposite_Sequence>(Tree);
		Sequence->NodeName = Label;
		Sequence->Children.AddDefaulted(1);
		Sequence->Children[0].ChildTask = Task;
		return Sequence;
	};
	UBTComposite_Selector* Root = NewObject<UBTComposite_Selector>(Tree);
	Root->NodeName = TEXT("ScratchRoot");
	Root->Children.AddDefaulted(2);
	Root->Children[0].ChildComposite = MakeSequence(MakeTask(true), TEXT("DeniedFirst"));
	Root->Children[1].ChildComposite = MakeSequence(MakeTask(false), TEXT("AllowedSecond"));
	Tree->RootNode = Root;

	FAssetRegistryModule::AssetCreated(Tree);
	Package->MarkPackageDirty();
	const FString File = FPackageName::LongPackageNameToFilename(PackagePath, FPackageName::GetAssetPackageExtension());
	FSavePackageArgs Args;
	Args.TopLevelFlags = RF_Public | RF_Standalone;
	if (!UPackage::SavePackage(Package, Tree, *File, Args))
	{
		OutError = TEXT("save failed: ") + File;
		return false;
	}
	return true;
#else
	OutError = TEXT("editor only");
	return false;
#endif
}

AActor* URPGScratchRouteALibrary::SpawnBossWithInfo(UObject* WorldContext, UClass* BossClass, UObject* InfoAsset, FVector Location, FString& OutError)
{
	if (!WorldContext || !BossClass || !InfoAsset)
	{
		OutError = TEXT("missing world, class or info");
		return nullptr;
	}
	const FTransform Transform(FRotator::ZeroRotator, Location);
	AActor* Boss = UGameplayStatics::BeginDeferredActorSpawnFromClass(WorldContext, BossClass, Transform, ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Boss)
	{
		OutError = TEXT("deferred spawn failed");
		return nullptr;
	}
	FObjectProperty* Property = CastField<FObjectProperty>(Boss->GetClass()->FindPropertyByName(TEXT("EnemyInfoRef")));
	if (!Property || !InfoAsset->IsA(Property->PropertyClass))
	{
		OutError = TEXT("EnemyInfoRef property missing or the info asset has the wrong class");
		Boss->Destroy();
		return nullptr;
	}
	Property->SetObjectPropertyValue_InContainer(Boss, InfoAsset);
	UGameplayStatics::FinishSpawningActor(Boss, Transform);
	if (APawn* Pawn = Cast<APawn>(Boss); Pawn && !Pawn->GetController())
	{
		Pawn->SpawnDefaultController();
	}
	return Boss;
}

FString URPGScratchRouteALibrary::DescribeAI(AActor* Boss)
{
	if (!Boss)
	{
		return TEXT("no actor");
	}
	FString Info = TEXT("no EnemyInfoRef property");
	if (const FObjectProperty* Property = CastField<FObjectProperty>(Boss->GetClass()->FindPropertyByName(TEXT("EnemyInfoRef"))))
	{
		const UObject* Value = Property->GetObjectPropertyValue_InContainer(Boss);
		Info = Value ? Value->GetPathName() : FString(TEXT("None"));
	}
	const APawn* Pawn = Cast<APawn>(Boss);
	const AAIController* Controller = Pawn ? Cast<AAIController>(Pawn->GetController()) : nullptr;
	const UBehaviorTreeComponent* Brain = Controller ? Cast<UBehaviorTreeComponent>(Controller->BrainComponent) : nullptr;
	const UBehaviorTree* Tree = Brain ? Brain->GetCurrentTree() : nullptr;
	const UBlackboardComponent* Board = Controller ? Controller->GetBlackboardComponent() : nullptr;
	const UBlackboardData* BoardAsset = Board ? Board->GetBlackboardAsset() : nullptr;
	return FString::Printf(TEXT("actor=%s class=%s EnemyInfoRef=%s controller=%s brain=%s running=%d tree=%s blackboard=%s"),
		*Boss->GetName(), *Boss->GetClass()->GetName(), *Info,
		Controller ? *Controller->GetClass()->GetName() : TEXT("none"),
		Brain ? *Brain->GetClass()->GetName() : TEXT("none"), Brain && Brain->IsRunning() ? 1 : 0,
		Tree ? *Tree->GetPathName() : TEXT("none"), BoardAsset ? *BoardAsset->GetPathName() : TEXT("none"));
}

TArray<FString> URPGScratchRouteALibrary::GetRouteAReport()
{
	return Report();
}

void URPGScratchRouteALibrary::ResetRouteAReport()
{
	Report().Reset();
	NextSequence = 0;
	NextReservation = 0;
}

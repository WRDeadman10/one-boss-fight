// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGCameraProbe.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Camera/PlayerCameraManager.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarCameraProbe(TEXT("rpg.CameraProbe"),0,TEXT("Measurement (BOSS-QA-006): 1 = log the framework boss place on the player screen four times a second (camera_frame lines); 2 = also stage the player at 300, 600 and 900 cm; 3 = as 2 with the camera turned away at 900 (negative control). 0 = off."),ECVF_Default);
#endif

void URPGCameraProbe::Tick(float DeltaTime)
{
#if !UE_BUILD_SHIPPING
    if (CVarCameraProbe.GetValueOnGameThread()<=0) return;
    SinceLastSample+=DeltaTime; if (SinceLastSample<.25) return; SinceLastSample=0.;
    UWorld* World=GetWorld(); APlayerController* PC=World?UGameplayStatics::GetPlayerController(World,0):nullptr; if (!PC||!PC->PlayerCameraManager||!PC->GetPawn()) return;
    ARPGFrameworkBossCharacter* Boss=nullptr; for (TActorIterator<ARPGFrameworkBossCharacter> It(World);It;++It) {Boss=*It;break;} if (!Boss) return;
    int32 ViewX=0, ViewY=0; PC->GetViewportSize(ViewX,ViewY); if (ViewX<=0||ViewY<=0) return;
    // The boss's box projected corner by corner; a corner behind the camera or off the screen makes the box not fully inside.
    FVector Origin, Extent; Boss->GetActorBounds(true,Origin,Extent);
    double MinX=1.e9,MinY=1.e9,MaxX=-1.e9,MaxY=-1.e9; int32 OnScreen=0;
    for (int32 I=0;I<8;++I)
    {
        const FVector Corner=Origin+FVector((I&1)?Extent.X:-Extent.X,(I&2)?Extent.Y:-Extent.Y,(I&4)?Extent.Z:-Extent.Z);
        FVector2D Screen; if (UGameplayStatics::ProjectWorldToScreen(PC,Corner,Screen,false))
        {
            MinX=FMath::Min(MinX,double(Screen.X));MinY=FMath::Min(MinY,double(Screen.Y));MaxX=FMath::Max(MaxX,double(Screen.X));MaxY=FMath::Max(MaxY,double(Screen.Y));
            if (Screen.X>=0.&&Screen.X<=ViewX&&Screen.Y>=0.&&Screen.Y<=ViewY) ++OnScreen;
        }
    }
    const double MarginX=ViewX*.05, MarginY=ViewY*.05;
    const bool bInside=OnScreen==8&&MinX>=MarginX&&MaxX<=ViewX-MarginX&&MinY>=MarginY&&MaxY<=ViewY-MarginY;
    const double HeightPct=(MaxY>MinY)?100.*(MaxY-MinY)/double(ViewY):0.;
    // Occlusion: the line from the camera to the boss's chest, both actors ignored.
    FHitResult Hit; FCollisionQueryParams Params(SCENE_QUERY_STAT(CameraProbe),false,Boss); Params.AddIgnoredActor(PC->GetPawn());
    const FVector Chest=Boss->GetActorLocation()+FVector(0.,0.,60.);
    const bool bBlocked=World->LineTraceSingleByChannel(Hit,PC->PlayerCameraManager->GetCameraLocation(),Chest,ECC_Visibility,Params);
    // Stage mode: wait until the distance has not changed for 3 samples (the boss has arrived and stands), then walk the player through the bands. The player keeps its height and facing; only the place changes.
    const int32 Mode=CVarCameraProbe.GetValueOnGameThread();   // 2 = stage the bands; 3 = the same, and the camera is turned 90 degrees away at the last band (NEGATIVE CONTROL: the boss must leave the screen)
    if (Mode==2||Mode==3)
    {
        const double Dist=FVector::Dist2D(PC->GetPawn()->GetActorLocation(),Boss->GetActorLocation());
        static const double Bands[]={300.,600.,900.};
        if (StageIndex<0) { StillSamples=(LastDistance>=0.&&FMath::Abs(Dist-LastDistance)<1.)?StillSamples+1:0; LastDistance=Dist; if (StillSamples>=3) StageIndex=-2; }
        if (StageIndex==-2||(StageIndex>=0&&StageIndex<3&&World->GetTimeSeconds()-StageSince>=2.))
        {
            StageIndex=(StageIndex==-2)?0:StageIndex+1; StageSince=World->GetTimeSeconds();
            if (StageIndex<3)
            {
                const FVector To=Boss->GetActorLocation()-PC->GetPawn()->GetActorLocation(); FVector Dir=To; Dir.Z=0.; Dir=Dir.GetSafeNormal();
                const FVector NewLoc=FVector(Boss->GetActorLocation().X,Boss->GetActorLocation().Y,PC->GetPawn()->GetActorLocation().Z)-Dir*Bands[StageIndex];
                PC->GetPawn()->SetActorLocation(NewLoc,false,nullptr,ETeleportType::TeleportPhysics);
                if (Mode==3&&StageIndex==2) PC->SetControlRotation(PC->GetControlRotation()+FRotator(0.,90.,0.));
                UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] camera_stage index=%d distanceCm=%g cameraTurnedAway=%d"),StageIndex,Bands[StageIndex],(Mode==3&&StageIndex==2)?1:0);
            }
        }
    }
    UE_LOG(LogTemp,Display,TEXT("[FrameworkProof] camera_frame t=%.2f distCm=%g screenMinX=%.1f screenMinY=%.1f screenMaxX=%.1f screenMaxY=%.1f viewX=%d viewY=%d cornersOnScreen=%d insideMargin=%d heightPct=%.2f occluded=%d"),
        World->GetTimeSeconds(),FVector::Dist2D(PC->GetPawn()->GetActorLocation(),Boss->GetActorLocation()),MinX,MinY,MaxX,MaxY,ViewX,ViewY,OnScreen,bInside?1:0,HeightPct,bBlocked?1:0);
#endif
}

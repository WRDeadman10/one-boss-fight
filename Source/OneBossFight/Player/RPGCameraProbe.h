// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "RPGCameraProbe.generated.h"

/**
 * BOSS-QA-006 (camera and readability): a measurement, not a camera. While the console variable rpg.CameraProbe is 1 and a game world has a framework boss and a player controller, it logs four times a second
 * where the boss's bounding box falls on the PLAYER's screen: the projected box, the viewport, whether the whole box is inside the viewport with a margin, how much of the screen height it covers, and whether a line
 * from the camera to the boss's chest is blocked. The evaluation (distance bands, thresholds) is done on the log by Docs/BossCombatReview/Execution/Claude/B_QA006/evaluate_framing.py. Not compiled into shipping builds.
 */
UCLASS()
class ONEBOSSFIGHT_API URPGCameraProbe : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(URPGCameraProbe, STATGROUP_Tickables); }
    virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override { return WorldType == EWorldType::Game || WorldType == EWorldType::PIE; }
private:
    double SinceLastSample = 0.;
    // Stage mode (rpg.CameraProbe 2): once the boss stands still the player is placed at 300, 600 and 900 cm from it, 2 s each, so every distance band is measured.
    double LastDistance = -1.; int32 StillSamples = 0, StageIndex = -1; double StageSince = 0.;
};

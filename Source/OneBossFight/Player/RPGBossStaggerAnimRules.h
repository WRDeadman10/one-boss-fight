// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
/**
 * F11 (owner decision 3, Option B, spec Antigravity/Reviews/F11_STAGGER_PHASE_ANIM_SPEC.md): pure rules of the stagger and phase transition animations. Header only, no UObject, so the boss and an automation
 * test share them. StaggerSeconds stays the TOTAL stagger time: Start plays first, Loop fills the middle, End starts at Total - EndLength and finishes with the stagger. The state is a pure function of the
 * elapsed time (no montage-ended callbacks).
 */
namespace RPGStaggerAnim
{
    enum class EState : uint8 { Start, Loop, End, Finished };

    /** Plain inputs of the profile checks (lengths in seconds, skeleton and slot names as text), so the checks run without loading assets. */
    struct FPureParams
    {
        bool bStart=false,bLoop=false,bEnd=false;          // which of the three stagger clips are set
        float StartLen=0.f,LoopLen=0.f,EndLen=0.f,Total=0.f; // clip lengths and StaggerSeconds
        FString BossSkeleton,StartSkeleton,LoopSkeleton,EndSkeleton;
        FName Slot;
        bool bSlotNodePresent=true;                          // false when the boss AnimBP has no slot node of that name
    };

    /** Empty string = valid, else the failure token (first failure wins, order as the spec section 3). All three clips set or none; every clip on the boss skeleton; Start+End must fit in Total. */
    inline FString Validate(const FPureParams& P)
    {
        const int32 Set=int32(P.bStart)+int32(P.bLoop)+int32(P.bEnd);
        if (Set==0) return FString();
        if (Set!=3) return TEXT("Framework.Profile.StaggerAnim.CoherentSet");
        if (P.StartSkeleton!=P.BossSkeleton) return TEXT("Framework.Profile.StaggerAnim.StartSkeleton");
        if (P.LoopSkeleton!=P.BossSkeleton) return TEXT("Framework.Profile.StaggerAnim.LoopSkeleton");
        if (P.EndSkeleton!=P.BossSkeleton) return TEXT("Framework.Profile.StaggerAnim.EndSkeleton");
        if (P.Slot.IsNone()) return TEXT("Framework.Profile.StaggerAnim.SlotNameEmpty");
        if (!FMath::IsFinite(P.StartLen)||!FMath::IsFinite(P.EndLen)||!FMath::IsFinite(P.LoopLen)||!FMath::IsFinite(P.Total)||P.StartLen<=0.f||P.LoopLen<=0.f||P.EndLen<=0.f||P.StartLen+P.EndLen>P.Total)
            return TEXT("Framework.Profile.StaggerAnim.TooShort");
        if (!P.bSlotNodePresent) return TEXT("Framework.Profile.StaggerAnim.SlotNode");
        return FString();
    }

    /** Sub state at Dt seconds after the break. Start for Dt < StartLen, Loop until Total - EndLen, End until Total, then Finished. */
    inline EState Evaluate(float StartLen,float EndLen,float Total,float Dt)
    {
        if (Dt>=Total) return EState::Finished;
        if (Dt>=Total-EndLen) return EState::End;
        if (Dt>=StartLen) return EState::Loop;
        return EState::Start;
    }

    /** Loops the Loop clip is asked for: ceil(middle / LoopLen), middle = Total - StartLen - EndLen. 0 when there is no middle or no loop length. The loop is stopped at Total - EndLen anyway. */
    inline int32 LoopCount(float Total,float StartLen,float EndLen,float LoopLen)
    {
        const float Middle=Total-StartLen-EndLen;
        if (!(Middle>0.f)||!(LoopLen>0.f)) return 0;
        return int32(FMath::CeilToInt(Middle/LoopLen));
    }

    /** Phase transition: the selector is held for the clip length from the latch (0 or less = no clip = no hold, F6c behaviour). */
    inline bool PhaseHoldActive(float ClipLen,float Elapsed) { return ClipLen>0.f && Elapsed<ClipLen; }

    /** Profile level phase clip check: a clip needs a second phase (fraction in (0,1), a name) and a slot name. Empty = valid. */
    inline FString ValidatePhaseClip(bool bClip,float PhaseTwoFraction,FName PhaseTwoId,FName Slot,const FString& BossSkeleton,const FString& ClipSkeleton)
    {
        if (!bClip) return FString();
        if (!(PhaseTwoFraction>0.f)||PhaseTwoId.IsNone()) return TEXT("Framework.Profile.PhaseTransitionAnim.Phaseless");
        if (ClipSkeleton!=BossSkeleton) return TEXT("Framework.Profile.PhaseTransitionAnim.Skeleton");
        if (Slot.IsNone()) return TEXT("Framework.Profile.StaggerAnim.SlotNameEmpty");
        return FString();
    }
}

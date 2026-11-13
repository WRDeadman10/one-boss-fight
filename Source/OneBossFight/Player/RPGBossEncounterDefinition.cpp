// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossEncounterDefinition.h"
#include "Player/RPGBossFrameworkProfile.h"

bool URPGBossEncounterDefinition::ValidateSelectionRecord(FString& OutError) const
{
	OutError.Reset();
	auto Fail = [&OutError](const TCHAR* Token)
	{
		OutError = Token;
		return false;
	};
	if (Schema != 1) return Fail(TEXT("EncounterDefinition.Schema"));
	if (!EncounterInstance.IsValid()) return Fail(TEXT("EncounterDefinition.InstanceId"));
	if (BossSlot.IsNone() || PlayerSlot.IsNone() || BossSlot == PlayerSlot) return Fail(TEXT("EncounterDefinition.Slots"));
	if (InitialBossPhase.IsNone()) return Fail(TEXT("EncounterDefinition.Phase"));
	if (BossDefinition.IsNull() || PlayerDefinition.IsNull()) return Fail(TEXT("EncounterDefinition.Definitions"));
	if (BossDefinition.ToSoftObjectPath() == PlayerDefinition.ToSoftObjectPath()) return Fail(TEXT("EncounterDefinition.DefinitionsNotDistinct"));
	if ((bUseFrameworkBoss && FrameworkBossProfile.IsNull()) || (!bUseFrameworkBoss && !FrameworkBossProfile.IsNull()))
		return Fail(TEXT("EncounterDefinition.FrameworkProfile"));
	if (StableManifestHash.Len() != 64) return Fail(TEXT("EncounterDefinition.ManifestShape"));
	for (TCHAR C : StableManifestHash)
	{
		if (!FChar::IsHexDigit(C)) return Fail(TEXT("EncounterDefinition.ManifestShape"));
	}
	return true;
}

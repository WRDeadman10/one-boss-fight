// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "Commandlets/Commandlet.h"
#include "EmberMontageTimingAuditCommandlet.generated.h"

/** Read-only audit of Ember montage timing annotations against the native tracker defaults. */
UCLASS()
class ONEBOSSFIGHTEDITOR_API UEmberMontageTimingAuditCommandlet : public UCommandlet
{
	GENERATED_BODY()

public:
	UEmberMontageTimingAuditCommandlet();
	virtual int32 Main(const FString& Params) override;
};

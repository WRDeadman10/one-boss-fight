#pragma once

#include "Commandlets/Commandlet.h"
#include "AuraBoostLiteGraphAuthoringCommandlet.generated.h"

UCLASS()
class ONEBOSSFIGHTEDITOR_API UAuraBoostLiteGraphAuthoringCommandlet : public UCommandlet
{
	GENERATED_BODY()

public:
	UAuraBoostLiteGraphAuthoringCommandlet();
	virtual int32 Main(const FString& Params) override;
};

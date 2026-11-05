// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "Components/ActorComponent.h"
#include "UObject/WeakObjectPtr.h"

/** Installs an explicit same-frame dependency for components that consume tracker state in TickComponent. */
namespace RPGBossTrackerTickPrerequisite
{
	inline bool Add(UActorComponent& Consumer, TWeakObjectPtr<UActorComponent>& BoundTracker, UActorComponent* Tracker)
	{
		if (!Tracker || Tracker == &Consumer || Tracker->GetOwner() != Consumer.GetOwner())
		{
			return false;
		}
		if (BoundTracker.Get() == Tracker)
		{
			return true;
		}
		Consumer.AddTickPrerequisiteComponent(Tracker);
		BoundTracker = Tracker;
		return true;
	}
}

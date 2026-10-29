# Itemised changed assertions (source-only, unrun)
Every changed assertion is recorded with its old/new line and complete expression. Sequence replacement blocks are paired in order; new prefix/suffix rows have no old assertion. The full diff remains authoritative for surrounding logic.

## 1. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line376:
```cpp
TestEqual(TEXT("boss-core has five plans"), Boss.Plans.Num(), 5)
```

new line391:
```cpp
TestEqual(TEXT("boss-core has twelve plans"), Boss.Plans.Num(), 12)
```

## 2. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line380:
```cpp
TestTrue(TEXT("plan classes in the deterministic relative order Stagger, Phases, Encounter, DormantWake, Posture"), Boss.Plans[0].Class == URPGBossStagger::StaticClass() && Boss.Plans[1].Class == URPGBossPhases::StaticClass()
		&& Boss.Plans[2].Class == URPGBossEncounter::StaticClass() && Boss.Plans[3].Class == URPGBossDormantWake::StaticClass() && Boss.Plans[4].Class == URPGBossPosture::StaticClass())
```

new line395:
```cpp
TestTrue(TEXT("plan classes in the deterministic relative order Stagger, Phases, Encounter, DormantWake, Posture"), Boss.Plans[0].Class == URPGBossStagger::StaticClass() && Boss.Plans[1].Class == URPGBossPhases::StaticClass()
		&& Boss.Plans[2].Class == URPGBossEncounter::StaticClass() && Boss.Plans[3].Class == URPGBossDormantWake::StaticClass() && Boss.Plans[4].Class == URPGBossPosture::StaticClass() && Boss.Plans[5].Class == URPGBossBleed::StaticClass() && Boss.Plans[6].Class == URPGBossLowSweep::StaticClass() && Boss.Plans[7].Class == URPGBossShockwave::StaticClass() && Boss.Plans[8].Class == URPGBossHealPunish::StaticClass() && Boss.Plans[9].Class == URPGBossLook::StaticClass() && Boss.Plans[10].Class == URPGBossCloseClipSwap::StaticClass() && Boss.Plans[11].Class == URPGBossDeath::StaticClass())
```

## 3. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line382:
```cpp
TestTrue(TEXT("plan instance names are the legacy names"), Boss.Plans[0].InstanceName == FName(TEXT("RPGBossStagger")) && Boss.Plans[1].InstanceName == FName(TEXT("RPGBossPhases")) && Boss.Plans[2].InstanceName == FName(TEXT("RPGBossEncounter"))
		&& Boss.Plans[3].InstanceName == FName(TEXT("RPGBossDormantWake")) && Boss.Plans[4].InstanceName == FName(TEXT("RPGBossPosture")))
```

new line397:
```cpp
TestTrue(TEXT("plan instance names are the legacy names"), Boss.Plans[0].InstanceName == FName(TEXT("RPGBossStagger")) && Boss.Plans[1].InstanceName == FName(TEXT("RPGBossPhases")) && Boss.Plans[2].InstanceName == FName(TEXT("RPGBossEncounter"))
		&& Boss.Plans[3].InstanceName == FName(TEXT("RPGBossDormantWake")) && Boss.Plans[4].InstanceName == FName(TEXT("RPGBossPosture")) && Boss.Plans[5].InstanceName == FName(TEXT("RPGBossBleed")) && Boss.Plans[6].InstanceName == FName(TEXT("RPGBossLowSweep")) && Boss.Plans[7].InstanceName == FName(TEXT("RPGBossShockwave")) && Boss.Plans[8].InstanceName == FName(TEXT("RPGBossHealPunish")) && Boss.Plans[9].InstanceName == FName(TEXT("RPGBossLook")) && Boss.Plans[10].InstanceName == FName(TEXT("RPGBossCloseClipSwap")) && Boss.Plans[11].InstanceName == FName(TEXT("RPGBossDeath")))
```

## 4. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line384:
```cpp
TestTrue(TEXT("the callbacks exist (they were built, never run)"), static_cast<bool>(Boss.Plans[0].Configure) && static_cast<bool>(Boss.Plans[1].Configure) && static_cast<bool>(Boss.Plans[2].Configure)
		&& static_cast<bool>(Boss.Plans[3].Configure) && static_cast<bool>(Boss.Plans[4].Configure))
```

new line399:
```cpp
TestTrue(TEXT("the callbacks exist (they were built, never run)"), static_cast<bool>(Boss.Plans[0].Configure) && static_cast<bool>(Boss.Plans[1].Configure) && static_cast<bool>(Boss.Plans[2].Configure)
		&& static_cast<bool>(Boss.Plans[3].Configure) && static_cast<bool>(Boss.Plans[4].Configure) && static_cast<bool>(Boss.Plans[5].Configure) && static_cast<bool>(Boss.Plans[6].Configure) && static_cast<bool>(Boss.Plans[7].Configure) && static_cast<bool>(Boss.Plans[8].Configure) && static_cast<bool>(Boss.Plans[9].Configure) && static_cast<bool>(Boss.Plans[10].Configure) && static_cast<bool>(Boss.Plans[11].Configure))
```

## 5. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line394:
```cpp
TestEqual(TEXT("the union of required manifest paths is fifty-one"), Required.Num(), 51)
```

new line409:
```cpp
TestEqual(TEXT("the union of required manifest paths is one hundred ten"), Required.Num(), 110)
```

## 6. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line399:
```cpp
TestEqual(TEXT("one class lease per boss plan"), Boss.ClassLeases.Num(), 5)
```

new line414:
```cpp
TestEqual(TEXT("one class lease per boss plan"), Boss.ClassLeases.Num(), 12)
```

## 7. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line400:
```cpp
TestTrue(TEXT("the class leases are the plan classes"), Boss.ClassLeases.Num() == 5 && Boss.ClassLeases[0].Get() == Boss.Plans[0].Class && Boss.ClassLeases[1].Get() == Boss.Plans[1].Class && Boss.ClassLeases[2].Get() == Boss.Plans[2].Class
		&& Boss.ClassLeases[3].Get() == Boss.Plans[3].Class && Boss.ClassLeases[4].Get() == Boss.Plans[4].Class)
```

new line415:
```cpp
TestTrue(TEXT("the class leases are the plan classes"), Boss.ClassLeases.Num() == 12 && Boss.ClassLeases[0].Get() == Boss.Plans[0].Class && Boss.ClassLeases[1].Get() == Boss.Plans[1].Class && Boss.ClassLeases[2].Get() == Boss.Plans[2].Class
		&& Boss.ClassLeases[3].Get() == Boss.Plans[3].Class && Boss.ClassLeases[4].Get() == Boss.Plans[4].Class && Boss.ClassLeases[5].Get() == Boss.Plans[5].Class && Boss.ClassLeases[6].Get() == Boss.Plans[6].Class && Boss.ClassLeases[7].Get() == Boss.Plans[7].Class && Boss.ClassLeases[8].Get() == Boss.Plans[8].Class && Boss.ClassLeases[9].Get() == Boss.Plans[9].Class && Boss.ClassLeases[10].Get() == Boss.Plans[10].Class && Boss.ClassLeases[11].Get() == Boss.Plans[11].Class)
```

## 8. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line831:
```cpp
TestTrue(TEXT("only the boss has plans"), Out->Participants[0].Plans.IsEmpty() && Out->Participants[1].Plans.Num() == 5)
```

new line846:
```cpp
TestTrue(TEXT("only the boss has plans"), Out->Participants[0].Plans.IsEmpty() && Out->Participants[1].Plans.Num() == 12)
```

## 9. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line852:
```cpp
TestTrue(TEXT("two boss-core members targeting each other compile"), Result.IsReady() && Out.IsValid() && Out->Participants.Num() == 2 && Out->Participants[0].Plans.Num() == 5 && Out->Participants[1].Plans.Num() == 5)
```

new line867:
```cpp
TestTrue(TEXT("two boss-core members targeting each other compile"), Result.IsReady() && Out.IsValid() && Out->Participants.Num() == 2 && Out->Participants[0].Plans.Num() == 12 && Out->Participants[1].Plans.Num() == 12)
```

## 10. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line1035:
```cpp
TestTrue(FString::Printf(TEXT("%s: exactly five plans, a boss-core role and five class leases"), *Who), BossPlan.Role == ERPGPreflightRole::BossCore && BossPlan.Plans.Num() == 5 && BossPlan.ClassLeases.Num() == 5)
```

new line1050:
```cpp
TestTrue(FString::Printf(TEXT("%s: exactly twelve plans, a boss-core role and twelve class leases"), *Who), BossPlan.Role == ERPGPreflightRole::BossCore && BossPlan.Plans.Num() == 12 && BossPlan.ClassLeases.Num() == 12)
```

## 11. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line1058:
```cpp
TestTrue(FString::Printf(TEXT("%s: the classes are Stagger, Phases, Encounter, DormantWake, Posture in this order"), *Who), bClasses)
```

new line1054:
```cpp
TestTrue(FString::Printf(TEXT("%s: original five-plan prefix keeps its reviewed classes and names"), *Who),
			BossPlan.Plans[0].Class == URPGBossStagger::StaticClass() && BossPlan.Plans[0].InstanceName == FName(TEXT("RPGBossStagger"))
			&& BossPlan.Plans[1].Class == URPGBossPhases::StaticClass() && BossPlan.Plans[1].InstanceName == FName(TEXT("RPGBossPhases"))
			&& BossPlan.Plans[2].Class == URPGBossEncounter::StaticClass() && BossPlan.Plans[2].InstanceName == FName(TEXT("RPGBossEncounter"))
			&& BossPlan.Plans[3].Class == URPGBossDormantWake::StaticClass() && BossPlan.Plans[3].InstanceName == FName(TEXT("RPGBossDormantWake"))
			&& BossPlan.Plans[4].Class == URPGBossPosture::StaticClass() && BossPlan.Plans[4].InstanceName == FName(TEXT("RPGBossPosture")))
```

## 12. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old (no assertion at this sequence position)

new line1060:
```cpp
TestTrue(FString::Printf(TEXT("%s: seven typed additions occupy exactly indexes5 through11 in DD order"), *Who),
			BossPlan.Plans[5].Class == URPGBossBleed::StaticClass() && BossPlan.Plans[5].InstanceName == FName(TEXT("RPGBossBleed"))
			&& BossPlan.Plans[6].Class == URPGBossLowSweep::StaticClass() && BossPlan.Plans[6].InstanceName == FName(TEXT("RPGBossLowSweep"))
			&& BossPlan.Plans[7].Class == URPGBossShockwave::StaticClass() && BossPlan.Plans[7].InstanceName == FName(TEXT("RPGBossShockwave"))
			&& BossPlan.Plans[8].Class == URPGBossHealPunish::StaticClass() && BossPlan.Plans[8].InstanceName == FName(TEXT("RPGBossHealPunish"))
			&& BossPlan.Plans[9].Class == URPGBossLook::StaticClass() && BossPlan.Plans[9].InstanceName == FName(TEXT("RPGBossLook"))
			&& BossPlan.Plans[10].Class == URPGBossCloseClipSwap::StaticClass() && BossPlan.Plans[10].InstanceName == FName(TEXT("RPGBossCloseClipSwap"))
			&& BossPlan.Plans[11].Class == URPGBossDeath::StaticClass() && BossPlan.Plans[11].InstanceName == FName(TEXT("RPGBossDeath")))
```

## 13. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old (no assertion at this sequence position)

new line1087:
```cpp
TestTrue(FString::Printf(TEXT("%s: all twelve classes follow the reviewed prefix and DD-order suffix"), *Who), bClasses)
```

## 14. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line1061:
```cpp
TestTrue(FString::Printf(TEXT("%s: no native class and no instance name appears twice"), *Who), DistinctClasses.Num() == 5 && DistinctNames.Num() == 5)
```

new line1090:
```cpp
TestTrue(FString::Printf(TEXT("%s: no native class and no instance name appears twice"), *Who), DistinctClasses.Num() == 12 && DistinctNames.Num() == 12)
```

## 15. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line1069:
```cpp
TestTrue(FString::Printf(TEXT("%s: the union of the plans' required paths is exactly the 51 independent literal paths, each named by exactly one plan"), *Who), bUnion)
```

new line1098:
```cpp
TestTrue(FString::Printf(TEXT("%s: the union of the plans' required paths is exactly the 110 independent literal paths, each named by exactly one plan"), *Who), bUnion)
```

## 16. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line1105:
```cpp
TestTrue(TEXT("no managed consumer (no Stagger, DormantWake, Phases, Encounter, Posture or participant component) exists on any actor"), bNoConsumers)
```

new line1134:
```cpp
TestTrue(TEXT("none of the thirteen managed consumer classes exists on any actor"), bNoConsumers)
```

## 17. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line1106:
```cpp
TestTrue(TEXT("the managed consumers are the six expected classes"), RPGBossHydrationPreflight::ManagedCoreConsumerClasses().Num() == 6)
```

new line1135:
```cpp
TestTrue(TEXT("the managed consumers are the thirteen expected classes"), RPGBossHydrationPreflight::ManagedCoreConsumerClasses().Num() == 13)
```

## 18. Source/OneBossFight/Tests/RPGBossHydrationPreflightTests.cpp

old line1282:
```cpp
TestTrue(TEXT("the batch compiles"), RPGBossHydrationPreflight::CompilePreflight(F.Valid, Plan).IsReady() && Plan.IsValid() && Plan->Participants.Num() == 2 && Plan->Participants[0].Plans.Num() == 5)
```

new line1311:
```cpp
TestTrue(TEXT("the batch compiles"), RPGBossHydrationPreflight::CompilePreflight(F.Valid, Plan).IsReady() && Plan.IsValid() && Plan->Participants.Num() == 2 && Plan->Participants[0].Plans.Num() == 12)
```

## 19. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line330:
```cpp
TestEqual(TEXT("ten components are leased"), Batch.GetOwnedComponentCount(), 10)
```

new line352:
```cpp
TestEqual(TEXT("twenty-four components are leased"), Batch.GetOwnedComponentCount(), 24)
```

## 20. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line333:
```cpp
TestTrue(TEXT("ten distinct owned component pointers"), OwnedList.Num() == 10 && OwnedSet.Num() == 10)
```

new line355:
```cpp
TestTrue(TEXT("twenty-four distinct owned component pointers"), OwnedList.Num() == 24 && OwnedSet.Num() == 24)
```

## 21. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line367:
```cpp
TestTrue(FString::Printf(TEXT("%s: exactly five components were added and every unrelated component is still there"), *Label), bPriorKept)
```

new line389:
```cpp
TestTrue(FString::Printf(TEXT("%s: exactly twelve components were added and every unrelated component is still there"), *Label), bPriorKept)
```

## 22. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line386:
```cpp
TestTrue(TEXT("summary: slots, targets, roles, explicit phase ids and owned counts"),
				Infos[0].Slot == FName(TEXT("Boss1")) && Infos[0].TargetSlot == FName(TEXT("Player")) && Infos[0].Role == ERPGPreflightRole::BossCore && Infos[0].SelectedPhaseId == PhaseTwo && Infos[0].OwnedComponentCount == 5
				&& Infos[1].Slot == FName(TEXT("Boss2")) && Infos[1].TargetSlot == FName(TEXT("Player")) && Infos[1].Role == ERPGPreflightRole::BossCore && Infos[1].SelectedPhaseId == PhaseAlt && Infos[1].OwnedComponentCount == 5
				&& Infos[2].Slot == FName(TEXT("Player")) && Infos[2].TargetSlot == FName(TEXT("Boss1")) && Infos[2].Role == ERPGPreflightRole::TargetOnly && Infos[2].SelectedPhaseId.IsNone() && Infos[2].OwnedComponentCount == 0)
```

new line408:
```cpp
TestTrue(TEXT("summary: slots, targets, roles, explicit phase ids and owned counts"),
				Infos[0].Slot == FName(TEXT("Boss1")) && Infos[0].TargetSlot == FName(TEXT("Player")) && Infos[0].Role == ERPGPreflightRole::BossCore && Infos[0].SelectedPhaseId == PhaseTwo && Infos[0].OwnedComponentCount == 12
				&& Infos[1].Slot == FName(TEXT("Boss2")) && Infos[1].TargetSlot == FName(TEXT("Player")) && Infos[1].Role == ERPGPreflightRole::BossCore && Infos[1].SelectedPhaseId == PhaseAlt && Infos[1].OwnedComponentCount == 12
				&& Infos[2].Slot == FName(TEXT("Player")) && Infos[2].TargetSlot == FName(TEXT("Boss1")) && Infos[2].Role == ERPGPreflightRole::TargetOnly && Infos[2].SelectedPhaseId.IsNone() && Infos[2].OwnedComponentCount == 0)
```

## 23. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line425:
```cpp
TestTrue(FString::Printf(TEXT("%s: every owned component is destroyed (none resolves any more)"), Label), Weak.Num() == 10 && bGone)
```

new line447:
```cpp
TestTrue(FString::Printf(TEXT("%s: every owned component is destroyed (none resolves any more)"), Label), Weak.Num() == 24 && bGone)
```

## 24. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line453:
```cpp
TestTrue(TEXT("the abort destroyed ten components and found nothing else"), Report.Destroyed == 10 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && Report.IsClean())
```

new line475:
```cpp
TestTrue(TEXT("the abort destroyed twenty-four components and found nothing else"), Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && Report.IsClean())
```

## 25. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line479:
```cpp
TestTrue(TEXT("explicit abort: ten destroyed, none already gone, no violation, clean"), First.Destroyed == 10 && First.AlreadyGone == 0 && First.ContractViolations == 0 && First.IsClean() && !First.bRefused)
```

new line501:
```cpp
TestTrue(TEXT("explicit abort: twenty-four destroyed, none already gone, no violation, clean"), First.Destroyed == 24 && First.AlreadyGone == 0 && First.ContractViolations == 0 && First.IsClean() && !First.bRefused)
```

## 26. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line538:
```cpp
TestTrue(TEXT("the first artifact is intact: prepared, the same ten components, still unregistered and not begun"), First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 10 && First.Batch->OwnedComponentsForTest() == Snapshot)
```

new line560:
```cpp
TestTrue(TEXT("the first artifact is intact: prepared, the same twenty-four components, still unregistered and not begun"), First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 24 && First.Batch->OwnedComponentsForTest() == Snapshot)
```

## 27. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line544:
```cpp
TestTrue(TEXT("the first artifact aborts cleanly"), Report.Destroyed == 10 && Report.IsClean())
```

new line566:
```cpp
TestTrue(TEXT("the first artifact aborts cleanly"), Report.Destroyed == 24 && Report.IsClean())
```

## 28. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line679:
```cpp
TestTrue(TEXT("component destroyed first: nine destroyed by the abort, one already gone, no violation, clean"), Report.Destroyed == 9 && Report.AlreadyGone == 1 && Report.ContractViolations == 0 && Report.IsClean())
```

new line701:
```cpp
TestTrue(TEXT("component destroyed first: twenty-three destroyed by the abort, one already gone, no violation, clean"), Report.Destroyed == 23 && Report.AlreadyGone == 1 && Report.ContractViolations == 0 && Report.IsClean())
```

## 29. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line698:
```cpp
TestTrue(TEXT("owner destroyed first: the first boss's five are destroyed, the destroyed owner's five are already gone, no violation"), Report.Destroyed == 5 && Report.AlreadyGone == 5 && Report.ContractViolations == 0 && Report.IsClean())
```

new line720:
```cpp
TestTrue(TEXT("owner destroyed first: the first boss's twelve are destroyed, the destroyed owner's twelve are already gone, no violation"), Report.Destroyed == 12 && Report.AlreadyGone == 12 && Report.ContractViolations == 0 && Report.IsClean())
```

## 30. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line716:
```cpp
TestTrue(TEXT("world torn down first: every owned component is accounted for and nothing is reported as a registration violation"), Report.Destroyed + Report.AlreadyGone == 10 && Report.ContractViolations == 0 && Report.IsClean())
```

new line738:
```cpp
TestTrue(TEXT("world torn down first: every owned component is accounted for and nothing is reported as a registration violation"), Report.Destroyed + Report.AlreadyGone == 24 && Report.ContractViolations == 0 && Report.IsClean())
```

## 31. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line747:
```cpp
TestTrue(TEXT("registered by somebody else: nine destroyed, one contract violation, not clean"), Report.Destroyed == 9 && Report.ContractViolations == 1 && !Report.IsClean() && AnyErrorStartsWith(Report.Errors, TEXT("Preparation.ContractViolation")) && AnyErrorContains(Report.Errors, TEXT("RPGBossEncounter")))
```

new line769:
```cpp
TestTrue(TEXT("registered by somebody else: twenty-three destroyed, one contract violation, not clean"), Report.Destroyed == 23 && Report.ContractViolations == 1 && !Report.IsClean() && AnyErrorStartsWith(Report.Errors, TEXT("Preparation.ContractViolation")) && AnyErrorContains(Report.Errors, TEXT("RPGBossEncounter")))
```

## 32. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line778:
```cpp
TestTrue(TEXT("the artifact is still prepared with its ten components after the refused abort"), Result.Batch->IsPrepared() && Result.Batch->GetOwnedComponentCount() == 10)
```

new line800:
```cpp
TestTrue(TEXT("the artifact is still prepared with its twenty-four components after the refused abort"), Result.Batch->IsPrepared() && Result.Batch->GetOwnedComponentCount() == 24)
```

## 33. Source/OneBossFight/Tests/RPGBossHydrationPreparationTests.cpp

old line780:
```cpp
TestTrue(TEXT("the game-thread abort then succeeds"), Report.Destroyed == 10 && Report.IsClean())
```

new line802:
```cpp
TestTrue(TEXT("the game-thread abort then succeeds"), Report.Destroyed == 24 && Report.IsClean())
```

## 34. Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp

old line519:
```cpp
TestEqual(TEXT("the boss has five plans"), BossPlan.Plans.Num(), 5)
```

new line534:
```cpp
TestEqual(TEXT("the boss has twelve plans"), BossPlan.Plans.Num(), 12)
```

## 35. Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp

old line523:
```cpp
TestTrue(TEXT("plan classes in the relative order Stagger, Phases, Encounter, DormantWake, Posture"), BossPlan.Plans[0].Class == URPGBossStagger::StaticClass() && BossPlan.Plans[1].Class == URPGBossPhases::StaticClass()
		&& BossPlan.Plans[2].Class == URPGBossEncounter::StaticClass() && BossPlan.Plans[3].Class == URPGBossDormantWake::StaticClass() && BossPlan.Plans[4].Class == URPGBossPosture::StaticClass())
```

new line538:
```cpp
TestTrue(TEXT("plan classes in the relative order Stagger, Phases, Encounter, DormantWake, Posture"), BossPlan.Plans[0].Class == URPGBossStagger::StaticClass() && BossPlan.Plans[1].Class == URPGBossPhases::StaticClass()
		&& BossPlan.Plans[2].Class == URPGBossEncounter::StaticClass() && BossPlan.Plans[3].Class == URPGBossDormantWake::StaticClass() && BossPlan.Plans[4].Class == URPGBossPosture::StaticClass() && BossPlan.Plans[5].Class == URPGBossBleed::StaticClass() && BossPlan.Plans[6].Class == URPGBossLowSweep::StaticClass() && BossPlan.Plans[7].Class == URPGBossShockwave::StaticClass() && BossPlan.Plans[8].Class == URPGBossHealPunish::StaticClass() && BossPlan.Plans[9].Class == URPGBossLook::StaticClass() && BossPlan.Plans[10].Class == URPGBossCloseClipSwap::StaticClass() && BossPlan.Plans[11].Class == URPGBossDeath::StaticClass())
```

## 36. Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp

old line525:
```cpp
TestTrue(TEXT("plan instance names are the legacy names"), BossPlan.Plans[0].InstanceName == FName(TEXT("RPGBossStagger")) && BossPlan.Plans[1].InstanceName == FName(TEXT("RPGBossPhases")) && BossPlan.Plans[2].InstanceName == FName(TEXT("RPGBossEncounter"))
		&& BossPlan.Plans[3].InstanceName == FName(TEXT("RPGBossDormantWake")) && BossPlan.Plans[4].InstanceName == FName(TEXT("RPGBossPosture")))
```

new line540:
```cpp
TestTrue(TEXT("plan instance names are the legacy names"), BossPlan.Plans[0].InstanceName == FName(TEXT("RPGBossStagger")) && BossPlan.Plans[1].InstanceName == FName(TEXT("RPGBossPhases")) && BossPlan.Plans[2].InstanceName == FName(TEXT("RPGBossEncounter"))
		&& BossPlan.Plans[3].InstanceName == FName(TEXT("RPGBossDormantWake")) && BossPlan.Plans[4].InstanceName == FName(TEXT("RPGBossPosture")) && BossPlan.Plans[5].InstanceName == FName(TEXT("RPGBossBleed")) && BossPlan.Plans[6].InstanceName == FName(TEXT("RPGBossLowSweep")) && BossPlan.Plans[7].InstanceName == FName(TEXT("RPGBossShockwave")) && BossPlan.Plans[8].InstanceName == FName(TEXT("RPGBossHealPunish")) && BossPlan.Plans[9].InstanceName == FName(TEXT("RPGBossLook")) && BossPlan.Plans[10].InstanceName == FName(TEXT("RPGBossCloseClipSwap")) && BossPlan.Plans[11].InstanceName == FName(TEXT("RPGBossDeath")))
```

## 37. Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp

old line527:
```cpp
TestTrue(TEXT("the callbacks exist (built, never run)"), static_cast<bool>(BossPlan.Plans[0].Configure) && static_cast<bool>(BossPlan.Plans[1].Configure) && static_cast<bool>(BossPlan.Plans[2].Configure)
		&& static_cast<bool>(BossPlan.Plans[3].Configure) && static_cast<bool>(BossPlan.Plans[4].Configure))
```

new line542:
```cpp
TestTrue(TEXT("the callbacks exist (built, never run)"), static_cast<bool>(BossPlan.Plans[0].Configure) && static_cast<bool>(BossPlan.Plans[1].Configure) && static_cast<bool>(BossPlan.Plans[2].Configure)
		&& static_cast<bool>(BossPlan.Plans[3].Configure) && static_cast<bool>(BossPlan.Plans[4].Configure) && static_cast<bool>(BossPlan.Plans[5].Configure) && static_cast<bool>(BossPlan.Plans[6].Configure) && static_cast<bool>(BossPlan.Plans[7].Configure) && static_cast<bool>(BossPlan.Plans[8].Configure) && static_cast<bool>(BossPlan.Plans[9].Configure) && static_cast<bool>(BossPlan.Plans[10].Configure) && static_cast<bool>(BossPlan.Plans[11].Configure))
```

## 38. Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp

old line535:
```cpp
TestEqual(TEXT("the union of required manifest paths is fifty-one"), Required.Num(), 51)
```

new line550:
```cpp
TestEqual(TEXT("the union of required manifest paths is one hundred ten"), Required.Num(), 110)
```

## 39. Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp

old line540:
```cpp
TestEqual(TEXT("one class lease per boss plan"), BossPlan.ClassLeases.Num(), 5)
```

new line555:
```cpp
TestEqual(TEXT("one class lease per boss plan"), BossPlan.ClassLeases.Num(), 12)
```

## 40. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line613:
```cpp
TestTrue(FString::Printf(TEXT("%s: every owned component is destroyed (none resolves any more)"), Label), Weak.Num() == 10 && bGone)
```

new line629:
```cpp
TestTrue(FString::Printf(TEXT("%s: every owned component is destroyed (none resolves any more)"), Label), Weak.Num() == 24 && bGone)
```

## 41. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line648:
```cpp
TestEqual(TEXT("ten components are leased"), Batch.GetOwnedComponentCount(), 10)
```

new line664:
```cpp
TestEqual(TEXT("twenty-four components are leased"), Batch.GetOwnedComponentCount(), 24)
```

## 42. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line651:
```cpp
TestTrue(TEXT("ten distinct owned component pointers"), OwnedList.Num() == 10 && OwnedSet.Num() == 10)
```

new line667:
```cpp
TestTrue(TEXT("twenty-four distinct owned component pointers"), OwnedList.Num() == 24 && OwnedSet.Num() == 24)
```

## 43. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line687:
```cpp
TestTrue(FString::Printf(TEXT("%s: exactly five components were added, every unrelated component is still there and the mesh asset is unchanged"), *Label), bPriorKept)
```

new line703:
```cpp
TestTrue(FString::Printf(TEXT("%s: exactly twelve components were added, every unrelated component is still there and the mesh asset is unchanged"), *Label), bPriorKept)
```

## 44. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line706:
```cpp
TestTrue(TEXT("summary: slots, targets, roles, explicit phase ids and owned counts"),
				Infos[0].Slot == FName(TEXT("BossOne")) && Infos[0].TargetSlot == FName(TEXT("Player")) && Infos[0].Role == ERPGPreflightRole::BossCore && Infos[0].SelectedPhaseId == FName(One.Phase) && Infos[0].OwnedComponentCount == 5
				&& Infos[1].Slot == FName(TEXT("BossTwo")) && Infos[1].TargetSlot == FName(TEXT("Player")) && Infos[1].Role == ERPGPreflightRole::BossCore && Infos[1].SelectedPhaseId == FName(Two.Phase) && Infos[1].OwnedComponentCount == 5
				&& Infos[2].Slot == FName(TEXT("Player")) && Infos[2].TargetSlot == FName(TEXT("BossOne")) && Infos[2].Role == ERPGPreflightRole::TargetOnly && Infos[2].SelectedPhaseId.IsNone() && Infos[2].OwnedComponentCount == 0)
```

new line722:
```cpp
TestTrue(TEXT("summary: slots, targets, roles, explicit phase ids and owned counts"),
				Infos[0].Slot == FName(TEXT("BossOne")) && Infos[0].TargetSlot == FName(TEXT("Player")) && Infos[0].Role == ERPGPreflightRole::BossCore && Infos[0].SelectedPhaseId == FName(One.Phase) && Infos[0].OwnedComponentCount == 12
				&& Infos[1].Slot == FName(TEXT("BossTwo")) && Infos[1].TargetSlot == FName(TEXT("Player")) && Infos[1].Role == ERPGPreflightRole::BossCore && Infos[1].SelectedPhaseId == FName(Two.Phase) && Infos[1].OwnedComponentCount == 12
				&& Infos[2].Slot == FName(TEXT("Player")) && Infos[2].TargetSlot == FName(TEXT("BossOne")) && Infos[2].Role == ERPGPreflightRole::TargetOnly && Infos[2].SelectedPhaseId.IsNone() && Infos[2].OwnedComponentCount == 0)
```

## 45. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line788:
```cpp
TestTrue(TEXT("explicit abort destroyed ten components, found none already gone and no contract violation"), Report.Destroyed == 10 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && !Report.bRefused)
```

new line804:
```cpp
TestTrue(TEXT("explicit abort destroyed twenty-four components, found none already gone and no contract violation"), Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && !Report.bRefused)
```

## 46. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line899:
```cpp
TestTrue(FString::Printf(TEXT("control: abort is clean and destroyed ten components (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 10 && Report.AlreadyGone == 0 && Report.ContractViolations == 0)
```

new line915:
```cpp
TestTrue(FString::Printf(TEXT("control: abort is clean and destroyed twenty-four components (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0)
```

## 47. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line984:
```cpp
TestTrue(TEXT("all five of boss one's components (earlier owner) were allocated and are now destroyed"), bBossOneAllocatedAndDestroyed)
```

new line1000:
```cpp
TestTrue(TEXT("all twelve of boss one's components (earlier owner) were allocated and are now destroyed"), bBossOneAllocatedAndDestroyed)
```

## 48. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line993:
```cpp
TestTrue(TEXT("boss two's two names after the blocked one were never allocated"), StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actors[1]), FName(Expected[3].Name)) == nullptr
		&& StaticFindObjectFast(UObject::StaticClass(), const_cast<AActor*>(Actors[1]), FName(Expected[4].Name)) == nullptr)
```

new line1014:
```cpp
TestTrue(TEXT("all nine names after the blocked third component were never allocated"), bAllLaterNamesAbsent)
```

## 49. Source/OneBossFight/Tests/RPGBossProductionPreparationTests.cpp

old line1052:
```cpp
TestTrue(FString::Printf(TEXT("the retry's abort is clean and destroyed ten components (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 10 && Report.AlreadyGone == 0 && Report.ContractViolations == 0)
```

new line1072:
```cpp
TestTrue(FString::Printf(TEXT("the retry's abort is clean and destroyed twenty-four components (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0)
```

## 50. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line541:
```cpp
TestTrue(FString::Printf(TEXT("%s: every owned component is destroyed (none resolves any more)"), Label), Weak.Num() == 10 && bGone)
```

new line557:
```cpp
TestTrue(FString::Printf(TEXT("%s: every owned component is destroyed (none resolves any more)"), Label), Weak.Num() == 24 && bGone)
```

## 51. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line557:
```cpp
TestTrue(TEXT("the artifact reports prepared and leases ten components"), Batch.IsPrepared() && Batch.GetOwnedComponentCount() == 10)
```

new line573:
```cpp
TestTrue(TEXT("the artifact reports prepared and leases twenty-four components"), Batch.IsPrepared() && Batch.GetOwnedComponentCount() == 24)
```

## 52. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line560:
```cpp
TestTrue(TEXT("ten distinct owned component pointers"), OwnedList.Num() == 10 && OwnedSet.Num() == 10)
```

new line576:
```cpp
TestTrue(TEXT("twenty-four distinct owned component pointers"), OwnedList.Num() == 24 && OwnedSet.Num() == 24)
```

## 53. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line593:
```cpp
TestTrue(FString::Printf(TEXT("%s: exactly five components were added, every unrelated component is still there, the mesh asset is unchanged and no participant component exists"), *Label), bPriorKept && !Case.Actor->FindComponentByClass<URPGCombatParticipant>())
```

new line609:
```cpp
TestTrue(FString::Printf(TEXT("%s: exactly twelve components were added, every unrelated component is still there, the mesh asset is unchanged and no participant component exists"), *Label), bPriorKept && !Case.Actor->FindComponentByClass<URPGCombatParticipant>())
```

## 54. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line618:
```cpp
TestTrue(TEXT("summaries: three participants, ten components, the explicit phase ids"), Infos.Num() == 3 && Infos[0].OwnedComponentCount == 5 && Infos[1].OwnedComponentCount == 5 && Infos[2].OwnedComponentCount == 0
			&& Infos[0].SelectedPhaseId == FName(One.Phase) && Infos[1].SelectedPhaseId == FName(Two.Phase) && Infos[2].SelectedPhaseId.IsNone())
```

new line634:
```cpp
TestTrue(TEXT("summaries: three participants, twenty-four components, the explicit phase ids"), Infos.Num() == 3 && Infos[0].OwnedComponentCount == 12 && Infos[1].OwnedComponentCount == 12 && Infos[2].OwnedComponentCount == 0
			&& Infos[0].SelectedPhaseId == FName(One.Phase) && Infos[1].SelectedPhaseId == FName(Two.Phase) && Infos[2].SelectedPhaseId.IsNone())
```

## 55. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line652:
```cpp
TestTrue(TEXT("and its abort is clean, ten destroyed"), Report.IsClean() && Report.Destroyed == 10 && Report.ContractViolations == 0)
```

new line668:
```cpp
TestTrue(TEXT("and its abort is clean, twenty-four destroyed"), Report.IsClean() && Report.Destroyed == 24 && Report.ContractViolations == 0)
```

## 56. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line668:
```cpp
TestTrue(FString::Printf(TEXT("explicit abort: clean report and ten destroyed (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 10 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && !Report.bRefused)
```

new line684:
```cpp
TestTrue(FString::Printf(TEXT("explicit abort: clean report and twenty-four destroyed (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsClean() && Report.Destroyed == 24 && Report.AlreadyGone == 0 && Report.ContractViolations == 0 && !Report.bRefused)
```

## 57. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line774:
```cpp
TestTrue(TEXT("name collision: boss one's five and boss two's two earlier components were allocated and are now destroyed"), bBossOneDestroyed && bBossTwoEarlierDestroyed)
```

new line790:
```cpp
TestTrue(TEXT("name collision: boss one's twelve and boss two's two earlier components were allocated and are now destroyed"), bBossOneDestroyed && bBossTwoEarlierDestroyed)
```

## 58. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line775:
```cpp
TestTrue(TEXT("name collision: the blocked name is still the very blocker, live; boss two's later two names were never allocated; the target got none"),
		StaticFindObjectFast(UObject::StaticClass(), F.BossTwoActor, FName(Expected[2].Name)) == Blocker && IsValid(Blocker) && StaticFindObjectFast(UObject::StaticClass(), F.BossTwoActor, FName(Expected[3].Name)) == nullptr
		&& StaticFindObjectFast(UObject::StaticClass(), F.BossTwoActor, FName(Expected[4].Name)) == nullptr && StaticFindObjectFast(UObject::StaticClass(), F.TargetActor, FName(Expected[0].Name)) == nullptr)
```

new line796:
```cpp
TestTrue(TEXT("name collision: blocked name keeps identity; all nine later names absent; target gets none"),
		StaticFindObjectFast(UObject::StaticClass(), F.BossTwoActor, FName(Expected[2].Name)) == Blocker && IsValid(Blocker) && bAllLaterNamesAbsent
		&& StaticFindObjectFast(UObject::StaticClass(), F.TargetActor, FName(Expected[0].Name)) == nullptr)
```

## 59. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line806:
```cpp
TestTrue(TEXT("the retry's abort is clean and destroyed ten"), Report.IsClean() && Report.Destroyed == 10 && Report.ContractViolations == 0)
```

new line827:
```cpp
TestTrue(TEXT("the retry's abort is clean and destroyed twenty-four"), Report.IsClean() && Report.Destroyed == 24 && Report.ContractViolations == 0)
```

## 60. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line848:
```cpp
TestTrue(TEXT("second preparation: the first artifact is undamaged: still prepared, ten components, the very same objects, unregistered, and every actor is exactly as with the first"),
			First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 10 && SameWorld(WithFirst, F.Capture()))
```

new line869:
```cpp
TestTrue(TEXT("second preparation: the first artifact is undamaged: still prepared, twenty-four components, the very same objects, unregistered, and every actor is exactly as with the first"),
			First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 24 && SameWorld(WithFirst, F.Capture()))
```

## 61. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line855:
```cpp
TestTrue(TEXT("second preparation: every component of the first artifact is still the same live unregistered object"), FirstWeak.Num() == 10 && bAllLive)
```

new line876:
```cpp
TestTrue(TEXT("second preparation: every component of the first artifact is still the same live unregistered object"), FirstWeak.Num() == 24 && bAllLive)
```

## 62. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line861:
```cpp
TestTrue(TEXT("the same binding again: the first artifact is still undamaged"), First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 10 && SameWorld(WithFirst, F.Capture()))
```

new line882:
```cpp
TestTrue(TEXT("the same binding again: the first artifact is still undamaged"), First.Batch->IsPrepared() && First.Batch->GetOwnedComponentCount() == 24 && SameWorld(WithFirst, F.Capture()))
```

## 63. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line865:
```cpp
TestTrue(TEXT("the first artifact's abort is clean and destroyed ten"), Report.IsClean() && Report.Destroyed == 10 && Report.ContractViolations == 0)
```

new line886:
```cpp
TestTrue(TEXT("the first artifact's abort is clean and destroyed twenty-four"), Report.IsClean() && Report.Destroyed == 24 && Report.ContractViolations == 0)
```

## 64. Source/OneBossFight/Tests/RPGBossWorldPreparationTests.cpp

old line926:
```cpp
TestTrue(FString::Printf(TEXT("control: the unmodified call succeeds after the refusals (errors: %s)"), *JoinErrors(Control.Errors)), Control.Succeeded() && Control.Batch->GetOwnedComponentCount() == 10)
```

new line947:
```cpp
TestTrue(FString::Printf(TEXT("control: the unmodified call succeeds after the refusals (errors: %s)"), *JoinErrors(Control.Errors)), Control.Succeeded() && Control.Batch->GetOwnedComponentCount() == 24)
```

## 65. Source/OneBossFight/Tests/RPGBossPreparationRegistryTests.cpp

old line620:
```cpp
TestTrue(TEXT("both encounters hold ten unregistered components each (five per boss, none on the target) and the unrelated markers are untouched"), IsFullyPrepared(*A) && IsFullyPrepared(*B) && MarkersIntact(*A) && MarkersIntact(*B))
```

new line636:
```cpp
TestTrue(TEXT("both encounters hold twenty-four unregistered components each (twelve per boss, none on the target) and the unrelated markers are untouched"), IsFullyPrepared(*A) && IsFullyPrepared(*B) && MarkersIntact(*A) && MarkersIntact(*B))
```

## 66. Source/OneBossFight/Tests/RPGBossPreparationRegistryTests.cpp

old line794:
```cpp
TestTrue(FString::Printf(TEXT("clean release: Released, ten destroyed, no violation (errors: %s)"), *JoinErrors(Released.Errors)), Released.IsReleased() && Released.Abort.IsClean() && Released.Abort.Destroyed == 10 && Released.Abort.ContractViolations == 0)
```

new line810:
```cpp
TestTrue(FString::Printf(TEXT("clean release: Released, twenty-four destroyed, no violation (errors: %s)"), *JoinErrors(Released.Errors)), Released.IsReleased() && Released.Abort.IsClean() && Released.Abort.Destroyed == 24 && Released.Abort.ContractViolations == 0)
```

## 67. Source/OneBossFight/Tests/RPGBossPreparationRegistryTests.cpp

old line856:
```cpp
TestTrue(FString::Printf(TEXT("the token releases through its own registry: Released, ten destroyed (errors: %s)"), *JoinErrors(ByOwnToken.Errors)), ByOwnToken.IsReleased() && ByOwnToken.Abort.Destroyed == 10 && !TokenTwo.IsHeld())
```

new line872:
```cpp
TestTrue(FString::Printf(TEXT("the token releases through its own registry: Released, twenty-four destroyed (errors: %s)"), *JoinErrors(ByOwnToken.Errors)), ByOwnToken.IsReleased() && ByOwnToken.Abort.Destroyed == 24 && !TokenTwo.IsHeld())
```

## 68. Source/OneBossFight/Tests/RPGBossPreparationRegistryTests.cpp

old line894:
```cpp
TestTrue(FString::Printf(TEXT("world dies first: the release is clean without a crash, every owned component accounted for (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsReleased() && Report.Abort.Destroyed + Report.Abort.AlreadyGone == 10 && Report.Abort.ContractViolations == 0)
```

new line910:
```cpp
TestTrue(FString::Printf(TEXT("world dies first: the release is clean without a crash, every owned component accounted for (errors: %s)"), *JoinErrors(Report.Errors)), Report.IsReleased() && Report.Abort.Destroyed + Report.Abort.AlreadyGone == 24 && Report.Abort.ContractViolations == 0)
```

## 69. Source/OneBossFight/Tests/RPGBossPreparationRegistryTests.cpp

old line986:
```cpp
TestTrue(FString::Printf(TEXT("actors die first: the release is clean, every component was destroyed with its owner (ten already gone, none destroyed by the abort), no violation (errors: %s)"), *JoinErrors(Report.Errors)),
			Report.IsReleased() && Report.Abort.AlreadyGone == 10 && Report.Abort.Destroyed == 0 && Report.Abort.ContractViolations == 0 && Registry.GetActiveReservationCount() == 0 && !Token.IsHeld())
```

new line1002:
```cpp
TestTrue(FString::Printf(TEXT("actors die first: the release is clean, every component was destroyed with its owner (twenty-four already gone, none destroyed by the abort), no violation (errors: %s)"), *JoinErrors(Report.Errors)),
			Report.IsReleased() && Report.Abort.AlreadyGone == 24 && Report.Abort.Destroyed == 0 && Report.Abort.ContractViolations == 0 && Registry.GetActiveReservationCount() == 0 && !Token.IsHeld())
```

## 70. Source/OneBossFight/Tests/RPGBossPreparationRegistryTests.cpp

old line1026:
```cpp
TestTrue(TEXT("after the off-thread refusals the token is still held, the reservation and its ten components are intact and the registry is unchanged"), Token.IsHeld() && IsFullyPrepared(*D) && Registry.GetActiveReservationCount() == 1
			&& Registry.GetReservedEncounters() == TArray<FGuid>{D->Encounter})
```

new line1042:
```cpp
TestTrue(TEXT("after the off-thread refusals the token is still held, the reservation and its twenty-four components are intact and the registry is unchanged"), Token.IsHeld() && IsFullyPrepared(*D) && Registry.GetActiveReservationCount() == 1
			&& Registry.GetReservedEncounters() == TArray<FGuid>{D->Encounter})
```

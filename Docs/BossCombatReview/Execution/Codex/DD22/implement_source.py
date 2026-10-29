"""Write the C265 typed HealPunish package only; no engine/build/test actions."""
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[4]
player=root/"Source/OneBossFight/Player"
testdir=root/"Source/OneBossFight/Tests"
fields=[("bool","bEnabled","true"),("float","MinRange","400.f"),("float","MaxRange","1000.f"),
("float","Cooldown","4.f"),("float","Damage","12.f"),("float","FlightTime","1.2f"),
("float","MinSpeed","450.f"),("float","MaxSpeed","2500.f"),("float","JavelinRadius","25.f"),
("float","JavelinMaxRange","3000.f"),("TArray<FName>","SpawnSockets",'{TEXT("JavelinSpawn"),TEXT("hand_l")}'),
("float","AimHeight","100.f"),("bool","bRespondToHeal","true"),("bool","bCancelJavelinsOnInterrupt","true")]
floats=[n for typ,n,d in fields if typ=="float"]
paths="\n".join(f'\tinline constexpr const TCHAR* Field{n}=TEXT("HealPunish.{n}");' for typ,n,d in fields)
header=r'''// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * C265 UNWIRED authored HealPunish record:14 public fields only, no runtime state.
 * All TEN floats finite first in native header order. Domain order:
 * MinRange>=0/cap; MaxRange>0/cap/>MinRange; Cooldown>=0/cap; Damage>=0(no cap);
 * FlightTime>=0.05/cap; MinSpeed>0/cap; MaxSpeed>0/cap then MinSpeed<=MaxSpeed;
 * JavelinRadius>0/cap; JavelinMaxRange>0/cap; nonempty SpawnSockets with each name
 * not None/no whitespace/control; finally AimHeight in[-cap,cap]. Bool values any.
 * These are AUTHORED RECORD CONTRACTS, not native guards or balance approval.
 * Editor minimum1 is not imposed;0.05 flight floor is an explicit authored choice.
 * Empty socket list is refused instead of silently invoking native fallback.
 * No ASCII regex, uniqueness rule, bone/socket existence or class check is invented.
 *
 * MaxAuthoredMagnitude=1e6 screens float-extreme values, not actual arena tuning.
 * Signed AimHeight is legal. Damage is a finite nonnegative health payload, not
 * trajectory geometry; it has no ceiling. Native world/time/trajectory inputs
 * remain separate: no unrestricted runtime arithmetic or gameplay proof.
 *
 * Move A5 and the player potion montage are HARDCODED in native cpp and UNRESOLVED
 * by this record. No move/ability/timing/socket resolution is claimed.
 * Exact class/live/not registered/not begun and valid not-begun owner precede
 * whole-record validation, then all14 fields are copied (array by value).
 * No pending/cooldown/counter/generation, DrinkMontage/Flying or tick flag is
 * assigned. No load, create, register, BeginPlay, Tick, heal notification, release,
 * launch, report or CancelAll operation. ComponentBegunPlay stays source-only.
 * Plan stays outside preflight/preparation/reservations: no Ready/legacy suppression.
 */
namespace RPGBossHealPunishAdapters
{
	inline constexpr float MaxAuthoredMagnitude=1.0e6f;
	inline constexpr float MinAuthoredFlightTime=0.05f;
'''
header+=paths+r'''
	ONEBOSSFIGHT_API bool ValidateHealPunish(const FRPGHealPunishConfig& Record,FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureHealPunish(UActorComponent& Component,const FRPGParticipantConfig& Config,FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeHealPunishPlan();
}
'''
(player/"RPGBossHealPunishAdapters.h").write_text(header,encoding="utf-8")
common=(player/"RPGBossLowSweepAdapters.cpp").read_text(encoding="utf-8").replace("LowSweep","HealPunish")
begin=common.index("\tbool ValidateHealPunish(");end=common.index("\n\tbool ConfigureHealPunish(",begin)
checks=[]
def reject(expr,token,field):
    checks.append(f'\t\tif ({expr}) {{ return Refuse(OutError,TEXT("InvalidPunish.{token}"),Field{field}); }}')
for n in ["MinRange","MaxRange","Cooldown","Damage","FlightTime","MinSpeed","MaxSpeed","JavelinRadius","JavelinMaxRange"]:
    if n in ["MinRange","Cooldown","Damage"]: reject(f"Record.{n}<0.f","Negative",n)
    elif n=="FlightTime": reject("Record.FlightTime<MinAuthoredFlightTime","BelowFlightTimeFloor",n)
    else: reject(f"Record.{n}<=0.f","NotPositive",n)
    if n!="Damage": reject(f"Record.{n}>MaxAuthoredMagnitude","AboveCeiling",n)
    if n=="MaxRange": reject("Record.MaxRange<=Record.MinRange","MaxNotAboveMin",n)
    if n=="MaxSpeed": reject("Record.MinSpeed>Record.MaxSpeed","MinSpeedAboveMax","MinSpeed")
scalarlist=",".join("{Field"+n+",Record."+n+"}" for n in floats)
validator=r'''
	bool ValidateHealPunish(const FRPGHealPunishConfig& Record,FString& OutError)
	{
		OutError.Reset();
		struct FScalar { const TCHAR* Field; float Value; };
		const FScalar Scalars[] = {SCALARS};
		for (const FScalar& S : Scalars)
		{
			if (!FMath::IsFinite(S.Value)) { return Refuse(OutError,TEXT("InvalidPunish.NotFinite"),S.Field); }
		}
CHECKS
		if (Record.SpawnSockets.IsEmpty()) { return Refuse(OutError,TEXT("InvalidDependency.Missing"),FieldSpawnSockets); }
		for (int32 Index=0;Index<Record.SpawnSockets.Num();++Index)
		{
			const FName Name=Record.SpawnSockets[Index];
			bool bInvalid=Name.IsNone();
			for (const TCHAR C : Name.ToString()) { bInvalid=bInvalid||FChar::IsWhitespace(C)||FChar::IsControl(C); }
			if (bInvalid)
			{
				OutError=FString::Printf(TEXT("InvalidDependency.Malformed: %s[%d]"),FieldSpawnSockets,Index);
				return false;
			}
		}
		if (Record.AimHeight < -MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidPunish.BelowFloor"),FieldAimHeight); }
		if (Record.AimHeight > MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidPunish.AboveCeiling"),FieldAimHeight); }
		return true;
	}
'''.replace("SCALARS",scalarlist).replace("CHECKS","\n".join(checks))
cpp=common[:begin]+validator
cpp+=r'''
	bool ConfigureHealPunish(UActorComponent& Component,const FRPGParticipantConfig& Config,FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component,OutError)||!ValidateHealPunish(Config.HealPunish,OutError)) { return false; }
		URPGBossHealPunish* Punish=CastChecked<URPGBossHealPunish>(&Component);
		const FRPGHealPunishConfig& Record=Config.HealPunish;
'''
cpp+="\n".join(f"\t\tPunish->{n}=Record.{n};" for typ,n,d in fields)
cpp+=r'''
		return true;
	}
	FRPGComponentPlan MakeHealPunishPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class=URPGBossHealPunish::StaticClass(); Plan.InstanceName=TEXT("RPGBossHealPunish");
'''
cpp+="\t\tPlan.RequiredFields={"+",".join("Field"+n for typ,n,d in fields)+"};\n"
cpp+=r'''		Plan.Configure=&ConfigureHealPunish; return Plan;
	}
}
'''
(player/"RPGBossHealPunishAdapters.cpp").write_text(cpp,encoding="utf-8")
h=player/"RPGEncounterBinding.h";text=h.read_text(encoding="utf-8")
assert "struct FRPGHealPunishConfig" not in text
record="\n/** C265 authored HealPunish profile; not tracker/ability/socket resolution or runtime state. */\nUSTRUCT(BlueprintType)\nstruct FRPGHealPunishConfig\n{\n\tGENERATED_BODY()\n"
record+="\n".join(f"\tUPROPERTY(EditAnywhere) {typ} {n}={d};" for typ,n,d in fields)+"\n};\n\n"
text=text.replace("USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig",record+"USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig",1)
text=text.replace("UPROPERTY(EditAnywhere) FRPGShockwaveConfig Shockwave;","UPROPERTY(EditAnywhere) FRPGShockwaveConfig Shockwave;\n\tUPROPERTY(EditAnywhere) FRPGHealPunishConfig HealPunish;")
text=text.replace("\tFRPGShockwaveConfig Shockwave;","\tFRPGShockwaveConfig Shockwave;\n\tFRPGHealPunishConfig HealPunish;")
h.write_text(text,encoding="utf-8")
p=player/"RPGEncounterBinding.cpp";text=p.read_text(encoding="utf-8")
text=text.replace('#include "Player/RPGBossShockwaveAdapters.h"','#include "Player/RPGBossShockwaveAdapters.h"\n#include "Player/RPGBossHealPunishAdapters.h"')
text=text.replace("\tTSet<FName> PhaseIds;",'\tFString PunishError;\n\tif (!RPGBossHealPunishAdapters::ValidateHealPunish(D.HealPunish,PunishError)) { Result.Fail(PunishError); } // C265 authored structure; no move/socket resolution\n\tTSet<FName> PhaseIds;',1)
text=text.replace("\tValue->Shockwave = D.Shockwave;","\tValue->Shockwave = D.Shockwave;\n\tValue->HealPunish = D.HealPunish;")
p.write_text(text,encoding="utf-8")
print("DD22 adapter/record/compiler source written; no build or engine operation.")

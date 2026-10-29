"""Generate the exact DD21 source package, reusing only existing fixture plumbing."""
from pathlib import Path
import re
here=Path(__file__).resolve().parent
root=here.parents[4]
player=root/"Source/OneBossFight/Player"
tests=root/"Source/OneBossFight/Tests"
def transform(text):
    text=text.replace("LowSweep","Shockwave")
    for old,new in [("Reach","StartRadius"),("InnerRadius","MaxRadius"),("BladeHeight","Speed"),("SweepFromDegrees","Thickness"),("SweepToDegrees","JumpClearance")]:
        # Includes field constants as well as standalone native property names.
        text=text.replace(old,new)
    return text
cpp=transform((player/"RPGBossLowSweepAdapters.cpp").read_text(encoding="utf-8"))
begin=cpp.index("\tbool ValidateShockwave(")
end=cpp.index("\n\tbool ConfigureShockwave(",begin)
validator=r'''
	bool ValidateShockwave(const FRPGShockwaveConfig& Record, FString& OutError)
	{
		OutError.Reset();
		struct FScalar { const TCHAR* Field; float Value; };
		const FScalar Scalars[] = {{FieldDamage,Record.Damage},{FieldStartRadius,Record.StartRadius},
			{FieldMaxRadius,Record.MaxRadius},{FieldSpeed,Record.Speed},{FieldThickness,Record.Thickness},{FieldJumpClearance,Record.JumpClearance}};
		for (const FScalar& S : Scalars)
		{
			if (!FMath::IsFinite(S.Value)) { return Refuse(OutError,TEXT("InvalidShockwave.NotFinite"),S.Field); }
		}
		if (Record.Damage<0.f) { return Refuse(OutError,TEXT("InvalidShockwave.Negative"),FieldDamage); }
		if (Record.StartRadius<0.f) { return Refuse(OutError,TEXT("InvalidShockwave.Negative"),FieldStartRadius); }
		if (Record.StartRadius>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldStartRadius); }
		if (Record.MaxRadius<=0.f) { return Refuse(OutError,TEXT("InvalidShockwave.NotPositive"),FieldMaxRadius); }
		if (Record.MaxRadius>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldMaxRadius); }
		if (Record.MaxRadius<=Record.StartRadius) { return Refuse(OutError,TEXT("InvalidShockwave.MaxNotAboveStart"),FieldMaxRadius); }
		if (Record.Speed<=0.f) { return Refuse(OutError,TEXT("InvalidShockwave.NotPositive"),FieldSpeed); }
		if (Record.Speed>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldSpeed); }
		if (Record.Thickness<=0.f) { return Refuse(OutError,TEXT("InvalidShockwave.NotPositive"),FieldThickness); }
		if (Record.Thickness>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldThickness); }
		if (Record.JumpClearance<=0.f) { return Refuse(OutError,TEXT("InvalidShockwave.NotPositive"),FieldJumpClearance); }
		if (Record.JumpClearance>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldJumpClearance); }
		if (Record.MoveId.IsNone()) { return Refuse(OutError,TEXT("InvalidDependency.Missing"),FieldMoveId); }
		for (const TCHAR C : Record.MoveId.ToString())
		{
			if (FChar::IsWhitespace(C)||FChar::IsControl(C)) { return Refuse(OutError,TEXT("InvalidDependency.Malformed"),FieldMoveId); }
		}
		return true;
	}
'''
cpp=cpp[:begin]+validator+cpp[end:]
(player/"RPGBossShockwaveAdapters.cpp").write_text(cpp,encoding="utf-8")
t=transform((tests/"RPGBossLowSweepAdaptersTests.cpp").read_text(encoding="utf-8"))
t=t.replace("#include <limits>","#include <limits>\n#include <cmath>")
t=t.replace("IsBladeActive","IsWaveActive").replace("GetBladeAngle","GetRadius").replace("GetSweepCount","GetLaunchCount").replace("GetBlockedCount","GetCentralPriorityCount")
begin=t.index("\tFRPGShockwaveConfig RecordA()")
end=t.index("\n\tFRPGParticipantConfig Config(",begin)
t=t[:begin]+r'''
	FRPGShockwaveConfig RecordA()
	{
		FRPGShockwaveConfig R;
		R.bEnabled=false; R.MoveId=TEXT("UnresolvedWaveIdentity");
		R.Damage=0.f; R.StartRadius=0.f; R.MaxRadius=0.5f; R.Speed=0.25f; R.Thickness=0.125f; R.JumpClearance=0.5f;
		return R;
	}
	FRPGShockwaveConfig RecordB()
	{
		FRPGShockwaveConfig R;
		R.bEnabled=true; R.MoveId=TEXT("AnotherWaveIdentity");
		R.Damage=53.25f; R.StartRadius=17.5f; R.MaxRadius=1111.f; R.Speed=876.f; R.Thickness=7.25f; R.JumpClearance=2.5f;
		return R;
	}
'''+t[end:]
begin=t.index('\t\tCases.Add({TEXT("negative damage")')
end=t.index("\n\t\treturn Cases;",begin)
rows=[
("negative damage","R.Damage=-1.f","Negative","Damage"),
("negative start","R.StartRadius=-0.25f","Negative","StartRadius"),
("zero max","R.MaxRadius=0.f","NotPositive","MaxRadius"),
("negative max","R.MaxRadius=-1.f","NotPositive","MaxRadius"),
("max equal start","R.StartRadius=1.f; R.MaxRadius=1.f","MaxNotAboveStart","MaxRadius"),
("max below start","R.StartRadius=2.f; R.MaxRadius=1.f","MaxNotAboveStart","MaxRadius")]
for f in ["Speed","Thickness","JumpClearance"]:
    rows += [(f+" zero",f"R.{f}=0.f","NotPositive",f),(f+" negative",f"R.{f}=-0.25f","NotPositive",f)]
for f in ["StartRadius","MaxRadius","Speed","Thickness","JumpClearance"]:
    rows.append((f+" next float above ceiling",f"R.{f}=std::nextafter(RPGBossShockwaveAdapters::MaxAuthoredMagnitude,std::numeric_limits<float>::infinity())","AboveCeiling",f))
rows += [("X301 radius overflow inputs","R.StartRadius=3.36879526214505e38f; R.MaxRadius=std::numeric_limits<float>::max(); R.Speed=3.36879526214505e38f; R.Thickness=1.f","AboveCeiling","StartRadius"),
("X301 band overflow inputs","R.StartRadius=2.5521175490829424e38f; R.MaxRadius=std::numeric_limits<float>::max(); R.Speed=1.f; R.Thickness=std::numeric_limits<float>::max()","AboveCeiling","StartRadius")]
bad="\n".join(f'\t\tCases.Add({{TEXT("{n}"), [](FRPGShockwaveConfig& R) {{ {body}; }}, TEXT("InvalidShockwave.{token}"), RPGBossShockwaveAdapters::Field{field}}});' for n,body,token,field in rows)
bad+=r'''
		Cases.Add({TEXT("None move"), [](FRPGShockwaveConfig& R) { R.MoveId=NAME_None; }, TEXT("InvalidDependency.Missing"), RPGBossShockwaveAdapters::FieldMoveId});
		Cases.Add({TEXT("space move"), [](FRPGShockwaveConfig& R) { R.MoveId=TEXT("Wave Id"); }, TEXT("InvalidDependency.Malformed"), RPGBossShockwaveAdapters::FieldMoveId});
		Cases.Add({TEXT("tab move"), [](FRPGShockwaveConfig& R) { R.MoveId=TEXT("Wave\tId"); }, TEXT("InvalidDependency.Malformed"), RPGBossShockwaveAdapters::FieldMoveId});
		Cases.Add({TEXT("control move"), [](FRPGShockwaveConfig& R) { R.MoveId=FName(*FString::Printf(TEXT("Wave%cId"),static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), RPGBossShockwaveAdapters::FieldMoveId});
'''
t=t[:begin]+bad+t[end:]
begin=t.index("\tTArray<FRPGShockwaveConfig> Valid")
end=t.index("\n\treturn true;\n}",begin)
t=t[:begin]+r'''
	TArray<FRPGShockwaveConfig> Valid{RecordA(),RecordB(),FRPGShockwaveConfig()};
	const float Ceiling=RPGBossShockwaveAdapters::MaxAuthoredMagnitude;
	auto Pair=RecordB(); Pair.StartRadius=std::nextafter(Ceiling,0.f); Pair.MaxRadius=Ceiling; Valid.Add(Pair);
	auto Max=RecordA(); Max.MaxRadius=Ceiling; Valid.Add(Max);
	auto Fast=RecordA(); Fast.Speed=Ceiling; Valid.Add(Fast);
	auto Wide=RecordA(); Wide.Thickness=Ceiling; Valid.Add(Wide);
	auto High=RecordA(); High.JumpClearance=Ceiling; Valid.Add(High);
	auto Damage=RecordA(); Damage.Damage=std::numeric_limits<float>::max(); Valid.Add(Damage); // finite health-damage payload, not wave arithmetic
	for (const auto& R : Valid)
	{
		FString E=TEXT("stale");
		TestTrue(TEXT("valid sub-1/zero/inclusive-ceiling/Damage-FLT_MAX record validates and assigns"),
			RPGBossShockwaveAdapters::ValidateShockwave(R,E)&&E.IsEmpty()
			&&RPGBossShockwaveAdapters::ConfigureShockwave(*Sweep,Config(R),E)&&Same(Read(*Sweep),R)&&Runtime.SameAs(FRuntime(*Sweep)));
	}
	auto CheckFirst=[this](const FRPGShockwaveConfig& R,const TCHAR* Token,const TCHAR* Path)
	{
		FString E; RPGBossShockwaveAdapters::ValidateShockwave(R,E);
		TestTrue(TEXT("validation precedence"),E.StartsWith(Token)&&E.Contains(Path));
	};
	auto R=RecordB(); R.Damage=-1.f; R.JumpClearance=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidShockwave.NotFinite"),RPGBossShockwaveAdapters::FieldJumpClearance);
	R=RecordB(); R.StartRadius=std::numeric_limits<float>::infinity(); R.Speed=std::numeric_limits<float>::quiet_NaN();
	CheckFirst(R,TEXT("InvalidShockwave.NotFinite"),RPGBossShockwaveAdapters::FieldStartRadius);
	R=RecordB(); R.StartRadius=Ceiling; R.MaxRadius=Ceiling;
	CheckFirst(R,TEXT("InvalidShockwave.MaxNotAboveStart"),RPGBossShockwaveAdapters::FieldMaxRadius); // inclusive Start ceiling itself passes, but no legal greater Max exists
	R=RecordB(); R.MaxRadius=Ceiling*2.f; R.Speed=0.f;
	CheckFirst(R,TEXT("InvalidShockwave.AboveCeiling"),RPGBossShockwaveAdapters::FieldMaxRadius);
	R=RecordB(); R.JumpClearance=0.f; R.MoveId=NAME_None;
	CheckFirst(R,TEXT("InvalidShockwave.NotPositive"),RPGBossShockwaveAdapters::FieldJumpClearance);
'''+t[end:]
# Replace the inherited explicit native-default assertion and runtime-absence names.
begin=t.index('\tTestTrue(TEXT("explicit native default baseline")')
end=t.index("\n\tauto D = Definition(Default);",begin)
t=t[:begin]+r'''
	TestTrue(TEXT("explicit native default baseline"),Default.bEnabled&&Default.MoveId==FName(TEXT("A6"))
		&&Default.Damage==48.f&&Default.StartRadius==200.f&&Default.MaxRadius==1100.f&&Default.Speed==1000.f&&Default.Thickness==180.f&&Default.JumpClearance==50.f);
'''+t[end:]
t=t.replace('TEXT("bActive"), TEXT("BladeAngle"), TEXT("PreviousAngle"), TEXT("LastInstance"), TEXT("SweepGeneration"), TEXT("SweepCount"), TEXT("HitCount")',
            'TEXT("bActive"), TEXT("bClearedBand"), TEXT("bResolved"), TEXT("Radius"), TEXT("Origin"), TEXT("GroundZ"), TEXT("LaunchGeneration"), TEXT("LaunchCount"), TEXT("HitCount")')
t=t.replace("wrapped angles","wave traversal").replace("StartForTest","LaunchForTest").replace("stationary angular band","wave")
(tests/"RPGBossShockwaveAdaptersTests.cpp").write_text(t,encoding="utf-8")
header=player/"RPGEncounterBinding.h"
h=header.read_text(encoding="utf-8")
assert "struct FRPGShockwaveConfig" not in h
record=r'''
/** C262/C263/C264 authored Shockwave configuration, NOT a resolved tracker move.
 * Defaults match the native declarations; no runtime state or invalid-input fallback. */
USTRUCT(BlueprintType)
struct FRPGShockwaveConfig
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) bool bEnabled=true;
	UPROPERTY(EditAnywhere) FName MoveId=TEXT("A6");
	UPROPERTY(EditAnywhere) float Damage=48.f;
	UPROPERTY(EditAnywhere) float StartRadius=200.f;
	UPROPERTY(EditAnywhere) float MaxRadius=1100.f;
	UPROPERTY(EditAnywhere) float Speed=1000.f;
	UPROPERTY(EditAnywhere) float Thickness=180.f;
	UPROPERTY(EditAnywhere) float JumpClearance=50.f;
};

'''
h=h.replace("USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig",record+"USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig",1)
h=h.replace("UPROPERTY(EditAnywhere) FRPGLowSweepConfig LowSweep;","UPROPERTY(EditAnywhere) FRPGLowSweepConfig LowSweep;\n\tUPROPERTY(EditAnywhere) FRPGShockwaveConfig Shockwave;")
h=h.replace("\tFRPGLowSweepConfig LowSweep;","\tFRPGLowSweepConfig LowSweep;\n\tFRPGShockwaveConfig Shockwave;")
header.write_text(h,encoding="utf-8")
p=player/"RPGEncounterBinding.cpp";c=p.read_text(encoding="utf-8")
c=c.replace('#include "Player/RPGBossLowSweepAdapters.h"','#include "Player/RPGBossLowSweepAdapters.h"\n#include "Player/RPGBossShockwaveAdapters.h"')
anchor="\tTSet<FName> PhaseIds;"
c=c.replace(anchor,'\tFString ShockwaveError;\n\tif (!RPGBossShockwaveAdapters::ValidateShockwave(D.Shockwave,ShockwaveError)) { Result.Fail(ShockwaveError); } // authored record only, no tracker resolution\n'+anchor,1)
c=c.replace("\tValue->LowSweep = D.LowSweep;","\tValue->LowSweep = D.LowSweep;\n\tValue->Shockwave = D.Shockwave;")
p.write_text(c,encoding="utf-8")
print("DD21 source written; not compiled or executed.")

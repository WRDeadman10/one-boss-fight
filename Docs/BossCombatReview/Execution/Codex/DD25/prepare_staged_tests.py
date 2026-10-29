"""C281/C284/C285 Death regression source only, no Unreal execution."""
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[4]
old=(root/'Source/OneBossFight/Tests/RPGBossCloseClipSwapAdaptersTests.cpp').read_text(encoding='utf-8')
fields=['DeathMode','DeathClip','DeathMontage','PackDeathAbilityClassName','PackDeathMontagesName','PackPollSeconds','PackEndTimeMultiplier','HoldAtSeconds','DyingSeconds','BlendInSeconds','MaxClipRestarts','bGuardPackDeath']
floats=['PackPollSeconds','PackEndTimeMultiplier','HoldAtSeconds','DyingSeconds','BlendInSeconds']
def rename(s):return s.replace('CloseClipSwap','Death')
start=rename(old[:old.index('\tFSoftObjectPath MakePath')]).replace('#include "Animation/AnimMontage.h"','#include "Animation/AnimMontage.h"\n#include "Animation/AnimSequence.h"\n#include <limits>\n#include <cmath>')
a=start.index('// STAGING ONLY');b=start.index('namespace',a)
start=start[:a]+'// SOURCE-ONLY, UNRUN. No Death BeginPlay/Tick/Attach, remains, pack ability,\n// preload/load/playback/pose/test-knob call. Plain actor starts before attachment.\n'+start[b:]
block=r'''
	FSoftObjectPath MakePath(const TCHAR* Package, const TCHAR* Asset, const TCHAR* Sub = TEXT(""))
	{
		return FSoftObjectPath(FTopLevelAssetPath(FName(Package), FName(Asset)), FString(Sub));
	}
	TSoftObjectPtr<UAnimSequence> Clip(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UAnimSequence>(Path);
	}
	TSoftObjectPtr<UAnimMontage> Montage(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UAnimMontage>(Path);
	}
	FRPGDeathConfig RecordA()
	{
		FRPGDeathConfig R;
		R.DeathMode = ERPGBossDeathMode::OwnClip;
		R.DeathClip = Clip(MakePath(TEXT("/SyntheticMount/Death/A"), TEXT("ClipA")));
		R.DeathMontage = Montage(MakePath(TEXT("/SyntheticMount/Death/A"), TEXT("MontageA")));
		R.PackDeathAbilityClassName = TEXT("Custom.DeathAbility-A");
		R.PackDeathMontagesName = TEXT("Custom.Montages-A");
		R.PackPollSeconds = 0.125f;
		R.PackEndTimeMultiplier = 0.f;
		R.HoldAtSeconds = 0.25f;
		R.DyingSeconds = 0.5f;
		R.BlendInSeconds = 0.f;
		R.MaxClipRestarts = 0;
		R.bGuardPackDeath = true;
		return R;
	}
	FRPGDeathConfig RecordB()
	{
		FRPGDeathConfig R;
		R.DeathMode = ERPGBossDeathMode::PackMontage;
		R.DeathClip = Clip(MakePath(TEXT("/OtherSynthetic/Death/B"), TEXT("ClipB")));
		R.DeathMontage = Montage(MakePath(TEXT("/OtherSynthetic/Death/B"), TEXT("MontageB")));
		R.PackDeathAbilityClassName = TEXT("CustomDeathAbilityB");
		R.PackDeathMontagesName = TEXT("CustomMontagesB");
		R.PackPollSeconds = 0.5f;
		R.PackEndTimeMultiplier = 0.75f;
		R.HoldAtSeconds = 1.25f;
		R.DyingSeconds = 1.5f;
		R.BlendInSeconds = 0.125f;
		R.MaxClipRestarts = 17;
		R.bGuardPackDeath = false;
		return R;
	}
	FRPGParticipantConfig Config(const FRPGDeathConfig& R)
	{
		FRPGParticipantConfig C;
		C.Death = R;
		return C;
	}
	FRPGDeathConfig Read(const URPGBossDeath& Death)
	{
		FRPGDeathConfig R;
'''
for f in fields:block+='\t\tR.'+f+' = Death.'+f+';\n'
block+='\t\treturn R;\n\t}\n\tbool Same(const FRPGDeathConfig& A, const FRPGDeathConfig& B)\n\t{\n\t\treturn '+ ' && '.join('A.'+f+('.ToSoftObjectPath() == B.'+f+'.ToSoftObjectPath()' if f in ['DeathClip','DeathMontage'] else ' == B.'+f) for f in fields)+';\n\t}\n'
block+=r'''
	struct FRuntime
	{
		bool Active, Held, Registered, Begun, TickRegistered, CanTick;
		double Age;
		FString State, LastPack;
		TArray<int32> Counters;
		explicit FRuntime(const URPGBossDeath& C)
			: Active(C.IsDeathActive()), Held(C.IsPoseHeld()), Registered(C.IsRegistered()), Begun(C.HasBegunPlay()),
			TickRegistered(C.PrimaryComponentTick.IsTickFunctionRegistered()), CanTick(C.PrimaryComponentTick.bCanEverTick),
			Age(C.GetDeathAge()), State(C.GetDeathStateName()), LastPack(C.GetLastPackResult()),
			Counters{C.GetDeathCount(), C.GetClipPlayCount(), C.GetClipRestartCount(), C.GetPoseHoldCount(), C.GetPhysicsOffCount(), C.GetPackSetCount()} {}
		bool SameAs(const FRuntime& O) const
		{
			return Active == O.Active && Held == O.Held && Registered == O.Registered && Begun == O.Begun && TickRegistered == O.TickRegistered
				&& CanTick == O.CanTick && Age == O.Age && State == O.State && LastPack == O.LastPack && Counters == O.Counters;
		}
	};
'''
block+=old[old.index('\tTArray<const UActorComponent*> Owned'):old.index('\tTArray<FString> Paths()')]
block+='\tTArray<FString> Paths()\n\t{\n\t\treturn {'+', '.join('TEXT("Death.'+f+'")' for f in fields)+'};\n\t}\n'
block+='\tstruct FBad\n\t{\n\t\tFString Name;\n\t\tTFunction<void(FRPGDeathConfig&)> Mutate;\n\t\tconst TCHAR* Token;\n\t\tconst TCHAR* Path;\n\t};\n\tTArray<FBad> BadCases()\n\t{\n\t\tTArray<FBad> Cases;\n'
def bad(label,expr,token,field):
    global block
    block+='\t\tCases.Add({TEXT("'+label+'"), [](FRPGDeathConfig& R) { '+expr+'; }, TEXT("'+token+'"), TEXT("Death.'+field+'")});\n'
for f in floats:
    for label,v in [('NaN','std::numeric_limits<float>::quiet_NaN()'),('+Inf','std::numeric_limits<float>::infinity()'),('-Inf','-std::numeric_limits<float>::infinity()')]:bad(f+' '+label,'R.'+f+' = '+v,'InvalidDeath.NotFinite',f)
for value in [2,255]:bad('bad enum '+str(value),'R.DeathMode = static_cast<ERPGBossDeathMode>('+str(value)+')','InvalidDeath.BadMode','DeathMode')
for f in floats:
    positive=f in ['PackPollSeconds','HoldAtSeconds','DyingSeconds']
    if positive:bad(f+' zero','R.'+f+' = 0.f','InvalidDeath.NotPositive',f)
    bad(f+' negative','R.'+f+' = -1.f','InvalidDeath.NotPositive' if positive else 'InvalidDeath.Negative',f)
    bad(f+' nextafter ceiling','R.'+f+' = std::nextafter(RPGBossDeathAdapters::MaxAuthoredMagnitude, std::numeric_limits<float>::infinity())','InvalidDeath.AboveCeiling',f)
for label,v,token in [('negative','-1','Negative'),('above ceiling','1000001','AboveCeiling'),('INT32_MAX','std::numeric_limits<int32>::max()','AboveCeiling')]:bad('restarts '+label,'R.MaxClipRestarts = '+v,'InvalidDeath.'+token,'MaxClipRestarts')
for f in fields[3:5]:
    for label,expression,token in [('None','NAME_None','Missing'),('mixed-case None','TEXT("nOnE")','Missing'),('space','TEXT("Ability A")','Malformed'),('tab',r'TEXT("Ability\tA")','Malformed'),('control','FName(*FString::Printf(TEXT("Ability%cA"), static_cast<TCHAR>(0x7f)))','Malformed')]:bad(f+' '+label,'R.'+f+' = '+expression,'InvalidDependency.'+token,f)
for f in fields[1:3]:bad('null '+f,'R.'+f+'.Reset()','InvalidDependency.Missing',f)
malformed=old[old.index('\t\tstruct FMalformed'):old.index('\t\tfor (const FMalformed& M')]
block+=malformed
block+='\t\tfor (const FMalformed& M : Malformed)\n\t\t{\n\t\t\tconst FSoftObjectPath Path = M.Path;\n'
for f,typ in [('DeathClip','Clip'),('DeathMontage','Montage')]:block+='\t\t\tCases.Add({FString(M.Name) + TEXT(" '+f+'"), [Path](FRPGDeathConfig& R) { R.'+f+' = '+typ+'(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("Death.'+f+'")});\n'
block+='\t\t}\n\t\treturn Cases;\n\t}\n'
block+=rename(old[old.index('\tbool HasError'):old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapAssignTest')])
def section(a,b):return rename(old[old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwap'+a+'Test'):old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwap'+b+'Test')])
assign=section('Assign','Validation').replace('five','twelve').replace('Five authored fields assigned; no ability, montage load or swap proof.','Twelve authored fields assigned; no native death/playback/remains proof.')
validation=r'''
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDeathValidationTest, "OneBossFight.Binding.Death.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDeathValidationTest::RunTest(const FString& Parameters)
{
	using namespace DeathTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossDeath> Death(NewObject<URPGBossDeath>(Owner));
	const auto Before = Read(*Death);
	const FRuntime Runtime(*Death);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA();
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator refuses"), RPGBossDeathAdapters::ValidateDeath(R, Error));
		TestTrue(Case.Name + TEXT(": named token/field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback refuses"), RPGBossDeathAdapters::ConfigureDeath(*Death, Config(R), Error));
		TestTrue(Case.Name + TEXT(": no partial write"), Same(Read(*Death), Before) && Runtime.SameAs(FRuntime(*Death)) && SameOwned(Components, Owned(Owner)));
	}
	TArray<FRPGDeathConfig> Valid{RecordA(), RecordB(), FRPGDeathConfig()};
'''
for f in floats:validation+='\t{ auto R = RecordA(); R.'+f+' = RPGBossDeathAdapters::MaxAuthoredMagnitude; Valid.Add(R); }\n'
validation+=r'''
	{ auto R = RecordA(); R.MaxClipRestarts = 1000000; Valid.Add(R); }
	{ auto R = RecordA(); R.bGuardPackDeath = false; Valid.Add(R); }
	for (const auto& R : Valid)
	{
		FString Error = TEXT("stale");
		TestTrue(TEXT("both modes/guards/off states/sub-editor floors/inclusive ceilings valid"), RPGBossDeathAdapters::ValidateDeath(R, Error) && Error.IsEmpty()
			&& RPGBossDeathAdapters::ConfigureDeath(*Death, Config(R), Error) && Same(Read(*Death), R) && Runtime.SameAs(FRuntime(*Death)));
	}
	auto First = [this](const FRPGDeathConfig& R, const TCHAR* Token, const TCHAR* Field)
	{
		FString E;
		TestFalse(TEXT("multi-invalid refusal"), RPGBossDeathAdapters::ValidateDeath(R, E));
		TestTrue(TEXT("first error order"), E.StartsWith(Token) && E.Contains(Field));
	};
	auto R = RecordA();
	R.DeathMode = static_cast<ERPGBossDeathMode>(255); R.BlendInSeconds = std::numeric_limits<float>::quiet_NaN();
	First(R, TEXT("InvalidDeath.NotFinite"), TEXT("Death.BlendInSeconds"));
	R = RecordA(); R.PackPollSeconds = 0.f; R.DeathMode = static_cast<ERPGBossDeathMode>(255);
	First(R, TEXT("InvalidDeath.BadMode"), TEXT("Death.DeathMode"));
	R = RecordA(); R.PackPollSeconds = std::numeric_limits<float>::infinity(); R.PackEndTimeMultiplier = std::numeric_limits<float>::quiet_NaN();
	First(R, TEXT("InvalidDeath.NotFinite"), TEXT("Death.PackPollSeconds"));
	R = RecordA(); R.MaxClipRestarts = -1; R.PackDeathAbilityClassName = NAME_None;
	First(R, TEXT("InvalidDeath.Negative"), TEXT("Death.MaxClipRestarts"));
	R = RecordA(); R.PackDeathMontagesName = NAME_None; R.DeathClip.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Death.PackDeathMontagesName"));
	R = RecordA(); R.DeathClip.Reset(); R.DeathMontage.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Death.DeathClip"));
	R = RecordB(); R.DeathClip.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Death.DeathClip")); // uniform both-path contract even PackMontage
	R = RecordA(); R.DeathMontage.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Death.DeathMontage")); // uniform both-path contract even OwnClip
	return true;
}

'''
isolation=section('Isolation','Rejections').replace('Input.Death.A1Montage = Montage','Input.Death.DeathMontage = Montage').replace('Invalid.A3bMontage.Reset();','Invalid.DeathMontage.Reset();')
reject=section('Rejections','Compile').replace('Bad.A1Montage.Reset();','Bad.DeathClip.Reset();').replace('swap a montage','play a death clip')
compile=section('Compile','Authoring').replace('five','twelve').replace('D->Death.A1Montage = Montage','D->Death.DeathMontage = Montage')
author=r'''
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDeathAuthoringTest, "OneBossFight.Binding.Death.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDeathAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace DeathTests;
	const UScriptStruct* Struct = FRPGDeathConfig::StaticStruct();
	int32 Count = 0;
	for (TFieldIterator<FProperty> It(Struct); It; ++It) { ++Count; TestTrue(TEXT("editable"), It->HasAnyPropertyFlags(CPF_Edit)); }
	TestEqual(TEXT("twelve authored fields"), Count, 12);
	const FEnumProperty* Mode = CastField<FEnumProperty>(Struct->FindPropertyByName(TEXT("DeathMode")));
	const FEnumProperty* NativeMode = CastField<FEnumProperty>(URPGBossDeath::StaticClass()->FindPropertyByName(TEXT("DeathMode")));
	TestTrue(TEXT("same reflected native enum"), Mode && NativeMode && Mode->GetEnum() == NativeMode->GetEnum());
	for (const TCHAR* N : {TEXT("PackDeathAbilityClassName"), TEXT("PackDeathMontagesName")}) { TestNotNull(N, CastField<FNameProperty>(Struct->FindPropertyByName(N))); }
	for (const TCHAR* N : {TEXT("PackPollSeconds"), TEXT("PackEndTimeMultiplier"), TEXT("HoldAtSeconds"), TEXT("DyingSeconds"), TEXT("BlendInSeconds")}) { TestNotNull(N, CastField<FFloatProperty>(Struct->FindPropertyByName(N))); }
	TestNotNull(TEXT("int32 restarts"), CastField<FIntProperty>(Struct->FindPropertyByName(TEXT("MaxClipRestarts"))));
	TestNotNull(TEXT("guard bool"), CastField<FBoolProperty>(Struct->FindPropertyByName(TEXT("bGuardPackDeath"))));
	const FSoftObjectProperty* ClipProperty = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(TEXT("DeathClip")));
	const FSoftObjectProperty* MontageProperty = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(TEXT("DeathMontage")));
	TestTrue(TEXT("typed clip and montage"), ClipProperty && ClipProperty->PropertyClass == UAnimSequence::StaticClass() && MontageProperty && MontageProperty->PropertyClass == UAnimMontage::StaticClass());
	const FStructProperty* Property = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("Death")));
	TestTrue(TEXT("Data Asset record"), Property && Property->Struct == Struct && Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGDeathConfig Default;
	TestTrue(TEXT("all native defaults"), Same(Default, Read(*GetDefault<URPGBossDeath>())));
	TestTrue(TEXT("explicit default baseline"), Default.DeathMode == ERPGBossDeathMode::PackMontage && Default.PackDeathAbilityClassName == FName(TEXT("GA_EnemyRagdollDeath_C"))
		&& Default.PackDeathMontagesName == FName(TEXT("DeathMontages")) && Default.PackPollSeconds == 1.f && Default.PackEndTimeMultiplier == 0.f && Default.HoldAtSeconds == 3.f
		&& Default.DyingSeconds == 2.5f && Default.BlendInSeconds == 0.1f && Default.MaxClipRestarts == 8 && !Default.bGuardPackDeath
		&& Default.DeathClip.ToString().EndsWith(TEXT("/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend"))
		&& Default.DeathMontage.ToString().EndsWith(TEXT("/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend")));
	for (const TCHAR* N : {TEXT("LoadedClip"), TEXT("LoadedMontage"), TEXT("State"), TEXT("DeathTime"), TEXT("RestartsThisDeath"), TEXT("ClipRestartCount"), TEXT("LoadedRemainsMesh"), TEXT("bPreloaded"), TEXT("NextPackPoll")})
	{
		TestNull(FString(N) + TEXT(" not authored"), Struct->FindPropertyByName(N));
	}
	AddInfo(TEXT("Reflection/defaults only. No pack ability, death flow, clip playback, remains or serialized authoring proof."));
	return true;
}
#endif
'''
text=start+block+assign+validation+isolation+reject+compile+author
assert 'CloseClipSwap' not in text and '.A1Montage' not in text and '.A3bMontage' not in text
(here/'Staging/RPGBossDeathAdaptersTests.cpp').write_text(text,encoding='utf-8')
print('DD25 six regression sources staged UNRUN. No Source or engine operation.')

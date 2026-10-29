"""C275/C277 unrun staged regression source. No live Source write."""
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[4]
old=(root/'Source/OneBossFight/Tests/RPGBossLookAdaptersTests.cpp').read_text(encoding='utf-8')
def rename(s):return s.replace('Look','CloseClipSwap')
start=rename(old[:old.index('\tFSoftObjectPath MakePath')])
start=start.replace('#include "Engine/SkeletalMesh.h"','#include "Animation/AnimMontage.h"').replace('#include "Engine/StaticMesh.h"\n','')
a=start.index('// SOURCE-ONLY');b=start.index('namespace',a)
start=start[:a]+'// STAGING ONLY, UNRUN. No CloseClipSwap BeginPlay/Tick/ApplyNowForTest,\n// ability reflection, montage load, test-enable call or gameplay operation.\n'+start[b:]
fields=['CloseAbilityClassName','AttackMontagesName','A1Montage','A3aMontage','A3bMontage']
block=r'''
	FSoftObjectPath MakePath(const TCHAR* Package, const TCHAR* Asset, const TCHAR* Sub = TEXT(""))
	{
		return FSoftObjectPath(FTopLevelAssetPath(FName(Package), FName(Asset)), FString(Sub));
	}
	TSoftObjectPtr<UAnimMontage> Montage(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UAnimMontage>(Path);
	}
	FRPGCloseClipSwapConfig RecordA()
	{
		FRPGCloseClipSwapConfig R;
		R.CloseAbilityClassName = TEXT("Custom.CloseAbility-A");
		R.AttackMontagesName = TEXT("Custom.Montages-A");
		R.A1Montage = Montage(MakePath(TEXT("/SyntheticMount/Close/A"), TEXT("A1")));
		R.A3aMontage = Montage(MakePath(TEXT("/SyntheticMount/Close/A"), TEXT("A3a")));
		R.A3bMontage = Montage(MakePath(TEXT("/SyntheticMount/Close/A"), TEXT("A3b")));
		return R;
	}
	FRPGCloseClipSwapConfig RecordB()
	{
		FRPGCloseClipSwapConfig R;
		R.CloseAbilityClassName = TEXT("CustomAbilityB");
		R.AttackMontagesName = TEXT("CustomMontagesB");
		R.A1Montage = Montage(MakePath(TEXT("/OtherSynthetic/Close/B"), TEXT("A1")));
		R.A3aMontage = Montage(MakePath(TEXT("/OtherSynthetic/Close/B"), TEXT("A3a")));
		R.A3bMontage = Montage(MakePath(TEXT("/OtherSynthetic/Close/B"), TEXT("A3b")));
		return R;
	}
	FRPGParticipantConfig Config(const FRPGCloseClipSwapConfig& R)
	{
		FRPGParticipantConfig C;
		C.CloseClipSwap = R;
		return C;
	}
	FRPGCloseClipSwapConfig Read(const URPGBossCloseClipSwap& CloseClipSwap)
	{
		FRPGCloseClipSwapConfig R;
'''
for f in fields:block+='\t\tR.'+f+' = CloseClipSwap.'+f+';\n'
block+='\t\treturn R;\n\t}\n\tbool Same(const FRPGCloseClipSwapConfig& A, const FRPGCloseClipSwapConfig& B)\n\t{\n\t\treturn '+ ' && '.join('A.'+f+(' == B.'+f if f in fields[:2] else '.ToSoftObjectPath() == B.'+f+'.ToSoftObjectPath()') for f in fields)+';\n\t}\n'
block+=r'''
	struct FRuntime
	{
		bool Applied, Registered, Begun, TickRegistered, CanTick;
		int32 Entries, Applies, Restores;
		FString LastResult;
		explicit FRuntime(const URPGBossCloseClipSwap& C)
			: Applied(C.IsApplied()), Registered(C.IsRegistered()), Begun(C.HasBegunPlay()),
			TickRegistered(C.PrimaryComponentTick.IsTickFunctionRegistered()), CanTick(C.PrimaryComponentTick.bCanEverTick),
			Entries(C.GetAppliedEntryCount()), Applies(C.GetApplyCount()), Restores(C.GetRestoreCount()), LastResult(C.GetLastResult()) {}
		bool SameAs(const FRuntime& O) const
		{
			return Applied == O.Applied && Registered == O.Registered && Begun == O.Begun && TickRegistered == O.TickRegistered
				&& CanTick == O.CanTick && Entries == O.Entries && Applies == O.Applies && Restores == O.Restores && LastResult == O.LastResult;
		}
	};
'''
block+=old[old.index('\tTArray<const UActorComponent*> Owned'):old.index('\tTArray<FString> Paths()')]
block+='\tTArray<FString> Paths()\n\t{\n\t\treturn {'+', '.join('TEXT("CloseClipSwap.'+f+'")' for f in fields)+'};\n\t}\n'
block+='\tstruct FBad\n\t{\n\t\tFString Name;\n\t\tTFunction<void(FRPGCloseClipSwapConfig&)> Mutate;\n\t\tconst TCHAR* Token;\n\t\tconst TCHAR* Path;\n\t};\n\tTArray<FBad> BadCases()\n\t{\n\t\tTArray<FBad> Cases;\n'
for f in fields[:2]:
    for label,expression,token in [('None','NAME_None','Missing'),('mixed-case None','TEXT("nOnE")','Missing'),('space','TEXT("Ability A")','Malformed'),('tab','TEXT("Ability\tA")','Malformed'),('control','FName(*FString::Printf(TEXT("Ability%cA"), static_cast<TCHAR>(0x7f)))','Malformed')]:
        block+='\t\tCases.Add({TEXT("'+f+' '+label+'"), [](FRPGCloseClipSwapConfig& R) { R.'+f+' = '+expression+'; }, TEXT("InvalidDependency.'+token+'"), TEXT("CloseClipSwap.'+f+'")});\n'
for f in fields[2:]:block+='\t\tCases.Add({TEXT("null '+f+'"), [](FRPGCloseClipSwapConfig& R) { R.'+f+'.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("CloseClipSwap.'+f+'")});\n'
malformed=old[old.index('\t\tstruct FMalformed'):old.index('\t\tfor (const FMalformed& M')]
block+=malformed.replace('Mesh','Montage').replace('//Look/A','//Close/A')
block+='\t\tfor (const FMalformed& M : Malformed)\n\t\t{\n\t\t\tconst FSoftObjectPath Path = M.Path;\n'
for f in fields[2:]:block+='\t\t\tCases.Add({FString(M.Name) + TEXT(" '+f+'"), [Path](FRPGCloseClipSwapConfig& R) { R.'+f+' = Montage(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("CloseClipSwap.'+f+'")});\n'
block+='\t\t}\n\t\treturn Cases;\n\t}\n'
block+=rename(old[old.index('\tbool HasError'):old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookAssignTest')])
def section(a,b):
    return rename(old[old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLook'+a+'Test'):old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLook'+b+'Test')])
assign=section('Assign','Validation').replace('Soft paths copied without loading; socket existence and runtime look are unresolved.','Five authored fields assigned; no ability, montage load or swap proof.')
validation=r'''
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapValidationTest, "OneBossFight.Binding.CloseClipSwap.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCloseClipSwapValidationTest::RunTest(const FString& Parameters)
{
	using namespace CloseClipSwapTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossCloseClipSwap> CloseClipSwap(NewObject<URPGBossCloseClipSwap>(Owner));
	const auto Before = Read(*CloseClipSwap);
	const FRuntime Runtime(*CloseClipSwap);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA();
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator refuses"), RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error));
		TestTrue(Case.Name + TEXT(": named first token/field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback refuses"), RPGBossCloseClipSwapAdapters::ConfigureCloseClipSwap(*CloseClipSwap, Config(R), Error));
		TestTrue(Case.Name + TEXT(": no partial write"), Same(Read(*CloseClipSwap), Before) && Runtime.SameAs(FRuntime(*CloseClipSwap)) && SameOwned(Components, Owned(Owner)));
	}
	TArray<FRPGCloseClipSwapConfig> Valid{RecordA(), RecordB(), FRPGCloseClipSwapConfig()};
	auto Repeated = RecordA();
	Repeated.A3aMontage = Repeated.A1Montage;
	Repeated.A3bMontage = Repeated.A1Montage;
	Valid.Add(Repeated); // distinct scalar fields, no container self-alias
	for (const auto& R : Valid)
	{
		FString Error = TEXT("stale");
		TestTrue(TEXT("non-suffix names/synthetic paths/repeated replacement/defaults valid"), RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error) && Error.IsEmpty()
			&& RPGBossCloseClipSwapAdapters::ConfigureCloseClipSwap(*CloseClipSwap, Config(R), Error) && Same(Read(*CloseClipSwap), R) && Runtime.SameAs(FRuntime(*CloseClipSwap)));
	}
	auto R = RecordA();
	R.CloseAbilityClassName = NAME_None;
	R.AttackMontagesName = NAME_None;
	R.A1Montage.Reset(); R.A3aMontage.Reset(); R.A3bMontage.Reset();
	FString Error;
	TestFalse(TEXT("multi-invalid fails"), RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error));
	TestTrue(TEXT("class name first"), Error.StartsWith(TEXT("InvalidDependency.Missing")) && Error.Contains(TEXT("CloseClipSwap.CloseAbilityClassName")));
	R.CloseAbilityClassName = RecordA().CloseAbilityClassName;
	RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error);
	TestTrue(TEXT("property name next"), Error.Contains(TEXT("CloseClipSwap.AttackMontagesName")));
	R.AttackMontagesName = RecordA().AttackMontagesName;
	RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error);
	TestTrue(TEXT("A1 before A3a/A3b"), Error.Contains(TEXT("CloseClipSwap.A1Montage")));
	R.A1Montage = RecordA().A1Montage;
	RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(R, Error);
	TestTrue(TEXT("A3a before A3b"), Error.Contains(TEXT("CloseClipSwap.A3aMontage")));
	return true;
}

'''
isolation=section('Isolation','Rejections')
a=isolation.index('\tInput.CloseClipSwap.Pieces[0]');b=isolation.index('\tInput.CloseClipSwap = RecordB();',a)
isolation=isolation[:a]+'''\tInput.CloseClipSwap.A1Montage = Montage(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Montage")));
\tTestTrue(TEXT("native soft reference owns independent value"), Same(Read(*A), RecordA()));
'''+isolation[b:]
isolation=isolation.replace('Invalid.Sword.Reset();','Invalid.A3bMontage.Reset();')
reject=section('Rejections','Compile').replace('Bad.Body.Reset();','Bad.A1Montage.Reset();').replace('apply a look','swap a montage')
compile=section('Compile','Authoring').replace('D->CloseClipSwap.Pieces[0] = Mesh(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Piece")));','D->CloseClipSwap.A1Montage = Montage(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Montage")));').replace('compiled piece array owns an independent copy','compiled soft reference owns an independent value').replace('mesh/socket resolution','ability/montage resolution')
a=compile.index('\tauto EmptyPieces');b=compile.index('\tauto Defaults',a)
compile=compile[:a]+compile[b:]
author=r'''
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCloseClipSwapAuthoringTest, "OneBossFight.Binding.CloseClipSwap.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGCloseClipSwapAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace CloseClipSwapTests;
	const UScriptStruct* Struct = FRPGCloseClipSwapConfig::StaticStruct();
	int32 Count = 0;
	for (TFieldIterator<FProperty> It(Struct); It; ++It) { ++Count; TestTrue(TEXT("editable"), It->HasAnyPropertyFlags(CPF_Edit)); }
	TestEqual(TEXT("five fields"), Count, 5);
	for (const TCHAR* N : {TEXT("CloseAbilityClassName"), TEXT("AttackMontagesName")})
	{
		TestNotNull(N, CastField<FNameProperty>(Struct->FindPropertyByName(N)));
	}
	for (const TCHAR* N : {TEXT("A1Montage"), TEXT("A3aMontage"), TEXT("A3bMontage")})
	{
		const FSoftObjectProperty* Property = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(N));
		TestTrue(FString(N) + TEXT(" soft montage"), Property && Property->PropertyClass == UAnimMontage::StaticClass());
	}
	const FStructProperty* Property = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("CloseClipSwap")));
	TestTrue(TEXT("Data Asset record"), Property && Property->Struct == Struct && Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGCloseClipSwapConfig Default;
	TestTrue(TEXT("all defaults match native constructor"), Same(Default, Read(*GetDefault<URPGBossCloseClipSwap>())));
	TestTrue(TEXT("default names and montage suffixes"), Default.CloseAbilityClassName == FName(TEXT("GA_GS_Boss_CloseAttack_C")) && Default.AttackMontagesName == FName(TEXT("AttackMontages"))
		&& Default.A1Montage.ToString().EndsWith(TEXT("/Animations/AM_Boss01_A1.AM_Boss01_A1"))
		&& Default.A3aMontage.ToString().EndsWith(TEXT("/Animations/AM_Boss01_A3a.AM_Boss01_A3a"))
		&& Default.A3bMontage.ToString().EndsWith(TEXT("/Animations/AM_Boss01_A3b.AM_Boss01_A3b")));
	for (const TCHAR* N : {TEXT("LoadedA1"), TEXT("LoadedA3a"), TEXT("LoadedA3b"), TEXT("SwappedAbility"), TEXT("Swaps"), TEXT("RetrySeconds"), TEXT("ApplyCount"), TEXT("RestoreCount"), TEXT("bApplied"), TEXT("bEnabledForTest"), TEXT("bPermanentFailure")})
	{
		TestNull(FString(N) + TEXT(" not authored"), Struct->FindPropertyByName(N));
	}
	AddInfo(TEXT("Declaration/reflection only. No live ability, load, swap or serialized/Details proof."));
	return true;
}
#endif
'''
text=start+block+assign+validation+isolation+reject+compile+author
unexpected = [s for s in text.splitlines() if 'Pieces' in s or 'Mesh(' in s or 'Look' in s]
assert not unexpected, unexpected
(here/'Staging/RPGBossCloseClipSwapAdaptersTests.cpp').write_text(text,encoding='utf-8')
print('Fifth DD24 staged file prepared: six UNRUN test sources. No live Source mutation or promotion. Self-alias audit still required before freeze.')

"""Create source-only regression fixtures; no UE or tests executed."""
from pathlib import Path
import re
here=Path(__file__).resolve().parent
root=here.parents[4]
old=(root/'Source/OneBossFight/Tests/RPGBossHealPunishAdaptersTests.cpp').read_text(encoding='utf-8')
start=old[:old.index('\tFRPGHealPunishConfig RecordA()')]
start=start.replace('HealPunish','Look').replace('// SOURCE-ONLY until', '// SOURCE-ONLY until')
a=start.index('// SOURCE-ONLY');b=start.index('namespace',a)
start=start[:a]+'''// SOURCE-ONLY until a lead release. No Look BeginPlay, Apply, enable-for-test,
// Revert, mesh loading or runtime appearance operation. Plain begun-owner fixture
// receives its unregistered Look component only AFTER the owner began play.
'''+start[b:]
start=start.replace('#include <limits>\n#include <cmath>','#include "Engine/SkeletalMesh.h"\n#include "Engine/StaticMesh.h"\n#include "UObject/TopLevelAssetPath.h"')
common=r'''
	FSoftObjectPath MakePath(const TCHAR* Package, const TCHAR* Asset, const TCHAR* Sub = TEXT(""))
	{
		return FSoftObjectPath(FTopLevelAssetPath(FName(Package), FName(Asset)), FString(Sub));
	}
	TSoftObjectPtr<USkeletalMesh> Mesh(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<USkeletalMesh>(Path);
	}
	TSoftObjectPtr<UStaticMesh> Weapon(const FSoftObjectPath& Path)
	{
		return TSoftObjectPtr<UStaticMesh>(Path);
	}
	FRPGLookConfig RecordA()
	{
		FRPGLookConfig R;
		R.bEnabled = false;
		R.Body = Mesh(MakePath(TEXT("/SyntheticMount/Look/A"), TEXT("Body")));
		R.Pieces = {Mesh(MakePath(TEXT("/SyntheticMount/Look/A"), TEXT("Crown"))), Mesh(MakePath(TEXT("/SyntheticMount/Look/A"), TEXT("Mantle")))};
		R.Sword = Weapon(MakePath(TEXT("/SyntheticMount/Look/A"), TEXT("Sword")));
		R.SwordSocket = TEXT("Custom.Grip-A");
		return R;
	}
	FRPGLookConfig RecordB()
	{
		FRPGLookConfig R;
		R.bEnabled = true;
		R.Body = Mesh(MakePath(TEXT("/OtherSynthetic/Look/B"), TEXT("BodyB")));
		R.Pieces = {Mesh(MakePath(TEXT("/OtherSynthetic/Look/B"), TEXT("Gauntlet")))};
		R.Sword = Weapon(MakePath(TEXT("/OtherSynthetic/Look/B"), TEXT("SwordB")));
		R.SwordSocket = TEXT("GripB");
		return R;
	}
	FRPGParticipantConfig Config(const FRPGLookConfig& R)
	{
		FRPGParticipantConfig C;
		C.Look = R;
		return C;
	}
	FRPGLookConfig Read(const URPGBossLook& Look)
	{
		FRPGLookConfig R;
		R.bEnabled = Look.bEnabled;
		R.Body = Look.Body;
		R.Pieces = Look.Pieces;
		R.Sword = Look.Sword;
		R.SwordSocket = Look.SwordSocket;
		return R;
	}
	bool Same(const FRPGLookConfig& A, const FRPGLookConfig& B)
	{
		if (A.bEnabled != B.bEnabled || A.Body.ToSoftObjectPath() != B.Body.ToSoftObjectPath()
			|| A.Sword.ToSoftObjectPath() != B.Sword.ToSoftObjectPath() || A.SwordSocket != B.SwordSocket || A.Pieces.Num() != B.Pieces.Num())
		{
			return false;
		}
		for (int32 Index = 0; Index < A.Pieces.Num(); ++Index)
		{
			if (A.Pieces[Index].ToSoftObjectPath() != B.Pieces[Index].ToSoftObjectPath()) { return false; }
		}
		return true;
	}
	struct FRuntime
	{
		bool Applied, Registered, Begun, TickRegistered, CanTick;
		int32 PieceCount, HiddenWeapons;
		const USkeletalMeshComponent* Body;
		const UStaticMeshComponent* Sword;
		explicit FRuntime(const URPGBossLook& Look)
			: Applied(Look.IsApplied()), Registered(Look.IsRegistered()), Begun(Look.HasBegunPlay()),
			TickRegistered(Look.PrimaryComponentTick.IsTickFunctionRegistered()), CanTick(Look.PrimaryComponentTick.bCanEverTick),
			PieceCount(Look.GetPieceCount()), HiddenWeapons(Look.GetHiddenPackWeaponCount()), Body(Look.GetBodyComponent()), Sword(Look.GetSwordComponent()) {}
		bool SameAs(const FRuntime& O) const
		{
			return Applied == O.Applied && Registered == O.Registered && Begun == O.Begun && TickRegistered == O.TickRegistered
				&& CanTick == O.CanTick && PieceCount == O.PieceCount && HiddenWeapons == O.HiddenWeapons && Body == O.Body && Sword == O.Sword;
		}
	};
'''
owned=old[old.index('\tTArray<const UActorComponent*> Owned'):old.index('\tTArray<FString> Paths()')]
cases=r'''
	TArray<FString> Paths()
	{
		return {TEXT("Look.bEnabled"), TEXT("Look.Body"), TEXT("Look.Pieces"), TEXT("Look.Sword"), TEXT("Look.SwordSocket")};
	}
	struct FBad
	{
		FString Name;
		TFunction<void(FRPGLookConfig&)> Mutate;
		const TCHAR* Token;
		const TCHAR* Path;
	};
	TArray<FBad> BadCases()
	{
		TArray<FBad> Cases;
		Cases.Add({TEXT("null body"), [](FRPGLookConfig& R) { R.Body.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("Look.Body")});
		Cases.Add({TEXT("null sword"), [](FRPGLookConfig& R) { R.Sword.Reset(); }, TEXT("InvalidDependency.Missing"), TEXT("Look.Sword")});
		Cases.Add({TEXT("late null piece"), [](FRPGLookConfig& R) { R.Pieces.Add(TSoftObjectPtr<USkeletalMesh>()); }, TEXT("InvalidDependency.Missing"), TEXT("Look.Pieces[2]")});
		Cases.Add({TEXT("duplicate piece"), [](FRPGLookConfig& R) { const TSoftObjectPtr<USkeletalMesh> Duplicate = R.Pieces[0]; R.Pieces.Add(Duplicate); }, TEXT("InvalidDependency.Duplicate"), TEXT("Look.Pieces[2]")});
		Cases.Add({TEXT("case-insensitive asset identity duplicate"), [](FRPGLookConfig& R) { R.Pieces.Add(Mesh(MakePath(TEXT("/syntheticmount/look/a"), TEXT("crown")))); }, TEXT("InvalidDependency.Duplicate"), TEXT("Look.Pieces[2]")});
		Cases.Add({TEXT("None socket"), [](FRPGLookConfig& R) { R.SwordSocket = NAME_None; }, TEXT("InvalidDependency.Missing"), TEXT("Look.SwordSocket")});
		Cases.Add({TEXT("mixed-case None socket"), [](FRPGLookConfig& R) { R.SwordSocket = TEXT("nOnE"); }, TEXT("InvalidDependency.Missing"), TEXT("Look.SwordSocket")});
		Cases.Add({TEXT("space socket"), [](FRPGLookConfig& R) { R.SwordSocket = TEXT("Grip A"); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.SwordSocket")});
		Cases.Add({TEXT("tab socket"), [](FRPGLookConfig& R) { R.SwordSocket = TEXT("Grip\tA"); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.SwordSocket")});
		Cases.Add({TEXT("control socket"), [](FRPGLookConfig& R) { R.SwordSocket = FName(*FString::Printf(TEXT("Grip%cA"), static_cast<TCHAR>(0x7f))); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.SwordSocket")});
		struct FMalformed { const TCHAR* Name; FSoftObjectPath Path; };
		// Exact accepted Bleed malformed-path fixture set, repeated for each reference slot.
		const FMalformed Malformed[] = {
			{TEXT("whitespace package"), MakePath(TEXT("/SyntheticMount/A B"), TEXT("Mesh"))},
			{TEXT("control object"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Mesh\tX"))},
			{TEXT("subobject"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Mesh"), TEXT("Sub"))},
			{TEXT("relative package"), MakePath(TEXT("Relative/A"), TEXT("Mesh"))},
			{TEXT("no folder"), MakePath(TEXT("/Root"), TEXT("Mesh"))},
			{TEXT("empty mount"), MakePath(TEXT("//Look/A"), TEXT("Mesh"))},
			{TEXT("repeated separator"), MakePath(TEXT("/SyntheticMount//A"), TEXT("Mesh"))},
			{TEXT("object dot"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Mesh.X"))},
			{TEXT("object pipe"), MakePath(TEXT("/SyntheticMount/A"), TEXT("Mesh|X"))},
			{TEXT("package pipe"), MakePath(TEXT("/SyntheticMount/A|B"), TEXT("Mesh"))},
		};
		for (const FMalformed& M : Malformed)
		{
			const FSoftObjectPath Path = M.Path;
			Cases.Add({FString(M.Name) + TEXT(" body"), [Path](FRPGLookConfig& R) { R.Body = Mesh(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.Body")});
			Cases.Add({FString(M.Name) + TEXT(" piece"), [Path](FRPGLookConfig& R) { R.Pieces.Add(Mesh(Path)); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.Pieces[2]")});
			Cases.Add({FString(M.Name) + TEXT(" sword"), [Path](FRPGLookConfig& R) { R.Sword = Weapon(Path); }, TEXT("InvalidDependency.Malformed"), TEXT("Look.Sword")});
		}
		return Cases;
	}
'''
tailcommon=old[old.index('\tbool HasError'):old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunishAssignTest')]
tailcommon=tailcommon.replace('HealPunish','Look')
def section(name,nextname):
    a=old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunish'+name+'Test')
    b=old.index('IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHealPunish'+nextname+'Test',a)
    return old[a:b].replace('HealPunish','Look').replace('Punish','Look').replace('fourteen','five')
assign=section('Assign','Validation').replace('Socket names copied by value; native A5/drink montage/socket resolution is unresolved.','Soft paths copied without loading; socket existence and runtime look are unresolved.')
validation=r'''
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookValidationTest, "OneBossFight.Binding.Look.Validation", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLookValidationTest::RunTest(const FString& Parameters)
{
	using namespace LookTests;
	FWorldScope Scope;
	AActor* Owner = Scope.Spawn();
	if (!TestNotNull(TEXT("owner"), Owner)) { return false; }
	TStrongObjectPtr<URPGBossLook> Look(NewObject<URPGBossLook>(Owner));
	const auto Before = Read(*Look);
	const FRuntime Runtime(*Look);
	const auto Components = Owned(Owner);
	for (const FBad& Case : BadCases())
	{
		auto R = RecordA(); // disabled records still validate all five fields
		Case.Mutate(R);
		FString Error;
		TestFalse(Case.Name + TEXT(": validator refuses"), RPGBossLookAdapters::ValidateLook(R, Error));
		TestTrue(Case.Name + TEXT(": named token and indexed field"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path));
		TestFalse(Case.Name + TEXT(": callback refuses"), RPGBossLookAdapters::ConfigureLook(*Look, Config(R), Error));
		TestTrue(Case.Name + TEXT(": no partial writes"), Error.StartsWith(Case.Token) && Error.Contains(Case.Path)
			&& Same(Read(*Look), Before) && Runtime.SameAs(FRuntime(*Look)) && SameOwned(Components, Owned(Owner)));
	}
	TArray<FRPGLookConfig> Valid{RecordA(), RecordB(), FRPGLookConfig()};
	auto Empty = RecordA();
	Empty.Pieces.Reset();
	Valid.Add(Empty);
	auto LongSocket = RecordB();
	LongSocket.SwordSocket = FName(*FString::ChrN(1100, TEXT('x')));
	Valid.Add(LongSocket); // no invented 1024-character policy
	for (const FRPGLookConfig& R : Valid)
	{
		FString Error = TEXT("stale");
		TestTrue(TEXT("valid non-mounted paths/empty pieces/defaults/long socket"), RPGBossLookAdapters::ValidateLook(R, Error) && Error.IsEmpty()
			&& RPGBossLookAdapters::ConfigureLook(*Look, Config(R), Error) && Same(Read(*Look), R) && Runtime.SameAs(FRuntime(*Look)));
	}
	auto First = [this](const FRPGLookConfig& R, const TCHAR* Token, const TCHAR* Path)
	{
		FString Error;
		TestFalse(TEXT("multi-invalid record refused"), RPGBossLookAdapters::ValidateLook(R, Error));
		TestTrue(TEXT("first failure order"), Error.StartsWith(Token) && Error.Contains(Path));
	};
	auto R = RecordA();
	R.Body.Reset(); R.Pieces[0].Reset(); R.Sword.Reset(); R.SwordSocket = NAME_None;
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Look.Body"));
	R = RecordA(); R.Pieces[0].Reset();
	const TSoftObjectPtr<USkeletalMesh> LaterDuplicate = R.Pieces[1];
	R.Pieces.Add(LaterDuplicate); R.Sword.Reset();
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Look.Pieces[0]"));
	R = RecordA();
	const TSoftObjectPtr<USkeletalMesh> FirstDuplicate = R.Pieces[0];
	R.Pieces.Add(FirstDuplicate); R.Sword.Reset();
	First(R, TEXT("InvalidDependency.Duplicate"), TEXT("Look.Pieces[2]"));
	R = RecordA(); R.Sword.Reset(); R.SwordSocket = NAME_None;
	First(R, TEXT("InvalidDependency.Missing"), TEXT("Look.Sword"));
	AddInfo(TEXT("Structure only; no path is loaded or class/socket existence certified."));
	return true;
}

'''
isolation=section('Isolation','Rejections').replace('Input.Look.SpawnSockets[0]=TEXT("ChangedAfterAssign"); Input.Look.SpawnSockets.Add(TEXT("Extra"));','Input.Look.Pieces[0] = Mesh(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Piece")));\n\tInput.Look.Pieces.Add(Mesh(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Extra"))));').replace('socket array','piece array').replace('Invalid.SpawnSockets.Reset();','Invalid.Sword.Reset();')
reject=section('Rejections','Compile').replace('Bad.SpawnSockets.Reset();','Bad.Body.Reset();').replace('start a sweep','apply a look')
compile=section('Compile','Authoring').replace('D->Look.SpawnSockets[0]=TEXT("ChangedAfterCompile");','D->Look.Pieces[0] = Mesh(MakePath(TEXT("/SyntheticMount/Changed"), TEXT("Piece")));').replace('socket array','piece array').replace('move-table resolution','mesh/socket resolution')
author=r'''
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLookAuthoringTest, "OneBossFight.Binding.Look.Authoring", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGLookAuthoringTest::RunTest(const FString& Parameters)
{
	using namespace LookTests;
	const UScriptStruct* Struct = FRPGLookConfig::StaticStruct();
	int32 Count = 0;
	for (TFieldIterator<FProperty> It(Struct); It; ++It)
	{
		++Count;
		TestTrue(TEXT("authored field editable"), It->HasAnyPropertyFlags(CPF_Edit));
	}
	TestEqual(TEXT("exact five authored properties"), Count, 5);
	TestNotNull(TEXT("enabled bool"), CastField<FBoolProperty>(Struct->FindPropertyByName(TEXT("bEnabled"))));
	TestNotNull(TEXT("socket FName"), CastField<FNameProperty>(Struct->FindPropertyByName(TEXT("SwordSocket"))));
	const FSoftObjectProperty* Body = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(TEXT("Body")));
	const FSoftObjectProperty* Sword = CastField<FSoftObjectProperty>(Struct->FindPropertyByName(TEXT("Sword")));
	const FArrayProperty* Pieces = CastField<FArrayProperty>(Struct->FindPropertyByName(TEXT("Pieces")));
	const FSoftObjectProperty* Inner = Pieces ? CastField<FSoftObjectProperty>(Pieces->Inner) : nullptr;
	TestTrue(TEXT("typed body/sword/piece soft references"), Body && Body->PropertyClass == USkeletalMesh::StaticClass()
		&& Sword && Sword->PropertyClass == UStaticMesh::StaticClass() && Inner && Inner->PropertyClass == USkeletalMesh::StaticClass());
	const FStructProperty* Property = CastField<FStructProperty>(URPGBossDefinition::StaticClass()->FindPropertyByName(TEXT("Look")));
	TestTrue(TEXT("editable Data Asset record"), Property && Property->Struct == Struct && Property->HasAnyPropertyFlags(CPF_Edit));
	const FRPGLookConfig Default;
	TestTrue(TEXT("all five native defaults including constructor soft paths"), Same(Default, Read(*GetDefault<URPGBossLook>())));
	TestTrue(TEXT("explicit declared baseline"), Default.bEnabled && Default.SwordSocket == FName(TEXT("HeavySwordSocket_R")) && Default.Pieces.Num() == 3
		&& Default.Body.ToString().EndsWith(TEXT("/Body/SK_Boss01_Body.SK_Boss01_Body"))
		&& Default.Sword.ToString().EndsWith(TEXT("/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword")));
	for (const TCHAR* N : {TEXT("bApplied"), TEXT("PieceCount"), TEXT("bSavedHidden"), TEXT("BodyComponent"), TEXT("SwordComponent"), TEXT("PieceComponents"), TEXT("HiddenPackWeapons"), TEXT("SavedTickOption")})
	{
		TestNull(FString(N) + TEXT(" not authored"), Struct->FindPropertyByName(N));
	}
	AddInfo(TEXT("Reflection/default comparison only, no mesh load/Apply/serialized Details proof."));
	return true;
}
#endif
'''
text=start+common+owned+cases+tailcommon+assign+validation+isolation+reject+compile+author
assert 'SpawnSockets' not in text and 'HealPunish' not in text and 'Punish' not in text
assert not re.search(r'["\']/Game/',text)
(root/'Source/OneBossFight/Tests/RPGBossLookAdaptersTests.cpp').write_text(text,encoding='utf-8')
print('DD23 six regression sources generated, UNRUN.')

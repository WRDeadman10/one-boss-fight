"""C269 source-only Look package. No compiler, engine, asset edit or load."""
from pathlib import Path
import re,hashlib,json
here=Path(__file__).resolve().parent
root=here.parents[4]
player=root/'Source/OneBossFight/Player'
assert not (player/'RPGBossLookAdapters.h').exists()
here.joinpath('Preimages').mkdir(exist_ok=True)
manifest={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'Source').rglob('*') if p.is_file()}
assert len(manifest)==203
baseline=(here.parent/'DD22/run_2026-10-29/final_source_manifest_sha256.txt').read_text(encoding='utf-8')
assert manifest=={line.split(' *',1)[1]:line.split(' *',1)[0] for line in baseline.splitlines()}
(here/'pre_source_manifest_sha256.txt').write_text(baseline,encoding='utf-8')
for n in ['RPGEncounterBinding.h','RPGEncounterBinding.cpp']:(here/'Preimages'/n).write_bytes((player/n).read_bytes())
native=(player/'RPGBossLook.cpp').read_text(encoding='utf-8')
paths=re.findall(r'FSoftObjectPath\(TEXT\("([^"]+)"\)\)',native)
assert len(paths)==5
asset_evidence=[]
for path in paths:
    asset=root/'Content'/ (path.removeprefix('/Game/').split('.',1)[0]+'.uasset')
    assert asset.is_file(),asset
    asset_evidence.append({'native_path':path,'file':asset.relative_to(root).as_posix(),'bytes':asset.stat().st_size,'sha256':hashlib.sha256(asset.read_bytes()).hexdigest()})
(here/'native_default_assets.json').write_text(json.dumps(asset_evidence,indent=2),encoding='utf-8')
h=player/'RPGEncounterBinding.h'
s=h.read_text(encoding='utf-8')
assert 'struct FRPGLookConfig' not in s
record='''/** C269 authored structure only; no asset class/load, socket fit or gameplay proof. */
USTRUCT(BlueprintType)
struct FRPGLookConfig
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) bool bEnabled = true;
	UPROPERTY(EditAnywhere) TSoftObjectPtr<USkeletalMesh> Body = TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("BODY_PATH")));
	UPROPERTY(EditAnywhere) TArray<TSoftObjectPtr<USkeletalMesh>> Pieces = {
		TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("PIECE0_PATH"))),
		TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("PIECE1_PATH"))),
		TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("PIECE2_PATH"))),
	};
	UPROPERTY(EditAnywhere) TSoftObjectPtr<UStaticMesh> Sword = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(TEXT("SWORD_PATH")));
	UPROPERTY(EditAnywhere) FName SwordSocket = TEXT("HeavySwordSocket_R");
};

'''
for key,value in zip(['BODY_PATH','PIECE0_PATH','PIECE1_PATH','PIECE2_PATH','SWORD_PATH'],paths):record=record.replace(key,value)
s=s.replace('class USoundBase;','class USoundBase;\nclass USkeletalMesh;\nclass UStaticMesh;')
s=s.replace('USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig',record+'USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig',1)
s=s.replace('UPROPERTY(EditAnywhere) FRPGHealPunishConfig HealPunish;','UPROPERTY(EditAnywhere) FRPGHealPunishConfig HealPunish;\n\tUPROPERTY(EditAnywhere) FRPGLookConfig Look;')
s=s.replace('\tFRPGHealPunishConfig HealPunish;','\tFRPGHealPunishConfig HealPunish;\n\tFRPGLookConfig Look;')
h.write_text(s,encoding='utf-8')
p=player/'RPGEncounterBinding.cpp'
s=p.read_text(encoding='utf-8').replace('#include "Player/RPGBossHealPunishAdapters.h"','#include "Player/RPGBossHealPunishAdapters.h"\n#include "Player/RPGBossLookAdapters.h"')
s=s.replace('\tTSet<FName> PhaseIds;','\tFString LookError;\n\tif (!RPGBossLookAdapters::ValidateLook(D.Look, LookError))\n\t{\n\t\tResult.Fail(LookError);\n\t}\n\tTSet<FName> PhaseIds;',1)
s=s.replace('\tValue->HealPunish = D.HealPunish;','\tValue->HealPunish = D.HealPunish;\n\tValue->Look = D.Look;')
p.write_text(s,encoding='utf-8')
(player/'RPGBossLookAdapters.h').write_text('''// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/** C269 UNWIRED authored record contracts, not native guards. No numeric field:
 * no magnitude ceiling or numeric arithmetic audit applies. Body and Sword are
 * required structural paths; Pieces may be empty but no entry may be null,
 * malformed or a duplicate FSoftObjectPath. Every record, even disabled, validates.
 * Socket is syntactic identity only; mesh/socket existence and hand_r fallback
 * remain UNRESOLVED. No class, mount, registry, existence check or load.
 * Native Apply body-load failure warns and leaves the pack mesh visible; a failed
 * piece warns and is omitted; a failed sword warns and leaves no new sword.
 * Those runtime outcomes are UNRESOLVED here, not prevented by typed structure.
 * Lifecycle guard: exact live class, unregistered/not begun, live not-begun owner.
 * Whole record validates before all five writes; no runtime/transient state write,
 * allocation, BeginPlay/Apply/enable-for-test call or load. No Ready or suppression.
 */
namespace RPGBossLookAdapters
{
	inline constexpr const TCHAR* FieldbEnabled = TEXT("Look.bEnabled");
	inline constexpr const TCHAR* FieldBody = TEXT("Look.Body");
	inline constexpr const TCHAR* FieldPieces = TEXT("Look.Pieces");
	inline constexpr const TCHAR* FieldSword = TEXT("Look.Sword");
	inline constexpr const TCHAR* FieldSwordSocket = TEXT("Look.SwordSocket");
	ONEBOSSFIGHT_API bool ValidateLook(const FRPGLookConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureLook(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeLookPlan();
}
''',encoding='utf-8')
bleed=(player/'RPGBossBleedAdapters.cpp').read_text(encoding='utf-8')
guard=bleed[bleed.index('\t\tbool CheckConfigurable'):bleed.index('\t\t/** Structure of a soft path')]
helper=bleed[bleed.index('\t\tFString PathProblem'):bleed.index('\t\tstruct FScalar')]
cpp='''// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossLookAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Misc/PackageName.h"
#include "Player/RPGBossLook.h"
#include "UObject/SoftObjectPath.h"

namespace RPGBossLookAdapters
{
	namespace
	{
'''+guard+'''		// PathProblem/CheckRequiredReference restated privately, byte-equivalent
		// policy from accepted RPGBossBleedAdapters.cpp. Frozen Bleed is unchanged.
'''+helper+'''	}

	bool ValidateLook(const FRPGLookConfig& Record, FString& OutError)
	{
		OutError.Reset();
		if (!CheckRequiredReference(FieldBody, Record.Body.ToSoftObjectPath(), OutError))
		{
			return false;
		}
		TSet<FSoftObjectPath> SeenPieces;
		for (int32 Index = 0; Index < Record.Pieces.Num(); ++Index)
		{
			const FString Field = FString::Printf(TEXT("%s[%d]"), FieldPieces, Index);
			const FSoftObjectPath Path = Record.Pieces[Index].ToSoftObjectPath();
			if (!CheckRequiredReference(*Field, Path, OutError))
			{
				return false;
			}
			if (SeenPieces.Contains(Path))
			{
				OutError = FString::Printf(TEXT("InvalidDependency.Duplicate: %s=%s"), *Field, *Path.ToString());
				return false;
			}
			SeenPieces.Add(Path);
		}
		if (!CheckRequiredReference(FieldSword, Record.Sword.ToSoftObjectPath(), OutError))
		{
			return false;
		}
		if (Record.SwordSocket.IsNone())
		{
			OutError = FString::Printf(TEXT("InvalidDependency.Missing: %s is required"), FieldSwordSocket);
			return false;
		}
		for (const TCHAR C : Record.SwordSocket.ToString())
		{
			if (FChar::IsWhitespace(C) || FChar::IsControl(C))
			{
				OutError = FString::Printf(TEXT("InvalidDependency.Malformed: %s contains whitespace or control"), FieldSwordSocket);
				return false;
			}
		}
		return true;
	}

	bool ConfigureLook(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, URPGBossLook::StaticClass(), OutError) || !ValidateLook(Config.Look, OutError))
		{
			return false;
		}
		URPGBossLook* Look = CastChecked<URPGBossLook>(&Component);
		Look->bEnabled = Config.Look.bEnabled;
		Look->Body = Config.Look.Body;
		Look->Pieces = Config.Look.Pieces;
		Look->Sword = Config.Look.Sword;
		Look->SwordSocket = Config.Look.SwordSocket;
		return true;
	}

	FRPGComponentPlan MakeLookPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossLook::StaticClass();
		Plan.InstanceName = TEXT("RPGBossLook");
		Plan.RequiredFields = {FieldbEnabled, FieldBody, FieldPieces, FieldSword, FieldSwordSocket};
		Plan.Configure = &ConfigureLook;
		return Plan;
	}
}
'''
(player/'RPGBossLookAdapters.cpp').write_text(cpp,encoding='utf-8')
print('DD23 record/adapter/compiler written, source only. Native files untouched; five constructor asset files statically present and hashed.')

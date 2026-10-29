"""C275 STAGING ONLY. No live Source/ write or engine operation."""
from pathlib import Path
import re,json,hashlib
here=Path(__file__).resolve().parent
root=here.parents[4]
player=root/'Source/OneBossFight/Player'
stage=here/'Staging'
stage.mkdir(exist_ok=False)
paths=re.findall(r'FSoftObjectPath\(TEXT\("([^"]+)"\)\)',(player/'RPGBossCloseClipSwap.cpp').read_text(encoding='utf-8'))
assert len(paths)==3
assets=[]
for path in paths:
    asset=root/'Content'/(path.removeprefix('/Game/').split('.',1)[0]+'.uasset')
    assert asset.is_file()
    assets.append({'path':path,'file':asset.relative_to(root).as_posix(),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest()})
(here/'native_default_assets.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
record='''/** C275 staged authored structure only; runtime reflection/swap remains unresolved. */
USTRUCT(BlueprintType)
struct FRPGCloseClipSwapConfig
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) FName CloseAbilityClassName = TEXT("GA_GS_Boss_CloseAttack_C");
	UPROPERTY(EditAnywhere) FName AttackMontagesName = TEXT("AttackMontages");
'''
fields=['CloseAbilityClassName','AttackMontagesName','A1Montage','A3aMontage','A3bMontage']
for field,path in zip(fields[2:],paths):record+='\tUPROPERTY(EditAnywhere) TSoftObjectPtr<UAnimMontage> '+field+' = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("'+path+'")));\n'
record+='};\n\n'
s=(player/'RPGEncounterBinding.h').read_text(encoding='utf-8')
assert 'struct FRPGCloseClipSwapConfig' not in s
s=s.replace('USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig',record+'USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig',1)
s=s.replace('UPROPERTY(EditAnywhere) FRPGLookConfig Look;','UPROPERTY(EditAnywhere) FRPGLookConfig Look;\n\tUPROPERTY(EditAnywhere) FRPGCloseClipSwapConfig CloseClipSwap;').replace('\tFRPGLookConfig Look;','\tFRPGLookConfig Look;\n\tFRPGCloseClipSwapConfig CloseClipSwap;')
(stage/'RPGEncounterBinding.h').write_text(s,encoding='utf-8')
s=(player/'RPGEncounterBinding.cpp').read_text(encoding='utf-8').replace('#include "Player/RPGBossLookAdapters.h"','#include "Player/RPGBossLookAdapters.h"\n#include "Player/RPGBossCloseClipSwapAdapters.h"')
s=s.replace('\tTSet<FName> PhaseIds;','\tFString CloseClipSwapError;\n\tif (!RPGBossCloseClipSwapAdapters::ValidateCloseClipSwap(D.CloseClipSwap, CloseClipSwapError))\n\t{\n\t\tResult.Fail(CloseClipSwapError);\n\t}\n\tTSet<FName> PhaseIds;',1).replace('\tValue->Look = D.Look;','\tValue->Look = D.Look;\n\tValue->CloseClipSwap = D.CloseClipSwap;')
(stage/'RPGEncounterBinding.cpp').write_text(s,encoding='utf-8')
header='''// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/** C275 UNWIRED authored record contracts, not native guards. Five fields, no
 * numeric field: no NotFinite, magnitude ceiling or numeric arithmetic audit.
 * Class/property FNames are syntactic identities only, no suffix/existence rule.
 * Three montage paths required and well-formed, no registry/mount/class/load check.
 * No duplicate rule: identical replacement assets do not create extra components;
 * the three existing pack slots may independently point at the same montage.
 * Live ability reflection, permanent-failure guard, four-entry/three-candidate
 * pack montage rules, playback/timing and successful swap remain UNRESOLVED.
 * Whole record validates after lifecycle checks before five assignments.
 * No transient state, ability, loaded montage or test-enable knob is touched.
 * No BeginPlay, Tick, load, preload, ApplyNowForTest or gameplay operation.
 */
namespace RPGBossCloseClipSwapAdapters
{
'''
for field in fields:header+='\tinline constexpr const TCHAR* Field'+field+' = TEXT("CloseClipSwap.'+field+'");\n'
header+='''	ONEBOSSFIGHT_API bool ValidateCloseClipSwap(const FRPGCloseClipSwapConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureCloseClipSwap(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeCloseClipSwapPlan();
}
'''
(stage/'RPGBossCloseClipSwapAdapters.h').write_text(header,encoding='utf-8')
look=(player/'RPGBossLookAdapters.cpp').read_text(encoding='utf-8')
s=look[:look.index('\tbool ValidateLook')].replace('RPGBossLook','RPGBossCloseClipSwap')
s+='''	bool ValidateCloseClipSwap(const FRPGCloseClipSwapConfig& Record, FString& OutError)
	{
		OutError.Reset();
'''
for field in fields[:2]:
    s+='''		if (Record.FIELD.IsNone())
		{
			OutError = FString::Printf(TEXT("InvalidDependency.Missing: %s is required"), FieldFIELD);
			return false;
		}
		for (const TCHAR C : Record.FIELD.ToString())
		{
			if (FChar::IsWhitespace(C) || FChar::IsControl(C))
			{
				OutError = FString::Printf(TEXT("InvalidDependency.Malformed: %s contains whitespace or control"), FieldFIELD);
				return false;
			}
		}
'''.replace('FIELD',field)
for field in fields[2:]:
    s+='''		if (!CheckRequiredReference(FieldFIELD, Record.FIELD.ToSoftObjectPath(), OutError))
		{
			return false;
		}
'''.replace('FIELD',field)
s+='''		return true;
	}

	bool ConfigureCloseClipSwap(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, URPGBossCloseClipSwap::StaticClass(), OutError) || !ValidateCloseClipSwap(Config.CloseClipSwap, OutError))
		{
			return false;
		}
		URPGBossCloseClipSwap* CloseClipSwap = CastChecked<URPGBossCloseClipSwap>(&Component);
'''
for field in fields:s+='\t\tCloseClipSwap->'+field+' = Config.CloseClipSwap.'+field+';\n'
s+='''		return true;
	}

	FRPGComponentPlan MakeCloseClipSwapPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossCloseClipSwap::StaticClass();
		Plan.InstanceName = TEXT("RPGBossCloseClipSwap");
'''
s+='\t\tPlan.RequiredFields = {'+', '.join('Field'+f for f in fields)+'};\n'
s+='\t\tPlan.Configure = &ConfigureCloseClipSwap;\n\t\treturn Plan;\n\t}\n}\n'
(stage/'RPGBossCloseClipSwapAdapters.cpp').write_text(s,encoding='utf-8')
# Preserve the exact baseline this staged Binding delta was based on.
(here/'binding_base_sha256.txt').write_text(''.join(hashlib.sha256((player/n).read_bytes()).hexdigest()+' *Source/OneBossFight/Player/'+n+'\n' for n in ['RPGEncounterBinding.h','RPGEncounterBinding.cpp']),encoding='utf-8')
print('Four DD24 staged source files prepared against current DD23 Binding. Live Source untouched. Tests still to prepare; not a handoff.')

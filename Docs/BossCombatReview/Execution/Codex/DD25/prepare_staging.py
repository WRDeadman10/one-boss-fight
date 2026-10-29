"""C281/C284 STAGING ONLY; no live Source, engine, build or native write."""
from pathlib import Path
import re,json,hashlib
here=Path(__file__).resolve().parent
root=here.parents[4]
player=root/'Source/OneBossFight/Player'
stage=here/'Staging'
stage.mkdir(exist_ok=False)
fields=['DeathMode','DeathClip','DeathMontage','PackDeathAbilityClassName','PackDeathMontagesName','PackPollSeconds','PackEndTimeMultiplier','HoldAtSeconds','DyingSeconds','BlendInSeconds','MaxClipRestarts','bGuardPackDeath']
floats=['PackPollSeconds','PackEndTimeMultiplier','HoldAtSeconds','DyingSeconds','BlendInSeconds']
paths=re.findall(r'FSoftObjectPath\(TEXT\("([^"]+)"\)\)',(player/'RPGBossDeath.cpp').read_text(encoding='utf-8'))
assert len(paths)==2
assets=[]
for path in paths:
    p=root/'Content'/(path.removeprefix('/Game/').split('.',1)[0]+'.uasset')
    assert p.is_file()
    assets.append({'path':path,'file':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(here/'native_default_assets.json').write_text(json.dumps(assets,indent=2),encoding='utf-8')
record='''/** C281/C284 authored record; both paths required, no native runtime guarantee. */
USTRUCT(BlueprintType)
struct FRPGDeathConfig
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) ERPGBossDeathMode DeathMode = ERPGBossDeathMode::PackMontage;
'''
for field,typ,path in zip(fields[1:3],['UAnimSequence','UAnimMontage'],paths):record+='\tUPROPERTY(EditAnywhere) TSoftObjectPtr<'+typ+'> '+field+' = TSoftObjectPtr<'+typ+'>(FSoftObjectPath(TEXT("'+path+'")));\n'
record+='''	UPROPERTY(EditAnywhere) FName PackDeathAbilityClassName = TEXT("GA_EnemyRagdollDeath_C");
	UPROPERTY(EditAnywhere) FName PackDeathMontagesName = TEXT("DeathMontages");
	UPROPERTY(EditAnywhere) float PackPollSeconds = 1.f;
	UPROPERTY(EditAnywhere) float PackEndTimeMultiplier = 0.f;
	UPROPERTY(EditAnywhere) float HoldAtSeconds = 3.f;
	UPROPERTY(EditAnywhere) float DyingSeconds = 2.5f;
	UPROPERTY(EditAnywhere) float BlendInSeconds = 0.1f;
	UPROPERTY(EditAnywhere) int32 MaxClipRestarts = 8;
	UPROPERTY(EditAnywhere) bool bGuardPackDeath = false;
};

'''
s=(player/'RPGEncounterBinding.h').read_text(encoding='utf-8')
s=s.replace('#include "Player/RPGCombatCatalog.h"','#include "Player/RPGCombatCatalog.h"\n#include "Player/RPGBossDeath.h"')
s=s.replace('USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig',record+'USTRUCT(BlueprintType)\nstruct FRPGPhaseConfig',1)
s=s.replace('UPROPERTY(EditAnywhere) FRPGCloseClipSwapConfig CloseClipSwap;','UPROPERTY(EditAnywhere) FRPGCloseClipSwapConfig CloseClipSwap;\n\tUPROPERTY(EditAnywhere) FRPGDeathConfig Death;').replace('\tFRPGCloseClipSwapConfig CloseClipSwap;','\tFRPGCloseClipSwapConfig CloseClipSwap;\n\tFRPGDeathConfig Death;')
(stage/'RPGEncounterBinding.h').write_text(s,encoding='utf-8')
s=(player/'RPGEncounterBinding.cpp').read_text(encoding='utf-8').replace('#include "Player/RPGBossCloseClipSwapAdapters.h"','#include "Player/RPGBossCloseClipSwapAdapters.h"\n#include "Player/RPGBossDeathAdapters.h"')
s=s.replace('\tTSet<FName> PhaseIds;','\tFString DeathError;\n\tif (!RPGBossDeathAdapters::ValidateDeath(D.Death, DeathError))\n\t{\n\t\tResult.Fail(DeathError);\n\t}\n\tTSet<FName> PhaseIds;',1).replace('\tValue->CloseClipSwap = D.CloseClipSwap;','\tValue->CloseClipSwap = D.CloseClipSwap;\n\tValue->Death = D.Death;')
(stage/'RPGEncounterBinding.cpp').write_text(s,encoding='utf-8')
header='''// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/** C281/C284 UNWIRED AUTHORED RECORD CONTRACTS, not native guards or tuning.
 * Five floats finite first, then enum, numeric domains, names and BOTH soft paths.
 * PackEndTimeMultiplier zero means OFF; both mode values and guard bools legal.
 * Restarts int32 in [0,1000000] closes the per-death equality-branch increment
 * overflow reasoning. Cumulative ClipRestartCount, external time/Age narrowing
 * and playback/asset timing remain separate residual hazards, not certified.
 * Native Attach internally returns Existing without assigning Mode: typed mode
 * remains authoritative on reuse. No second-instance claim, race/reservation or
 * activation-order guarantee. Constructor enables tick; first Tick preloads only
 * the selected mode. Live pack ability reflection, ragdoll/pose behaviour and
 * KI-083 pack destruction/remains EndPlay behaviour are UNRESOLVED here.
 * Both paths required uniformly by authored choice, no mode fallback, load,
 * registry/mount/class/existence query. Full validation precedes all12 writes.
 * Same exact live/unregistered/not-begun component/live not-begun owner boundary.
 * No runtime state, loaded clips or remains touched, no BeginPlay/Tick/Attach,
 * pack ability, remains or test knob invoked. No Ready/legacy suppression.
 */
namespace RPGBossDeathAdapters
{
	inline constexpr float MaxAuthoredMagnitude = 1.0e6f;
	inline constexpr int32 MaxAuthoredRestarts = 1000000;
'''
for f in fields:header+='\tinline constexpr const TCHAR* Field'+f+' = TEXT("Death.'+f+'");\n'
header+='''	ONEBOSSFIGHT_API bool ValidateDeath(const FRPGDeathConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureDeath(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeDeathPlan();
}
'''
(stage/'RPGBossDeathAdapters.h').write_text(header,encoding='utf-8')
prior=(player/'RPGBossCloseClipSwapAdapters.cpp').read_text(encoding='utf-8')
s=prior[:prior.index('\tbool ValidateCloseClipSwap')].replace('RPGBossCloseClipSwap','RPGBossDeath')
# Private helper addition, separate from the unchanged restated path helper.
i=s.rfind('\t}\n')
s=s[:i]+'''		bool Refuse(FString& Error, const TCHAR* Token, const TCHAR* Field)
		{
			Error = FString::Printf(TEXT("%s: %s"), Token, Field);
			return false;
		}
'''+s[i:]
s+='''	bool ValidateDeath(const FRPGDeathConfig& Record, FString& OutError)
	{
		OutError.Reset();
		struct FScalar { const TCHAR* Field; float Value; };
		const FScalar Scalars[] = {
'''
for f in floats:s+='\t\t\t{Field'+f+', Record.'+f+'},\n'
s+='''		};
		for (const FScalar& Scalar : Scalars)
		{
			if (!FMath::IsFinite(Scalar.Value))
			{
				return Refuse(OutError, TEXT("InvalidDeath.NotFinite"), Scalar.Field);
			}
		}
		if (Record.DeathMode != ERPGBossDeathMode::PackMontage && Record.DeathMode != ERPGBossDeathMode::OwnClip)
		{
			return Refuse(OutError, TEXT("InvalidDeath.BadMode"), FieldDeathMode);
		}
'''
for f in floats:
    positive=f in ['PackPollSeconds','HoldAtSeconds','DyingSeconds']
    op='<=' if positive else '<'
    token='NotPositive' if positive else 'Negative'
    s+='\t\tif (Record.'+f+' '+op+' 0.f)\n\t\t{\n\t\t\treturn Refuse(OutError, TEXT("InvalidDeath.'+token+'"), Field'+f+');\n\t\t}\n'
    s+='\t\tif (Record.'+f+' > MaxAuthoredMagnitude)\n\t\t{\n\t\t\treturn Refuse(OutError, TEXT("InvalidDeath.AboveCeiling"), Field'+f+');\n\t\t}\n'
for op,val,token in [('<','0','Negative'),('>','MaxAuthoredRestarts','AboveCeiling')]:
    s+='\t\tif (Record.MaxClipRestarts '+op+' '+val+')\n\t\t{\n\t\t\treturn Refuse(OutError, TEXT("InvalidDeath.'+token+'"), FieldMaxClipRestarts);\n\t\t}\n'
for f in fields[3:5]:
    s+='\t\tif (Record.'+f+'.IsNone())\n\t\t{\n\t\t\treturn Refuse(OutError, TEXT("InvalidDependency.Missing"), Field'+f+');\n\t\t}\n'
    s+='\t\tfor (const TCHAR C : Record.'+f+'.ToString())\n\t\t{\n\t\t\tif (FChar::IsWhitespace(C) || FChar::IsControl(C))\n\t\t\t{\n\t\t\t\treturn Refuse(OutError, TEXT("InvalidDependency.Malformed"), Field'+f+');\n\t\t\t}\n\t\t}\n'
for f in fields[1:3]:s+='\t\tif (!CheckRequiredReference(Field'+f+', Record.'+f+'.ToSoftObjectPath(), OutError))\n\t\t{\n\t\t\treturn false;\n\t\t}\n'
s+='''		return true;
	}

	bool ConfigureDeath(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, URPGBossDeath::StaticClass(), OutError) || !ValidateDeath(Config.Death, OutError))
		{
			return false;
		}
		URPGBossDeath* Death = CastChecked<URPGBossDeath>(&Component);
'''
for f in fields:s+='\t\tDeath->'+f+' = Config.Death.'+f+';\n'
s+='\t\treturn true;\n\t}\n\n\tFRPGComponentPlan MakeDeathPlan()\n\t{\n\t\tFRPGComponentPlan Plan;\n\t\tPlan.Class = URPGBossDeath::StaticClass();\n\t\tPlan.InstanceName = TEXT("RPGBossDeath");\n'
s+='\t\tPlan.RequiredFields = {'+', '.join('Field'+f for f in fields)+'};\n\t\tPlan.Configure = &ConfigureDeath;\n\t\treturn Plan;\n\t}\n}\n'
(stage/'RPGBossDeathAdapters.cpp').write_text(s,encoding='utf-8')
(here/'binding_base_sha256.txt').write_text(''.join(hashlib.sha256((player/n).read_bytes()).hexdigest()+' *Source/OneBossFight/Player/'+n+'\n' for n in ['RPGEncounterBinding.h','RPGEncounterBinding.cpp']),encoding='utf-8')
audit=(here/'C281_PREWRITE_SOURCE_FINDINGS.md').read_text(encoding='utf-8')
(here/'NATIVE_ARITHMETIC_AUDIT.md').write_text(audit+'\nC284 supersedes the historical continuation request above: authored MaxClipRestarts0..1000000, closes per-death equality-increment reasoning only. Native remains unchanged. Cumulative ClipRestartCount, external world times/Age narrowing remain separate. Attach internally reuses Existing without Mode overwrite. No runtime reproduction or tuning claim.\n',encoding='utf-8')
(here/'STAGING_STATUS.md').write_text('C281/C284: four Death source drafts prepared only in Staging. No staged tests yet, no promotion, handoff, build or UE run. All12fields/order and amended int ceiling implemented; source review/freeze incomplete.\n',encoding='utf-8')
print('DD25 four staged files prepared; tests/freeze pending. Source unchanged, no engine action.')

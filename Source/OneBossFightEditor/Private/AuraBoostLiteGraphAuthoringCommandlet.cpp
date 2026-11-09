#include "AuraBoostLiteGraphAuthoringCommandlet.h"

#include "AssetToolsModule.h"
#include "EdGraph/EdGraphPin.h"
#include "EdGraphSchema_Niagara.h"
#include "HAL/PlatformFileManager.h"
#include "IAssetTools.h"
#include "Misc/PackageName.h"
#include "NiagaraEditorModule.h"
#include "NiagaraEmitter.h"
#include "NiagaraEmitterHandle.h"
#include "NiagaraGraph.h"
#include "NiagaraNodeFunctionCall.h"
#include "NiagaraParameterStore.h"
#include "NiagaraScript.h"
#include "NiagaraScriptSource.h"
#include "NiagaraScriptVariable.h"
#include "NiagaraSystem.h"
#include "UObject/SavePackage.h"
#include "ViewModels/Stack/NiagaraParameterHandle.h"
#include "ViewModels/Stack/NiagaraStackGraphUtilities.h"

namespace
{
	const TCHAR* SourcePath = TEXT("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite");
	const TCHAR* DestinationPath = TEXT("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite_Authored");
	const TCHAR* ProductionPath = TEXT("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura");
	const TCHAR* PackRoot = TEXT("/Game/AdvancedARPGCombat");
	const TCHAR* LogPrefix = TEXT("[AuraGraphAuthoring]");

	bool assert_safe_copy_paths()
	{
		return FCString::Strncmp(DestinationPath, TEXT("/Game/OneBossFight/VFX/"), FCString::Strlen(TEXT("/Game/OneBossFight/VFX/"))) == 0
			&& FCString::Strcmp(DestinationPath, ProductionPath) != 0
			&& FCString::Strncmp(DestinationPath, PackRoot, FCString::Strlen(PackRoot)) != 0;
	}

	bool SaveSystem(UNiagaraSystem* System)
	{
		if (!System || !System->GetPackage()) return false;
		const FString Filename = FPackageName::LongPackageNameToFilename(System->GetPackage()->GetName(), FPackageName::GetAssetPackageExtension());
		FSavePackageArgs Args;
		Args.TopLevelFlags = RF_Public | RF_Standalone;
		Args.bWarnOfLongFilename = false;
		return UPackage::SavePackage(System->GetPackage(), System, *Filename, Args);
	}

	bool AllScriptsCompiled(UNiagaraSystem& System)
	{
		for (const FNiagaraEmitterHandle& Handle : System.GetEmitterHandles())
		{
			FVersionedNiagaraEmitterData* Data = Handle.GetEmitterData();
			if (!Data) return false;
			TArray<UNiagaraScript*> Scripts;
			Data->GetScripts(Scripts, true, true);
			for (UNiagaraScript* Script : Scripts)
			{
				if (!Script) return false;
				const ENiagaraScriptCompileStatus Status = Script->GetLastCompileStatus();
				if (Status != ENiagaraScriptCompileStatus::NCS_UpToDate &&
					Status != ENiagaraScriptCompileStatus::NCS_UpToDateWithWarnings &&
					Status != ENiagaraScriptCompileStatus::NCS_ComputeUpToDateWithWarnings)
				{
					UE_LOG(LogTemp, Error, TEXT("%s Script compile not current: %s Status=%s"), LogPrefix, *Script->GetPathName(), *UEnum::GetValueAsString(Status));
					return false;
				}
			}
		}
		return true;
	}

	bool SetModuleInput(UNiagaraNodeFunctionCall& Call, const FName InputName, const TFunction<void(FNiagaraVariable&)>& AssignValue)
	{
		UNiagaraScriptSource* FunctionSource = Call.GetFunctionScriptSource();
		UNiagaraGraph* FunctionGraph = FunctionSource ? FunctionSource->NodeGraph : nullptr;
		UNiagaraGraph* OwnerGraph = Call.GetNiagaraGraph();
		if (!FunctionGraph || !OwnerGraph) return false;

		const FName FullName = InputName;
		UNiagaraScriptVariable* ScriptVariable = FunctionGraph->GetScriptVariable(FullName);
		if (!ScriptVariable)
		{
			UE_LOG(LogTemp, Error, TEXT("%s Missing function input metadata %s in %s"), LogPrefix, *FullName.ToString(), *FunctionGraph->GetPathName());
			return false;
		}

		FNiagaraVariable Value = ScriptVariable->Variable;
		AssignValue(Value);
		const FNiagaraParameterHandle ModuleParameter(FullName);
		const FNiagaraParameterHandle Aliased = FNiagaraParameterHandle::CreateAliasedModuleParameterHandle(ModuleParameter, &Call);
		UEdGraphPin& Pin = FNiagaraStackGraphUtilities::GetOrCreateStackFunctionInputOverridePin(
			Call, Aliased, Value.GetType(), ScriptVariable->Metadata.GetVariableGuid(), FGuid());
		if (Pin.LinkedTo.Num() > 0)
		{
			UE_LOG(LogTemp, Error, TEXT("%s Refusing linked module input %s on %s"), LogPrefix, *FullName.ToString(), *Call.GetPathName());
			return false;
		}
		FString PinValue;
		const UEdGraphSchema_Niagara* Schema = GetDefault<UEdGraphSchema_Niagara>();
		if (!Schema->TryGetPinDefaultValueFromNiagaraVariable(Value, PinValue)) return false;
		Schema->TrySetDefaultValue(Pin, PinValue);
		return true;
	}

	bool SetFloatInput(UNiagaraNodeFunctionCall& Call, const TCHAR* InputName, const float Number)
	{
		return SetModuleInput(Call, FName(InputName), [Number](FNiagaraVariable& Var) { Var.SetValue<float>(Number); });
	}

	bool SetVec2Input(UNiagaraNodeFunctionCall& Call, const TCHAR* InputName, const FVector2f& Number)
	{
		return SetModuleInput(Call, FName(InputName), [&Number](FNiagaraVariable& Var) { Var.SetValue<FVector2f>(Number); });
	}

	template<typename T>
	bool HasModuleInputValue(UNiagaraNodeFunctionCall& Call, const TCHAR* InputName, const T& Expected)
	{
		UNiagaraScriptSource* FunctionSource = Call.GetFunctionScriptSource();
		UNiagaraGraph* FunctionGraph = FunctionSource ? FunctionSource->NodeGraph : nullptr;
		UNiagaraGraph* OwnerGraph = Call.GetNiagaraGraph();
		UNiagaraScriptVariable* ScriptVariable = FunctionGraph ? FunctionGraph->GetScriptVariable(FName(InputName)) : nullptr;
		if (!ScriptVariable || !OwnerGraph) return false;
		FNiagaraVariable ExpectedVariable = ScriptVariable->Variable;
		ExpectedVariable.SetValue<T>(Expected);
		FString ExpectedText;
		if (!GetDefault<UEdGraphSchema_Niagara>()->TryGetPinDefaultValueFromNiagaraVariable(ExpectedVariable, ExpectedText)) return false;
		const FNiagaraParameterHandle Aliased = FNiagaraParameterHandle::CreateAliasedModuleParameterHandle(FNiagaraParameterHandle(FName(InputName)), &Call);
		for (UEdGraphNode* Node : OwnerGraph->Nodes)
		{
			if (!Node) continue;
			for (UEdGraphPin* Pin : Node->Pins)
			{
				if (Pin && Pin->PinName == Aliased.GetParameterHandleString())
					return Pin->LinkedTo.Num() == 0 && Pin->DefaultValue == ExpectedText;
			}
		}
		return false;
	}

	bool VerifyGraphInput(UNiagaraSystem& System, const TCHAR* EmitterName, const TCHAR* ModulePath, const TCHAR* InputName, const float Expected)
	{
		bool bFound = false;
		for (const FNiagaraEmitterHandle& Handle : System.GetEmitterHandles())
		{
			if (Handle.GetName() != FName(EmitterName)) continue;
			FVersionedNiagaraEmitterData* Data = Handle.GetEmitterData();
			if (!Data) return false;
			TArray<UNiagaraScript*> Scripts;
			Data->GetScripts(Scripts, true, true);
			for (UNiagaraScript* Script : Scripts)
			{
				if (!Script || Script->GetUsage() != ENiagaraScriptUsage::ParticleSpawnScriptInterpolated) continue;
				UNiagaraScriptSource* Source = Cast<UNiagaraScriptSource>(Script->GetLatestSource());
				UNiagaraGraph* Graph = Source ? Source->NodeGraph : nullptr;
				if (!Graph) continue;
				TArray<UNiagaraNodeFunctionCall*> Calls;
				Graph->GetNodesOfClass(Calls);
				for (UNiagaraNodeFunctionCall* Call : Calls)
					if (Call && Call->FunctionScript && Call->FunctionScript->GetPathName().Contains(ModulePath))
					{
						bFound = true;
						if (!HasModuleInputValue<float>(*Call, InputName, Expected)) return false;
					}
			}
		}
		return bFound;
	}

	bool VerifyGraphVec2(UNiagaraSystem& System, const TCHAR* EmitterName, const TCHAR* ModulePath, const TCHAR* InputName, const FVector2f& Expected)
	{
		bool bFound = false;
		for (const FNiagaraEmitterHandle& Handle : System.GetEmitterHandles())
		{
			if (Handle.GetName() != FName(EmitterName)) continue;
			FVersionedNiagaraEmitterData* Data = Handle.GetEmitterData();
			if (!Data) return false;
			TArray<UNiagaraScript*> Scripts;
			Data->GetScripts(Scripts, true, true);
			for (UNiagaraScript* Script : Scripts)
			{
				if (!Script || Script->GetUsage() != ENiagaraScriptUsage::ParticleSpawnScriptInterpolated) continue;
				UNiagaraScriptSource* Source = Cast<UNiagaraScriptSource>(Script->GetLatestSource());
				UNiagaraGraph* Graph = Source ? Source->NodeGraph : nullptr;
				if (!Graph) continue;
				TArray<UNiagaraNodeFunctionCall*> Calls;
				Graph->GetNodesOfClass(Calls);
				for (UNiagaraNodeFunctionCall* Call : Calls)
					if (Call && Call->FunctionScript && Call->FunctionScript->GetPathName().Contains(ModulePath))
					{
						bFound = true;
						if (!HasModuleInputValue<FVector2f>(*Call, InputName, Expected)) return false;
					}
			}
		}
		return bFound;
	}

	bool SetUserFloat(UNiagaraSystem& System, const TCHAR* Name, float Number)
	{
		FNiagaraParameterStore& Store = System.GetExposedParameters();
		TArray<FNiagaraVariable> Variables;
		Store.GetParameters(Variables);
		for (FNiagaraVariable& Variable : Variables)
		{
			if (Variable.GetName() == FName(Name) && Variable.GetType() == FNiagaraTypeDefinition::GetFloatDef())
				return Store.SetParameterValue<float>(Number, Variable, false);
		}
		return false;
	}

	bool SetUserColor(UNiagaraSystem& System, const TCHAR* Name, const FLinearColor& Color)
	{
		FNiagaraParameterStore& Store = System.GetExposedParameters();
		TArray<FNiagaraVariable> Variables;
		Store.GetParameters(Variables);
		for (FNiagaraVariable& Variable : Variables)
		{
			if (Variable.GetName() == FName(Name) && Variable.GetType() == FNiagaraTypeDefinition::GetColorDef())
				return Store.SetParameterValue<FLinearColor>(Color, Variable, false);
		}
		return false;
	}

	bool ReadUserFloat(UNiagaraSystem& System, const TCHAR* Name, float Expected)
	{
		FNiagaraParameterStore& Store = System.GetExposedParameters();
		TArray<FNiagaraVariable> Variables;
		Store.GetParameters(Variables);
		for (const FNiagaraVariable& Variable : Variables)
			if (Variable.GetName() == FName(Name)) return FMath::IsNearlyEqual(Store.GetParameterValue<float>(Variable), Expected);
		return false;
	}

	bool ReadUserColor(UNiagaraSystem& System, const TCHAR* Name, const FLinearColor& Expected)
	{
		FNiagaraParameterStore& Store = System.GetExposedParameters();
		TArray<FNiagaraVariable> Variables;
		Store.GetParameters(Variables);
		for (const FNiagaraVariable& Variable : Variables)
			if (Variable.GetName() == FName(Name)) return Store.GetParameterValue<FLinearColor>(Variable).Equals(Expected, 0.001f);
		return false;
	}

	bool ApplyAuthoredValues(UNiagaraSystem& System)
	{
		bool bSpawn1 = false, bSpawn2 = false, bSizeMax = false, bSizeMin = false, bSize = false;
		for (const FNiagaraEmitterHandle& Handle : System.GetEmitterHandles())
		{
			FVersionedNiagaraEmitterData* Data = Handle.GetEmitterData();
			if (!Data) return false;
			const FString EmitterName = Handle.GetName().ToString();
			if (EmitterName == TEXT("Sparks1"))
			{
				UNiagaraEmitter* EmitterObject = Handle.GetInstance().Emitter;
				if (!EmitterObject || EmitterObject->GetOutermost()->GetName() != DestinationPath) return false;
				Data->CalculateBoundsMode = ENiagaraEmitterCalculateBoundMode::Fixed;
				Data->FixedBounds = FBox(FVector(-175.0), FVector(175.0));
			}
			TArray<UNiagaraScript*> Scripts;
			Data->GetScripts(Scripts, true, true);
			for (UNiagaraScript* Script : Scripts)
			{
				if (!Script || Script->GetUsage() != ENiagaraScriptUsage::ParticleSpawnScriptInterpolated) continue;
				UNiagaraScriptSource* Source = Cast<UNiagaraScriptSource>(Script->GetLatestSource());
				UNiagaraGraph* Graph = Source ? Source->NodeGraph : nullptr;
				if (!Graph) continue;
				TArray<UNiagaraNodeFunctionCall*> Calls;
				Graph->GetNodesOfClass(Calls);
				for (UNiagaraNodeFunctionCall* Call : Calls)
				{
					if (!Call || !Call->FunctionScript) continue;
					const FString FunctionPath = Call->FunctionScript->GetPathName();
					if (FunctionPath.Contains(TEXT("/Emitter/SpawnRate.")))
					{
						if (EmitterName == TEXT("Sparks1")) bSpawn1 |= SetFloatInput(*Call, TEXT("Module.SpawnRate"), 70.0f);
						if (EmitterName == TEXT("Sparks2")) bSpawn2 |= SetFloatInput(*Call, TEXT("Module.SpawnRate"), 52.5f);
					}
					if (EmitterName == TEXT("Sparks1") && FunctionPath.Contains(TEXT("/InitializeParticle.")))
					{
						bSizeMax |= SetVec2Input(*Call, TEXT("Module.Sprite Size Max"), FVector2f(10.0f, 100.0f));
						bSizeMin |= SetVec2Input(*Call, TEXT("Module.Sprite Size Min"), FVector2f(5.0f, 50.0f));
						bSize |= SetVec2Input(*Call, TEXT("Module.Sprite Size"), FVector2f(15.0f, 10.0f));
					}
				}
			}
		}
		if (!(bSpawn1 && bSpawn2 && bSizeMax && bSizeMin && bSize)) return false;
		const bool bUsers =
			SetUserFloat(System, TEXT("User.Scale_All"), 1.25f) &&
			SetUserFloat(System, TEXT("User.Scale_Sparks1"), 1.25f) &&
			SetUserFloat(System, TEXT("User.Scale_Sparks2"), 1.25f) &&
			SetUserColor(System, TEXT("User.Color_Smoke"), FLinearColor(20.0f, 2.8296f, 0.0f, 1.0f)) &&
			SetUserColor(System, TEXT("User.Color_Sparks1"), FLinearColor(200.0f, 29.7466f, 0.0f, 1.0f)) &&
			SetUserColor(System, TEXT("User.Color_Sparks2"), FLinearColor(20.0f, 1.8574f, 0.0f, 1.0f)) &&
			SetUserColor(System, TEXT("User.Color_Spiral1"), FLinearColor(60.0f, 8.3257f, 0.0f, 1.0f));
		return bUsers;
	}
}

UAuraBoostLiteGraphAuthoringCommandlet::UAuraBoostLiteGraphAuthoringCommandlet()
{
	IsEditor = true;
	IsClient = false;
	IsServer = false;
	LogToConsole = true;
}

int32 UAuraBoostLiteGraphAuthoringCommandlet::Main(const FString& Params)
{
	if (!assert_safe_copy_paths()) return 2;
	const bool bUpdate = Params.Contains(TEXT("Update"));
	const bool bWrite = Params.Contains(TEXT("Write")) || bUpdate;
	const bool bVerify = Params.Contains(TEXT("Verify"));
	const TCHAR* AssetPath = (bVerify || bUpdate) ? DestinationPath : SourcePath;
	UNiagaraSystem* System = LoadObject<UNiagaraSystem>(nullptr, AssetPath);
	if (!System) return 3;
	if (!bWrite && !bVerify)
	{
		UE_LOG(LogTemp, Display, TEXT("%s INSPECT_ONLY_COMPLETE asset=%s emitters=%d"), LogPrefix, *System->GetPathName(), System->GetEmitterHandles().Num());
		return 0;
	}

	if (bWrite && !bVerify)
	{
		if (!bUpdate && (FPackageName::DoesPackageExist(DestinationPath) || LoadObject<UNiagaraSystem>(nullptr, DestinationPath)))
		{
			UE_LOG(LogTemp, Error, TEXT("%s Refusing existing destination %s"), LogPrefix, DestinationPath);
			return 4;
		}
		if (!bUpdate)
		{
			FAssetToolsModule& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools"));
			System = Cast<UNiagaraSystem>(AssetTools.Get().DuplicateAsset(TEXT("NS_Boss_PhaseTwoAura_BoostLite_Authored"), TEXT("/Game/OneBossFight/VFX"), System));
			if (!System) return 5;
		}
		if (!ApplyAuthoredValues(*System))
		{
			UE_LOG(LogTemp, Error, TEXT("%s Could not author every requested graph/user value; refusing save"), LogPrefix);
			return 6;
		}
		System->bFixedBounds = true;
		System->SetFixedBounds(FBox(FVector(-175.0), FVector(175.0)));
		System->MarkPackageDirty();
		if (!System->RequestCompile(true, nullptr, nullptr)) return 11;
		System->WaitForCompilationComplete(true, true);
		if (!AllScriptsCompiled(*System)) return 15;
		if (!SaveSystem(System)) return 7;
		UE_LOG(LogTemp, Display, TEXT("%s WRITE_SAVED %s"), LogPrefix, DestinationPath);
		return 0;
	}

	if (!System->RequestCompile(true, nullptr, nullptr)) return 11;
	System->WaitForCompilationComplete(true, true);
	if (!AllScriptsCompiled(*System)) return 15;
	for (const FNiagaraEmitterHandle& Handle : System->GetEmitterHandles())
		UE_LOG(LogTemp, Display, TEXT("%s Emitter=%s Object=%s OuterPackage=%s BoundsMode=%d Bounds=%s..%s"), LogPrefix,
			*Handle.GetName().ToString(), *GetPathNameSafe(Handle.GetInstance().Emitter),
			Handle.GetInstance().Emitter ? *Handle.GetInstance().Emitter->GetOutermost()->GetName() : TEXT("<null>"),
			static_cast<int32>(Handle.GetEmitterData()->CalculateBoundsMode), *Handle.GetEmitterData()->FixedBounds.Min.ToString(), *Handle.GetEmitterData()->FixedBounds.Max.ToString());
	if (!System->bFixedBounds || !System->GetFixedBounds().Min.Equals(FVector(-175.0), 0.01) || !System->GetFixedBounds().Max.Equals(FVector(175.0), 0.01)) return 8;
	bool bSparks1FixedBounds = false;
	for (const FNiagaraEmitterHandle& Handle : System->GetEmitterHandles())
		if (Handle.GetName() == FName(TEXT("Sparks1")))
		{
			const FVersionedNiagaraEmitterData* Data = Handle.GetEmitterData();
			bSparks1FixedBounds = Data && Data->CalculateBoundsMode == ENiagaraEmitterCalculateBoundMode::Fixed &&
				Data->FixedBounds.Min.Equals(FVector(-175.0), 0.01) && Data->FixedBounds.Max.Equals(FVector(175.0), 0.01);
		}
	if (!bSparks1FixedBounds) return 14;
	if (!ReadUserFloat(*System, TEXT("User.Scale_All"), 1.25f) ||
		!ReadUserFloat(*System, TEXT("User.Scale_Sparks1"), 1.25f) ||
		!ReadUserFloat(*System, TEXT("User.Scale_Sparks2"), 1.25f)) return 9;
	if (!ReadUserColor(*System, TEXT("User.Color_Smoke"), FLinearColor(20.0f, 2.8296f, 0.0f, 1.0f)) ||
		!ReadUserColor(*System, TEXT("User.Color_Sparks1"), FLinearColor(200.0f, 29.7466f, 0.0f, 1.0f)) ||
		!ReadUserColor(*System, TEXT("User.Color_Sparks2"), FLinearColor(20.0f, 1.8574f, 0.0f, 1.0f)) ||
		!ReadUserColor(*System, TEXT("User.Color_Spiral1"), FLinearColor(60.0f, 8.3257f, 0.0f, 1.0f))) return 12;
	if (!VerifyGraphInput(*System, TEXT("Sparks1"), TEXT("/Emitter/SpawnRate."), TEXT("Module.SpawnRate"), 70.0f) ||
		!VerifyGraphInput(*System, TEXT("Sparks2"), TEXT("/Emitter/SpawnRate."), TEXT("Module.SpawnRate"), 52.5f) ||
		!VerifyGraphVec2(*System, TEXT("Sparks1"), TEXT("/InitializeParticle."), TEXT("Module.Sprite Size Max"), FVector2f(10.0f, 100.0f)) ||
		!VerifyGraphVec2(*System, TEXT("Sparks1"), TEXT("/InitializeParticle."), TEXT("Module.Sprite Size Min"), FVector2f(5.0f, 50.0f)) ||
		!VerifyGraphVec2(*System, TEXT("Sparks1"), TEXT("/InitializeParticle."), TEXT("Module.Sprite Size"), FVector2f(15.0f, 10.0f))) return 13;
	if (!SaveSystem(System)) return 10;
	UE_LOG(LogTemp, Display, TEXT("%s ROUNDTRIP_PASS %s"), LogPrefix, DestinationPath);
	return 0;
}

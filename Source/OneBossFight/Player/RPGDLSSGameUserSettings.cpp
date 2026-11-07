// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGDLSSGameUserSettings.h"

#include "DLSSLibrary.h"
#include "HAL/IConsoleManager.h"
#include "Player/RPGDLSSPlayerSettingsRules.h"

namespace
{
	UDLSSMode ToPluginMode(ERPGDLSSPlayerMode Mode)
	{
		switch (Mode)
		{
		case ERPGDLSSPlayerMode::DLAA: return UDLSSMode::DLAA;
		case ERPGDLSSPlayerMode::Quality: return UDLSSMode::Quality;
		case ERPGDLSSPlayerMode::Balanced: return UDLSSMode::Balanced;
		case ERPGDLSSPlayerMode::Performance: return UDLSSMode::Performance;
		default: return UDLSSMode::Off;
		}
	}

	RPGDLSSPlayerSettingsRules::EPlayerMode ToRulesMode(ERPGDLSSPlayerMode Mode)
	{
		switch (Mode)
		{
		case ERPGDLSSPlayerMode::DLAA: return RPGDLSSPlayerSettingsRules::EPlayerMode::DLAA;
		case ERPGDLSSPlayerMode::Quality: return RPGDLSSPlayerSettingsRules::EPlayerMode::Quality;
		case ERPGDLSSPlayerMode::Balanced: return RPGDLSSPlayerSettingsRules::EPlayerMode::Balanced;
		case ERPGDLSSPlayerMode::Performance: return RPGDLSSPlayerSettingsRules::EPlayerMode::Performance;
		default: return RPGDLSSPlayerSettingsRules::EPlayerMode::Off;
		}
	}

	UDLSSMode ToPluginMode(RPGDLSSPlayerSettingsRules::ERuntimeMode Mode)
	{
		switch (Mode)
		{
		case RPGDLSSPlayerSettingsRules::ERuntimeMode::DLAA: return UDLSSMode::DLAA;
		case RPGDLSSPlayerSettingsRules::ERuntimeMode::Quality: return UDLSSMode::Quality;
		case RPGDLSSPlayerSettingsRules::ERuntimeMode::Balanced: return UDLSSMode::Balanced;
		case RPGDLSSPlayerSettingsRules::ERuntimeMode::Performance: return UDLSSMode::Performance;
		default: return UDLSSMode::Off;
		}
	}

	void SelectTSRFallback()
	{
		// EAntiAliasingMethod::AAM_TSR is 2 in UE 5.5. This is an internal game-setting CVar write, not a console command.
		if (IConsoleVariable* AntiAliasing = IConsoleManager::Get().FindConsoleVariable(TEXT("r.AntiAliasingMethod")))
		{
			AntiAliasing->Set(2, ECVF_SetByGameSetting);
		}
	}
}

void URPGDLSSGameUserSettings::SetDLSSPlayerMode(ERPGDLSSPlayerMode NewMode)
{
	DLSSPlayerMode = NewMode;
	ApplyDLSSPlayerMode();
	SaveSettings();
}

void URPGDLSSGameUserSettings::ApplySettings(bool bCheckForCommandLineOverrides)
{
	Super::ApplySettings(bCheckForCommandLineOverrides);
	ApplyDLSSPlayerMode();
}

void URPGDLSSGameUserSettings::ApplyDLSSPlayerMode()
{
	const UDLSSMode Requested = ToPluginMode(DLSSPlayerMode);
	const bool bRequestedSupported = DLSSPlayerMode != ERPGDLSSPlayerMode::Off &&
		UDLSSLibrary::IsDLSSSupported() && UDLSSLibrary::IsDLSSModeSupported(Requested);
	const RPGDLSSPlayerSettingsRules::ERuntimeMode RuntimeMode = RPGDLSSPlayerSettingsRules::Resolve(ToRulesMode(DLSSPlayerMode), bRequestedSupported);

	// An unsupported saved preference remains saved, so it can apply again on a supported machine.
	if (RuntimeMode == RPGDLSSPlayerSettingsRules::ERuntimeMode::TSR)
	{
		UDLSSLibrary::SetDLSSMode(nullptr, UDLSSMode::Off);
		SelectTSRFallback();
		return;
	}

	UDLSSLibrary::SetDLSSMode(nullptr, ToPluginMode(RuntimeMode));
}

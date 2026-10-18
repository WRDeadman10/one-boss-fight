// Copyright One Boss Fight. All Rights Reserved.

using UnrealBuildTool;
using System.Collections.Generic;

public class OneBossFightTarget : TargetRules
{
	public OneBossFightTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_5;
		ExtraModuleNames.Add("OneBossFight");
	}
}

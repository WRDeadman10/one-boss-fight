// Copyright One Boss Fight. All Rights Reserved.

using UnrealBuildTool;
using System.Collections.Generic;

public class OneBossFightEditorTarget : TargetRules
{
	public OneBossFightEditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_5;
		ExtraModuleNames.Add("OneBossFight");
	}
}

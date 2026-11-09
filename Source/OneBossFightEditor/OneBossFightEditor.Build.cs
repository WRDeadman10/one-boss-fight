using UnrealBuildTool;

public class OneBossFightEditor : ModuleRules
{
	public OneBossFightEditor(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"OneBossFight",
			"AssetRegistry",
			"UnrealEd",
			"Niagara",
			"NiagaraEditor",
			"AssetTools"
		});
	}
}

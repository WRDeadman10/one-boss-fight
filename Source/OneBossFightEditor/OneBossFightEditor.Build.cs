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
			"UnrealEd",
			"Niagara",
			"NiagaraEditor",
			"AssetTools"
		});
	}
}

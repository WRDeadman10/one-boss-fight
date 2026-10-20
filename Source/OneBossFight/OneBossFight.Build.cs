// Copyright One Boss Fight. All Rights Reserved.

using UnrealBuildTool;

public class OneBossFight : ModuleRules
{
	public OneBossFight(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		// Headers live in feature folders (Arena/, Boss/, Pack/, ...) and are included as "Folder/File.h".
		PublicIncludePaths.Add(ModuleDirectory);

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"GameplayTags",
			"AIModule",
			"GameplayTasks",
			"UMG",
			"Slate",
			"SlateCore",
			"Niagara"                  // the spawn-effect notify (Sevarog shockwave)
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Json",
			"AssetRegistry", // content wiring test: dependencies of the pack assets
			"RenderCore", // game/render thread timings for the benchmark
			"RHI"         // GPU frame time for the benchmark
		});

		// Editor-only authoring helpers (skeleton sockets, montage slots).
		if (Target.bBuildEditor)
		{
			PrivateDependencyModuleNames.AddRange(new string[]
			{
				"UnrealEd"
			});
		}
	}
}

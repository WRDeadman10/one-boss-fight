// Copyright One Boss Fight. All Rights Reserved.

using UnrealBuildTool;

public class OneBossFight : ModuleRules
{
	public OneBossFight(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		// Headers live in feature folders (Characters/, Arena/, ...) and are included as "Folder/File.h".
		PublicIncludePaths.Add(ModuleDirectory);

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput"
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Json",
			"RenderCore", // game/render thread timings for the benchmark
			"RHI"         // GPU frame time for the benchmark
		});
	}
}

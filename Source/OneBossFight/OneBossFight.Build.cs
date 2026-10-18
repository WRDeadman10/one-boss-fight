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
			"EnhancedInput",
			"GameplayTags",
			"AIModule",                // UBrainComponent (base of UStateTreeComponent)
			"GameplayTasks",
			"StateTreeModule",         // boss state tree tasks and conditions
			"GameplayStateTreeModule"  // UStateTreeComponent
		});

		PrivateDependencyModuleNames.AddRange(new string[]
		{
			"Json",
			"RenderCore", // game/render thread timings for the benchmark
			"RHI"         // GPU frame time for the benchmark
		});

		// Authoring helper that builds the boss StateTree asset (editor builds only).
		if (Target.bBuildEditor)
		{
			PrivateDependencyModuleNames.AddRange(new string[]
			{
				"UnrealEd",
				"StateTreeEditorModule"
			});
		}
	}
}

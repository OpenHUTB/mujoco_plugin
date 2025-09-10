// Copyright Epic Games, Inc. All Rights Reserved.
using System;
using System.IO;
using UnrealBuildTool;

public class MuJoCoUE : ModuleRules
{
	public MuJoCoUE(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicIncludePaths.AddRange(
			new string[] {
				// ... add public include paths required here ...
			}
			);


		PrivateIncludePaths.AddRange(
			new string[] {
				// ... add other private include paths required here ...
			}
			);


		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core", "ProceduralMeshComponent",
                "MeshDescription",
                "StaticMeshDescription",
                "MeshConversion",
				// solve link error: FMeshDescription::~FMeshDescription(void)
				// ... add other public dependencies that you statically link with here ...
			}
            );


		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				"Projects", 
				// ... add private dependencies that you statically link with here ...	
			}
			);


		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
				// ... add any modules that your module loads dynamically here ...
			}
			);


		string MUJOCO_ROOT = Path.GetFullPath(Path.Combine(ModuleDirectory, "../../Source/mujoco/"));
		string MUJOCO_INCLUDE_PATH = Path.Combine(MUJOCO_ROOT, "include/");
		PublicIncludePaths.Add(MUJOCO_INCLUDE_PATH);

		// Find the 3rd Party DLL

		//if (Target.Platform == UnrealTargetPlatform.Win64 || Target.Platform == UnrealTargetPlatform.Win32)
		//{
		//	string SDLPlatformPrefix = Target.Platform == UnrealTargetPlatform.Win64 ? "x64" : "x86";
		string UE4PlatformPrefix = Target.Platform == UnrealTargetPlatform.Win64 ? "Win64" : "Win32";

		string MujocoBinDirectory = Path.Combine(MUJOCO_ROOT, "lib");
		string UE4BinDirectory = Path.Combine(PluginDirectory, "Binaries", UE4PlatformPrefix);

		PublicAdditionalLibraries.Add(Path.Combine(MujocoBinDirectory, "mujoco.lib"));
		string DLLTargetPath = Path.Combine(UE4BinDirectory, "mujoco.dll");

		string DLLSourcePath = Path.Combine(Path.Combine(MUJOCO_ROOT, "bin"), "mujoco.dll");

		// Copy the SDL2 dll if it doesn't exist
		if (!File.Exists(DLLTargetPath))
		{
			Console.WriteLine("[SDL2InputDevice] Copy " + DLLSourcePath + " -> " + DLLTargetPath);
			File.Copy(DLLSourcePath, DLLTargetPath, false);
		}

		RuntimeDependencies.Add(DLLTargetPath);     // Add a dependancy on the DLL
		PublicDelayLoadDLLs.Add("mujoco.DLL");
	}
}

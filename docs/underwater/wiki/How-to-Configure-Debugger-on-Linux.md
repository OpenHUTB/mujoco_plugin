## CLion

#### 1. Create CLion project files
- Open Holodeck in Unreal Engine
- Edit -> Editor Preferences -> General -> Source Code -> Source Code Editor -> CLion
- File -> Generate CLion Project (this will be "Refresh CLion Project"  if the project was already generated)

#### 2. Open the project in CLion
Open the project from the project root in CLion or in Unreal Engine Editor goto File -> Open CLion

#### 3. Edit the configurations
**Note:** You need to copy libopenvr_api.so from `{where you cloned ue4}/UnrealEngine/Engine/Binaries/ThirdParty/OpenVR/OpenVRv1_0_16/linux64` to `holodeck-engine/Binaries/Linux` to be able to run/debug the game following these instructions.
- In CLion goto Run -> Edit Configurations (also available in the run section of the toolbar)
- Select Holodeck-Linux-DebugGame
- Set the value in `Executable` to {HOLODECK-ENGINE-ROOT}/Binaries/Linux/Holodeck-Linux-DebugGame
- Leave 'Program arguments` blank. Alternatively, you can specify the map/world to load e.g `TestWorld`
- Click OK
- Use the debug icon to debug the game or press `Shift + F9`

#### 4. Run Holodeck in debug mode
After the setup, you should be able to click on Run -> Debug <configuration_name>, click on the debug icon on the top right corner of the toolbar or simply use Shift + F9 to debug Holodeck. 

> Note: This will build the project and open Unreal Engine in debug mode. Running Holodeck in Unreal Engine should hit any reachable breakpoints you set.

## VSCode
#### 1. Create VSCode project files
- Open Holodeck in Unreal Engine
- Edit -> Editor Preferences -> General -> Source Code -> Source Code Editor -> VSCode
- File -> Generate VSCode Project (this will be "Refresh VSCode Project"  if the project was already generated)

#### 2. Open the project in VSCode
Open the workspace from the project root in VSCode

#### 3. Copy missing library
Copy `libopenvr_api.so` from `{where you cloned ue4}/UnrealEngine/Engine/Binaries/ThirdParty/OpenVR/OpenVRv1_0_16/linux64` to `holodeck-engine/Binaries/Linux`

#### 4. Run
F5 to debug, Ctrl + Shift + B to build 

## Command line
#### 1. Build from the command line:
`{UnrealEngineDir}/Engine/Build/BatchFiles/Linux/Build.sh holodeck Linux {BuildConfiguration} {HolodeckEngineDir}/Holodeck.uproject -waitmutex`


`ExecutableName` can be anything. The resulting executable will have this name. Typically would be Holodeck-{BuildConfiguration}. E.g. Holodeck-Debug. If you get a couldn't find target rules error just use "holodeck"

`BuildConfiguration` must be one of:
- `Debug`: Includes symbols for debugging both the engine and the game
- `DebugGame`: the engine is optimized but the game's debug symbols are included so the game is debuggable
- `Development`: enables all but the most time-consuming optimizations
- `Shipping`: well, optimize the game and engine code
- `Test`: same as shipping but with some console commands, stats, and profiling tools enabled


#### 2. Run the game from the command line:
`{HolodeckEngineDir}/Build/Linux}/{TargetName}-{Linux}-{BuildConfiguration}`

> Note: You may need to cook the project for Linux else you'd get some kind of "uncooked" game error. To cook the game for Linux, open the game in UnrealEditor click File -> Cook Content -> [PlatformName] or File -> Cook Content for Linux.

#### 3. Attach a debugger to the process:
You can use your debugger of choice to attach to the game's running process

#### Links to helpful Unreal Engine docs:

[Packaging Projects](https://docs.unrealengine.com/en-US/Engine/Basics/Projects/Packaging/index.html)

[Build configuration](https://docs.unrealengine.com/en-US/Programming/Development/CompilingProjects/index.html)
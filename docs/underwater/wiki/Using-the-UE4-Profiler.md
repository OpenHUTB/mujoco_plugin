UE4 ships with a useful [profiler](https://docs.unrealengine.com/en-us/Engine/Performance/Profiler) in the "Session Frontend" utility. By adding some macros to the Holodeck Engine source, you can easily measure the performance impact of a section of code.

## Add the Macros
In the header file for the class you want to profile, you need to declare a group for your new stat and the stat itself:

`RenderRequest.h:`
```cpp
DECLARE_STATS_GROUP(TEXT("RenderRequest"), STATGROUP_RenderRequest, STATCAT_Advanced);
DECLARE_CYCLE_STAT_EXTERN(TEXT("CameraExecuteTask"), STAT_CameraExecuteTask, STATGROUP_RenderRequest, );
```
The third option of the `DECLARE_STATS_GROUP` macro must always be `STATCAT_Advanced`, but the other two paramaters can be changed. The second paramater is the name of the variable the macro will create, and convention is to name it `STATGROUP_*`.

Next, in the implementation of  your header file
`RenderRequest.cpp`
```cpp
DEFINE_STAT(STAT_CameraExecuteTask);

void FRenderRequest::ExecuteTask()
{
    SCOPE_CYCLE_COUNTER(STAT_CameraExecuteTask);
    // ...
}
```
Note that with creative use of braces you can scope the cycle counter anywhere you want, eg
```cpp
void FRenderRequest::ExecuteTask()
{
    {
        SCOPE_CYCLE_COUNTER(STAT_Thing1);
        do_thing_1()
    }
    {
        SCOPE_CYCLE_COUNTER(STAT_Thing2);
        do_thing_2()
    }
}
```
Make sure everything builds. To use the profiler you will need to be running a debug build of the engine.
## Attach the session frontend
You will need to enable messaging in UE4 and then attach the session frontend to your instance of Holodeck.

### Enable Messaging
You just need to add the `-messaging` command line option to however you invoke the engine. 

If you want to run Holodeck from Visual Studio, right click on the Holodeck project -> Properties -> Debugging -> Edit "Command Arguments" and add `-messaging` to the end

You can also modify the `__windows_start_process__` method in `environments.py` to add `-messaging`.

Start Holodeck and attach the python portion so the game is ticking as normal.

### Launch the Frontend and Attach
Open the `holodeck.uproject` file in the Unreal Editor.
Window -> Developer Tools -> Session Frontend

You should see your instance of Holodeck in the left hand column under "My Sessions" -> Unnamed. Don't select the 
editor, select the instance of type "Game". Click on it to connect and then select the "Profiler" tab. 

You can now select Data Preview and Data Capture to begin loading data. Deselect Data Capture and use the search boxes to search for your new stat, you can have the Profiler plot it's execution time with the overall frame time. The "FPS Chart" gives a useful representation of framerates as well.

Example of captured data:
[[images/session-frontend.png]]
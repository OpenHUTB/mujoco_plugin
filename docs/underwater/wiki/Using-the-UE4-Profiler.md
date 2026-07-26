# UE4性能分析（提升性能）

UE4 自带一个实用的[性能分析器](https://openhutb.github.io/engine_doc/zh-CN/TestingAndOptimization/PerformanceAndProfiling/index.html)，名为“Session Frontend”。通过向 Holodeck 引擎源代码添加一些宏，您可以轻松地测量一段代码的性能影响。

## 添加宏

在要进行性能分析的类的头文件中，需要为你的新统计信息声明一个组以及统计信息本身：

[RenderRequest.h](https://github.com/OpenHUTB/Underwater/tree/master/Source/Holodeck/General/Public/RenderRequest.h):
```cpp
DECLARE_STATS_GROUP(TEXT("RenderRequest"), STATGROUP_RenderRequest, STATCAT_Advanced);
DECLARE_CYCLE_STAT_EXTERN(TEXT("CameraExecuteTask"), STAT_CameraExecuteTask, STATGROUP_RenderRequest, );
```

`DECLARE_STATS_GROUP` 宏的第三个选项必须始终为 `STATCAT_Advanced`，但其他两个参数可以更改。第二个参数是宏将创建的变量的名称，约定将其命名为 `STATGROUP_*`。

接下来，在您的头文件 [RenderRequest.cpp](https://github.com/OpenHUTB/Underwater/blob/master/Source/Holodeck/General/Private/RenderRequest.cpp) 的实现中。

```cpp
DEFINE_STAT(STAT_CameraExecuteTask);

void FRenderRequest::ExecuteTask()
{
    SCOPE_CYCLE_COUNTER(STAT_CameraExecuteTask);
    // ...
}
```
请注意，通过巧妙地使用花括号，您可以将循环计数器的范围限定在您想要的任何位置，例如
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
确保所有组件都能成功构建。要使用性能分析器，您需要运行引擎的调试版本。

## 附加会话前端
您需要在 UE4 中启用消息传递，然后将会话前端附加到您的 Holodeck 实例。

### 启用消息传递
您只需在调用引擎的任何命令中添加 `-messaging` 命令行选项即可。

如果您想从 Visual Studio 运行 Holodeck，请右键单击 Holodeck 项目 -> 属性 -> 调试 -> 编辑“命令参数”，并在末尾添加 `-messaging`。

您也可以修改 `environments.py` 文件中的 `__windows_start_process__` 方法来添加 `-messaging`。

启动 Holodeck 并附加 Python 部分，以便游戏正常运行。

### 启动前端并附加

在虚幻引擎编辑器中打开 `holodeck.uproject` 文件。依次点击“窗口”->“开发者工具”->“会话前端”。

您应该会在左侧“我的会话”->“未命名”下方看到您的 Holodeck 实例。不要选择编辑器，而是选择类型为“游戏”的实例。点击它进行连接，然后选择“性能分析器”选项卡。

现在您可以选择“数据预览”和“数据捕获”来开始加载数据。取消选择“数据捕获”，然后使用搜索框搜索您的新统计数据。您可以让性能分析器绘制其执行时间和总帧时间的图表。“FPS 图表”也提供了帧率的有用表示。

捕获数据示例：
[[images/session-frontend.png]]
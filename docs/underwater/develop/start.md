# 入门指南

虽然可以在 Linux 上进行引擎开发，但我发现使用 Windows 会更简单、更稳定。无论选择哪个平台，都需要安装以下依赖项：

* [引擎定制版](https://github.com/OpenHUTB/engine)

* [Visual Studio 2019](https://visualstudio.microsoft.com/vs/older-downloads/)（具体设置请参阅[引擎文档](https://openhutb.github.io/engine_doc/zh-CN/index.html)）

* git

* Python 环境（推荐使用 conda）

## 克隆代码 <span id="cloning"></span>

若要运行 HoloOcean Live，你需要配置 HoloOcean 的 C++ 和 Python 部分；目前这两部分已整合在同一个代码仓库中，操作更为便捷。

* 克隆 [Underwater](https://github.com/OpenHUTB/Underwater) 仓库。

* 进入克隆后的目录。

* 切换到你想要开发的分支，通常是 develop 分支，你可以通过 `git checkout develop` 命令访问该分支。

    * 或者，你也可以创建一个新的分支来添加新功能，命令是 `git checkout -b [你的分支名称] [你要从中创建分支的分支名称]`。

现在可以通过运行 `pip install -e client/` 来安装 python 包。


## 打开和准备项目 <span id="opening_prepping_project"></span>

在克隆的仓库的引擎目录中，你会找到一个名为 holodeck.uproject 的文件。双击该文件，如果弹出引擎版本对话框，请选择“4.26”。对于任何提示“是否立即重新构建？”的对话框，请点击“是”。之后，虚幻引擎应该就会打开！

虚幻引擎的开发方式有很多种，但我们将重点介绍我发现的最简便的开发方法。

在虚幻编辑器中，依次点击“File”->“Cook Content for {Platform}”。几分钟后，你应该会在右下角看到一个成功弹出窗口。


## 设置 VSCode <span id="setting_up_vscode"></span>

也可以使用 Visual Studio IDE，这里介绍使用 VSCode。如果您已经安装了 VSCode，并且也想这样做，请按以下步骤操作：

* 在 Unreal 编辑器中，依次点击“编辑”->“编辑器首选项”

* 然后依次点击“常规”->“源代码”->“源代码编辑器”，并选择“Visual Studio Code”

* 完成上述步骤后，您应该可以使用“文件”->“生成 Visual Studio Code 项目”来创建一个新的 Visual Studio Code 项目。

* 要打开 Visual Studio Code，请依次点击“文件”->“打开 Visual Studio Code”。


## 编译  <span id="compiling"></span>

通常通过点击虚幻编辑器中的“编译”按钮进行编译。每次修改代码后都需要执行此操作。当然，您也可以在 Visual Studio 中进行编译。

“编译”按钮位于顶部工具栏，在“过场动画”和“构建”按钮旁边。如果您的屏幕不够宽，该按钮可能会被隐藏。点击双箭头向右滚动即可找到它。


## 启动游戏  <span id="launching_game_live"></span>

为了避免每次想要查看代码更改时都需要打包项目，您可以直接在虚幻编辑器中运行游戏，然后将您的 Python 代码附加到游戏中。这是一个多步骤的过程，具体如下。


!!! 注意
    如果要开发声呐模块，请在UE4中点击顶部工具栏“播放”按钮旁边的向下箭头，然后点击“高级设置”。将以下代码添加到“附加启动参数”中。
    
    `-EnvMinX=-1000 -EnvMinY=-1000 -EnvMinZ=-1000 -EnvMaxX=1000 -EnvMaxY=1000 -EnvMinZ=1000 -OctreeMin=0.02 OctreeMax=5`

    这些单位都是米。您可以根据需要进行调整，它们的含义都很容易理解。

!!! 注意
    如果您使用动态传感器，或者期望特定的每秒帧数 (tick per second)，请确保将 `-TicksPerSec=<val>` 设置为以下参数之一，以便获得您期望的模拟速率和行为。`-FramesPerSec=<val>` 命令控制程序在您计算机上的运行速度。请参阅 https://byu-holoocean.github.io/holoocean-docs/v1.0.0/usage/scenarios.html#frame-rates。此外，`-log` 参数可用于轻松关闭游戏窗口，以及查看日志消息以进行调试。

打开并准备一个类似于以下内容的 Python 脚本

```python
import holoocean

config = {
      "name": "test",
      "world": "ExampleLevel",
      "main_agent": "auv0",
      "agents": [
            {
               "agent_name": "auv0",
               "agent_type": "HoveringAUV",
               "sensors": [
                  {
                        "sensor_type": "LocationSensor",
                  }
               ],
               "control_scheme": 1,
               "location": [0, 0, 1]
            }
      ]
   }

command = [0, 0, 0, 0, 0, 0, 0, 0]
with holoocean.make(scenario_cfg=config, start_world=False) as env:
   for _ in range(1000):
      state, reward = env.step(command)
```

根据需要调整脚本，添加所需的传感器/代理。

* 确保打开并准备好运行此 Python 文件。

* 返回虚幻编辑器，点击顶部工具栏“运行”按钮旁边的箭头，然后选择“独立游戏”。此时会弹出一个单独的窗口，显示虚幻游戏。

* 窗口弹出后，运行你的 Python 脚本。脚本会附加到新打开的虚幻游戏窗口，并像正常的 HoloOcean 模拟一样运行。注意，你可能需要尝试运行几次脚本，因为虚幻游戏窗口需要一些时间加载。

完成！这里还有一些需要注意的小问题。如果在退出 Python 脚本之前关闭虚幻游戏窗口，终端会冻结，你需要重新打开一个终端。我有一个固定到任务栏的 .bat 脚本来运行 Python 文件，以解决这个问题。此外，VSCode 的播放按钮也能流畅地快速打开/关闭具有正确 conda 环境的终端。


## 日志记录  <span id="logging"></span>

虽然这绝对不是最佳方法，但我通常使用虚幻引擎中与 print 语句等效的功能来调试代码。[这里](https://unrealcommunity.wiki/logging-lgpidy6i)有一个关于如何将信息发送到虚幻引擎日志的优秀教程。

如果您想稍后查看，此日志将保存在 holoocean-engine/Saved/Logs 目录中。或者，我更喜欢这种方式。在虚幻编辑器中，

* 转到“窗口”->“开发者工具”->“会话前端”

* 在“我的会话”下，您的虚幻游戏窗口将有一个条目，其中列出了所有日志。

非常简单！

有关开发自定义传感器/代理/环境以及如何入门的信息，请参阅[开发代理](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/develop/agents.html#develop-agents)、[开发传感器](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/develop/sensors.html#develop-sensor)和[开发环境](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/develop/env.html#develop-env)。

要开发自定义声呐，请参阅 [HolodeckSonar.h](https://github.com/OpenHUTB/Underwater/blob/master/Source/Holodeck/HolodeckCore/Public/HolodeckSonar.h) 和 [HolodeckSonar.cpp](https://github.com/OpenHUTB/Underwater/blob/master/Source/Holodeck/HolodeckCore/Private/HolodeckSonar.cpp) 文件以获取所需的超类，并参阅 [ImagingSonar.h](https://github.com/OpenHUTB/Underwater/blob/master/Source/Holodeck/Sensors/Public/ImagingSonar.h) 和 [ImagingSonar.cpp](https://github.com/OpenHUTB/Underwater/blob/master/Source/Holodeck/Sensors/Private/ImagingSonar.cpp) 以获取如何使用它们的示例。

## 代码格式化  <span id="code_formatting"></span>

如果您要提交修改 C++ 或 Python 代码的 pull request，请确保您的代码格式正确。Python 代码应使用 [ruff](https://docs.astral.sh/ruff/) 进行格式化，C++ 代码应使用提供的 clang-format 配置进行格式化，并遵循 UE 风格指南。要格式化 C++ 代码，您可以从 engine/ue5-clang-format-file 运行以下命令：
```shell
find ../Source -iname "*.h" -o -iname "*.cpp" | xargs clang-format -style=file -i
```

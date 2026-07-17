# 水下机器人 HoloOcean

文档请查看[UE4.27归档版](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/index.html) ，文档的源码位于[27_archival_develop目录](https://github.com/byu-holoocean/holoocean-docs/tree/main/UE4.27_archival_develop)。

## 运行

Windows: https://robots.et.byu.edu/holo/Ocean/v1.0.0/Windows.zip

Installing Ocean ver. 0.1.0 from https://robots.et.byu.edu/holo/Ocean/v0.1.0/Linux.zip


## 编译

把引擎移出，调整引擎的版本为现有引擎版本

* 报错：Missing Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.exe after build

    解决：

    ```shell
    "D:\hutb\Build\engine\Engine\Build\BatchFiles\GenerateProjectFiles.bat" -project="D:\hutb\Unreal\CarlaUE4\Plugins\Underwater\Holodeck.uproject" -game -progress
    ```


通过VS进行启动，启动画面为：
![](../img/underwater/launch.jpg)

启动到92%报错：“打开地图文件失败。可能是因为该地图使用了较新版本的引擎进行保存。”

没有在内容浏览器中显示的资产：`Underwater\Content\HolodeckContent\Agents\NavAgent\NavAgentBlueprint.uasset`、`Underwater\Content\HolodeckContent\Agents\AgentSpectatorPawn.uasset`、`Underwater\Content\HolodeckContent\Agents\SphereRobot_Blueprint.uasset`

资产``Underwater\Content\HolodeckContent\Agents\AgentFollower.uasset`打开编译报错。


可以打开相关的资产：
![](../img/underwater/HoveringAUVMesh.png)


## 参考文档

* [holoocean-v1.0.0](https://byu-holoocean.github.io/holoocean-docs/v1.0.0)
* [所有版本的文档](https://byu-holoocean.github.io/holoocean-docs/versionList.html)
* [构建后缺少 UnrealBuildTool.exe](https://forums.unrealengine.com/t/missing-unrealbuildtool-exe-after-build/2674046/2)
# Mujoco 插件文档

该项目用于管理 hutb 模拟器的 [Mujoco 插件文档](https://openhutb.github.io/mujoco_plugin/)，包含准备导入 mujoco 插件的模型验证代码和文档（包括[肌肉骨骼人](https://openhutb.github.io/mujoco_plugin/ms/human_700/)、[人形机器人](https://openhutb.github.io/mujoco_plugin/humanoid/g1/)、[水下机器人](https://openhutb.github.io/mujoco_plugin/underwater/)、[机器狗](https://openhutb.github.io/mujoco_plugin/go2/)等）、[插件实现](https://openhutb.github.io/mujoco_plugin/#implementation)、[插件开发](https://openhutb.github.io/mujoco_plugin/#dev)等。

![](https://openhutb.github.io/mujoco_plugin/img/humanoid/hutb_demo.png)

**注意**：该仓库后面只用于储存[Mujoco 使用和其插件文档（docs文件夹）](https://github.com/OpenHUTB/mujoco_plugin/tree/main/docs)和[相应测试的 Python 代码（src文件夹）](https://github.com/OpenHUTB/mujoco_plugin/tree/main/src)，原有的插件示例代码（包括 [Config](https://github.com/OpenHUTB/mujoco_plugin/tree/main/Config)、[Content](https://github.com/OpenHUTB/mujoco_plugin/tree/main/Content)、[Plugins](https://github.com/OpenHUTB/mujoco_plugin/tree/main/Plugins)、[Source](https://github.com/OpenHUTB/mujoco_plugin/tree/main/Source)文件夹、[自述文件](./docs/deprecated.md)）将会在功能更完善的 Mujoco 插件（[UnrealRoboticsLab](https://github.com/OpenHUTB/hutb/tree/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab)）完全测试通过后移除。


### 适配 hutb 模拟器

UnrealRoboticsLab 插件的[适配细节](https://openhutb.github.io/mujoco_plugin/dev/ue4/)。


## 参考

* [MuJoCo-Unreal-Engine-Plugin](https://github.com/oneclicklabs/MuJoCo-Unreal-Engine-Plugin)
* [Unreal_Mujoco](https://github.com/miaobeihai/Unreal_Mujoco)
* [mujoco-unreal-plugin](https://github.com/carTloyal123/mujoco-unreal-plugin)
* [无人机模型](https://github.com/google-deepmind/mujoco_menagerie) - [Skydio X2](https://github.com/google-deepmind/mujoco_menagerie/tree/main/skydio_x2) 、[Crazyflie 2](https://github.com/google-deepmind/mujoco_menagerie/tree/main/bitcraze_crazyflie_2)
* [Unity 的 Mujoco 插件](./docs/unity.md)
* [UnrealRoboticsLab](https://github.com/URLab-Sim/UnrealRoboticsLab)







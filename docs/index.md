title: 主页

# [Mujoco 插件](https://github.com/OpenHUTB/mujoco_plugin)

欢迎使用 Mujoco 插件文档，该页面包含所有内容的索引。


* [__mujoco 插件实现__](#implementation)  
    * [插件指南](#guide)
    * [肌肉骨骼人](#ms)
    * [人形机器人](#humanoid)
    * [水下机器人](#other)
* [__引擎插件开发__](#dev)

---



# mujoco 插件实现 <span id="implementation"></span>

<!-- 更新至：Truncate test log up-front in build+test scripts
https://github.com/donghaiwang/UnrealRoboticsLab/commit/51cce72a014a42612125ea6bef5a5494e4f94c5d -->

虚幻机器人实验室 (Unreal Robotics Lab, URLab) 虚幻引擎插件将 [MuJoCo](https://github.com/google-deepmind/mujoco) 物理引擎直接嵌入到编辑器和运行时中。

该插件提供研究级的接触动力学功能，并兼容虚幻引擎的渲染、蓝图脚本和编辑器工具。您可以从 MJCF XML 文件导入机器人（或在组件层级结构中创建机器人），点击“运行”按钮，MuJoCo 会在专用线程上处理物理效果，而虚幻引擎则负责所有视觉效果。


![](./img/hero.png)

---

## 插件指南  <span id="guide"></span>

| 指南 | 涵盖的内容 |
|-------|---------------|
| [介绍](paper.md) | 理论说明 |
| [入门](getting_started.md) | 安装、首次模拟、控制方法 |
| [特性](features.md) | 完整特性参考 |
| [MJCF 导入](guides/mujoco_import.md) | 将 MuJoCo XML 模型导入虚幻引擎 |
| [URLab 编辑器](./dev/URLabEditor.md) | URLab 的编辑器模块 |
| [几何体与碰撞](guides/geometry_authoring.md) | 图元、网格几何体、快速转换、高度场 |
| [控制器框架](guides/controller_framework.md) | PD、关键帧和自定义控制器 |
| [调试可视化](guides/debug_visualization.md) | 快捷键驱动的叠加层：接触点、关节、岛状结构、分割、肌肉 |
| [交互式扰动](guides/perturbation.md) | 鼠标驱动的身体拖动：选择、平移、旋转——模拟兼容的手势 |
| [持有和扭转控制](guides/possession_twist.md) | WASD控制，弹簧臂摄像头 |
| [使用蓝图编写脚本](guides/blueprint_reference.md) | 快捷键、API 使用、脚本工作流程 |
| [ZMQ 网络与 ROS 2](guides/zmq_networking.md) | ZMQ 传输、主题、摄像头流媒体 |
| [URLab 桥接](guides/policy_bridge.md) | Python 中间件、强化学习策略、远程控制 |
| [架构](architecture.md) | 子系统设计、线程模型、编译流程 |
| [适配 hutb](./dev/ue4.md) | 迁移到 UE4，[适配 hutb 模拟器](https://github.com/OpenHUTB/hutb) |
| [自动化测试](./dev/testing.md) | 各种插件功能的测试 |

---

## 肌肉骨骼人 <span id="ms"></span>

| 指南 | 涵盖的内容 |
|-------|---------------|
| [肌肉骨骼人模型](./ms/human_700.md) | 全身肌肉骨骼模型参考模型 |


## 人形机器人 <span id="humanoid"></span>

| 指南 | 涵盖的内容 |
|-------|---------------|
| [人形机器人模型](./humanoid/g1.md) | 人形机器人参考模型 |

## 水下机器人 <span id="other"></span>

| 指南 | 涵盖的内容 |
|-------|---------------|
| [水下机器人](./underwater/index.md) | 高保真的水下机器人插件 |
| [HoloOcean](./underwater/holoocean_paper.md) | HoloOcean 的理论介绍 |
| [机器狗](./go2.md) | 仿生四足机器人 Go2 |

---

# 引擎插件开发 <span id="dev"></span>

[__引擎插件开发入门__](introduction.md) — 引擎插件开发的环境配置



--- 
## API 参考

[API参考文档](api/index.md) 会在每次构建时根据 C++ 头文件自动生成。它涵盖了插件中的每个类、结构体和枚举。


---

# 参考

## 第三方软件

| 库 | 许可证 | 角色 |
|---------|---------|------|
| [MuJoCo](https://github.com/google-deepmind/mujoco) | Apache 2.0 | 物理模拟引擎 |
| [CoACD](https://github.com/SarahWeiii/CoACD) | MIT | 凸近似分解（Convex approximate decomposition, CoACD）|
| [libzmq](https://zeromq.org) | MPL 2.0 | 高性能消息传递，即**零开销消息队列**（Zero cost Message Queue, ZMQ），是一个无代理、点对点的高性能异步消息传递库 |

## 引用

* [deepwiki](https://deepwiki.com/URLab-Sim/UnrealRoboticsLab/)


如果对文档中的任何问题可以在 [本文档的源码仓库](https://github.com/OpenHUTB/mujoco_plugin) 中的 [问题](https://github.com/OpenHUTB/mujoco_plugin/issues) 页面讨论或者提交 [拉取请求](https://zhuanlan.zhihu.com/p/153381521) 直接修改文档。
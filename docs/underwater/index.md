# 水下机器人 HoloOcean

HoloOcean[@Potokar22icra] 基于虚幻引擎和全息舱开发，能够轻松模拟海洋机器人与自主系统，支持多种传感器、智能体及功能特性。

* __[安装](./usage/installation.md)__  
* __[入门与示例](./getting_started.md)__  
* __[使用 HoloOcean](./usage/usage.md)__
* __[HoloOcean 软件包](./packages/packages.md)__
* __[代理](./agents/agents.md)__
* __[传感器](./sensors/sensors.md)__
* __[环境外观](./env_appearance/env_appearance.md)__
* __[示例](./example/examples.md)__
* __[开发指南](./develop/develop.md)__
* __[PythonAPI 参考](https://openhutb.github.io/doc/python_api/#water)__

---

* __[ROS2 桥接器](./develop/ros2.md)__

---
* __[环境搭建](./HoloOcean.md)__  
* __[迁移至 UE4.26](./develop/ue4.md)__  
* __[使用 HoloOcean 的列表](./used_by.md)__ 
* __[其他](./underwater.md)__


## 功能

<!-- HoloOcean 2.4.0 特性 -->

* 声呐传感器的射线投射和GPU实现

* FFT 波

* FFT 波的新浮力

* 哈士奇号（Husky）载具

<!-- HoloOcean 2.2.2 - 2.3.0 特性 -->

* Raycast 和 Semantic Raycast 激光雷达

* 深度摄像头

* 语义分割摄像头

* 新业务园区软件包

* 水下洋流

* 生物量、盐度和温度 (BST) 传感器

* 潮汐控制

* 可根据天气和时间指令调整环境外观

* 车载闪光灯

* 3个拥有丰富基础设施、用于生成数据或测试水下算法的丰富世界

* 配备常规水下传感器，包括多普勒测速仪（DVL）、惯性测量单元（IMU）、光学相机、各类声呐[@Potokar22iros]、深度传感器等

* 高度且易于配置的传感器与任务

* 多代理任务，包括光学与声学通信

* 新型声纳仿真框架，用于模拟成像、剖面、侧扫和回声探测器声纳

* 成像声纳实现包含针对小型仿真-真实差距的逼真噪声建模

* 易于安装且简洁，提供类似 OpenAI Gym 的 Python 接口

* 高性能 - 模拟速度可达真实时间的2倍。仅对所需部分产生性能损耗

* 无头运行或观察代理学习过程

* 同时支持 Linux 和 Windows


## 参考

* [holoocean-v1.0.0](https://byu-holoocean.github.io/holoocean-docs/v1.0.0)
* [所有版本的文档](https://byu-holoocean.github.io/holoocean-docs/versionList.html) - [develop 分支文档](https://byu-holoocean.github.io/holoocean-docs/develop/index.html)
* [HoloOcean 2 主仓库](https://github.com/byu-holoocean/HoloOcean) - [develop 分支](https://github.com/byu-holoocean/HoloOcean/commits/develop/)（从 UnrealEngine fork）
* [holodeck-engine 源代码](https://github.com/BYU-PCCL/holodeck-engine) - [holodeck 客户端](https://github.com/BYU-PCCL/holodeck)、[holodeck文档](https://holodeck.readthedocs.io/en/latest/)
* [HoloOcean 的 bitbucket 仓库列表](https://bitbucket.org/frostlab/workspace/projects/FROST_CORE)
* [HoloOcean 论文](https://www.cs.cmu.edu/~kaess/pub/Potokar22icra.pdf)
* [构建后缺少 UnrealBuildTool.exe](https://forums.unrealengine.com/t/missing-unrealbuildtool-exe-after-build/2674046/2)
* [UE Asset Downgrader 高版本转低版本-哔哩哔哩](https://b23.tv/EukLZB6)

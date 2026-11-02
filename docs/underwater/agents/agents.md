# HoloOcean 代理

在 HoloOcean 中，代理（Agent）是与环境进行交互的实体，并在场景配置文件中进行定义。代理配备了用于从环境收集数据的传感器。通过调用 `env.act()` 或 `env.step()` 传入指令来控制代理，这些指令会由代理的控制方案进行解析。

```python
import holoocean

scenario = {
   "name": "{Scenario Name}",
   "world": "{world it is associated with}",
   "package_name": "{package it is associated with}",
   "agents":[
      {
         "agent_name": "uav0",
         "agent_type": "{agent types}",
         "location": [1.0, 2.0, 3.0],
         "control_scheme": 0,
         "sensors": [
            { ... }
         ]
   ],
}

env = holoocean.make(scenario_cfg=scenario)

command = [0, 0, 0, 0, ...]

for range(100):
   env.step(command)
```

HoloOcean 提供了多种代理，每种代理都具备不同的能力。HoloOcean 中的三种主要智能体分别代表了三种最常见的**水域载具**：[悬停式自主水下航行器（HoveringAUV）](hovering_auv_agent.md)、[水面航行器（SurfaceVessel）](./surface_vessel_agent.md)和[鱼雷型自主水下航行器（TorpedoAUV）](./torpedo_auv_agent.md)。这三种代理能够执行大部分感知和导航任务。此外，系统中还包含代表飞行器及特定现实世界载具的其他代理。

有关在 HoloOcean 中开发自定义智能体的信息，请参阅[开发代理](../develop/agents.md)相关内容。


## 使用代理

关于如何在 HoloOcean 中使用代理的文档：

* [代理配置](./agent_config.md)

* [洋流控制器](./currents.md)

* [控制方案](./control_schemes.md)

* [基于 Fossen 模型的动力学](./fossen_based_dynamics.md)

* [手电筒](./flashlight.md)

## 代理

HoloOcean 中特定代理的文档。请注意，测试代理不应用重力效果。

### 水下代理

* 悬停式自主水下航行器 ([HoveringAUV](hovering_auv_agent.md))

* 鱼雷型自主水下航行器 ([TorpedoAUV](./torpedo_auv_agent.md))

* [BlueRov2](./blue_rov_agent.md)

* [CougUV](./coug_uv_agent.md)


### 水面代理

* 水面航行器 ([SurfaceVessel](./surface_vessel_agent.md))


### 测试代理

* 海龟代理 ([TurtleAgent](./turtle_agent.md))

* 球形代理 ([SphereAgent](./sphere_agent.md))

* 手部代理（[HandAgent](./hand_agent.md)）

* 机器人代理（[AndroidAgent](./android_agent.md)）


### 空域代理

* 无人机代理 ([UAVAgent](./uav_agent.md))


### 地面代理


* [哈士奇载具](./husky_agent.md)


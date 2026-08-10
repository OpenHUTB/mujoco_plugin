# 代理配置

HoloOcean 代理在场景字典中以列表形式声明。每个代理都使用列表中的一个新字典进行定义。

!!! 注意
    代理数组中的第一个代理是“主代理”。

```json
"agents":[
   {
      "agent_name": "uav0",
      "agent_type": "{agent types}",
      "sensors": [
         "array of sensor objects"
      ],
      "location": [1.0, 2.0, 3.0],
      "rotation": [1.0, 2.0, 3.0],
      "location_randomization": [1, 2, 3],
      "rotation_randomization": [10, 10, 10],
      "control_scheme": "{control scheme type}",
   },
   {
      "agent_name": "uav1",
      ...
   }
]
```

以下是代理字典中各键的说明：

## 代理名称

`agent_name` 是一个字符串，用于指定代理的名称。此名称用于在与环境交互时识别代理。

## 代理类型

`agent_type` 是一个字符串，用于指定代理的类型。下表列出了 `agent_type` 的当前有效参数：

| 代理类型  | agent_type 中的字符串 |
|-------|--------|
| [HoveringAUV](./hovering_auv_agent.md)     | `HoveringAUV`  |
| [SurfaceVessel](./surface_vessel_agent.md)     | `SurfaceVessel`  |
| [TorpedoAUV](./torpedo_auv_agent.md)     | `TorpedoAUV`  |
| [CougUV](./coug_uv_agent.md)     | `CougUV`  |
| [BlueROV2](./blue_rov_agent.md)     | `BlueROV2`  |
| [SphereAgent](./sphere_agent.md)     | `SphereAgent`  |
| [TurtleAgent](./turtle_agent.md)     | `TurtleAgent`  |
| [FixedWing](./fixed_wing_agent.md)     | `FixedWing`  |
| [UAV](./uav_agent.md)     | `UAV`  |
| [哈士奇载具](./husky_agent.md)     | `HuskyVehicle`  |


## 参考

* [Agent Configuration](https://byu-holoocean.github.io/holoocean-docs/develop/agents/docs/agent-config.html)
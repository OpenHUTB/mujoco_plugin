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


您可以在 [HoloOcean 代理](./agents.md) 中的各个代理页面找到每个代理的详细信息。随着更多代理加入 HoloOcean，此列表将会更新。

## 传感器

`sensors` 是一个传感器对象数组，这些传感器对象附加到代理上。每个传感器都使用列表中的一个新字典进行定义。有关配置和使用传感器的详细信息，请参阅[传感器配置](../sensors/sensor_config.md)。


## 位置和旋转

这些键定义了代理在世界中的位置和方向，分别以米和度为单位。位置的格式为 `[dx, dy, dz]`，旋转的格式为 `[roll, pitch, yaw]`，绕 XYZ 固定轴旋转，即 \(R_z\) \(R_y\) \(R_x\)。

!!! 注意
   * 位置使用 HoloOcean 世界坐标，而不是虚幻引擎关卡坐标！

   * HoloOcean 坐标系采用右手坐标，单位为米。

   * 有关详细信息，请参阅 [HoloOcean 中的单位和坐标](../usage/units_and_coordinates.md)。


## 位置随机化

`location_randomization` 和 `rotation_randomization` 是可选参数。如果提供，代理的起始位置和/或旋转角度将根据指定范围内的均匀采样值进行随机变化。每个方向的随机化是独立采样的。

位置随机化值以米为单位，格式为 `[dx, dy, dz]`。旋转随机化值格式为 `[roll, pitch, yaw]`，绕 XYZ 固定轴旋转（即 \( R_z*R_y*R_x \)）。

## 控制方案

`control_scheme` 是一个字符串，用于指定智能体使用的控制方案（以整数表示）。

控制方案决定了发送给代理的命令如何被解释。大多数代理都具有一种控制方案，该方案允许直接命令控制其推进器、鳍片等。其他控制方案则实现了诸如位置 PID 控制器等便捷功能。用户可以使用自定义动力学控制方案来微调飞行器的运动。

有关控制方案的更多详细信息，请参[阅控制方案](./control_schemes.md)。



## 参考

* [Agent Configuration](https://byu-holoocean.github.io/holoocean-docs/develop/agents/docs/agent-config.html)
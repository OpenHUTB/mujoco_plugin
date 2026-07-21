# 场景 <span id="scenarios"></span>

## 什么是场景（Scenario）？<span id="what_is_a_scenario"></span>

场景用于告知 HoloOcean 需要加载哪个世界、在世界中放置哪些代理（agent），以及这些代理需要配备哪些传感器。

它定义了：

* 要加载的世界

* 代理定义

    * 代理的类型

    * 代理的位置

    * 代理配备的传感器

!!! 提示
    你可以把“场景”（scenarios）想象成《光环》（Halo）中的地图或游戏模式变体：地图本身保持不变，但其中的事物以及你的目标可能会发生变化。

场景功能允许同一个世界用于多种不同的用途，并且允许您扩展和自定义我们提供的场景以满足您的需求，而无需重新打包引擎。

当您调用 `holoocean.make()` 创建环境时，您需要传入一个场景名称，例如 `holoocean.make("Pier-Hovering")`。这会告诉 HoloOcean 要加载哪个世界以及在哪里放置代理。


## 场景文件格式 <span id="scenario_file_format"></span>

场景 `.json` 文件以包的形式分发（参见[包内容](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/packages/docs/package-structure.html#package-contents)），且必须命名为 `{WorldName}-{ScenarioName}.json`。默认情况下，它们存储在 `worlds/{PackageName}` 目录下，但也支持直接从 Python 字典加载。

### 场景文件

```json
{
   "name": "{Scenario Name}",
   "world": "{world it is associated with}",
   "lcm_provider": "{Optional, where to publish lcm to}",
   "ticks_per_sec": 30,
   "frames_per_sec": 30,
   "env_min": [-10, -10, -10],
   "env_max": [10, 10, 10],
   "octree_min": 0.1,
   "octree_max": 5,
   "agents":[
      "array of agent objects"
   ],
   "weather": {
      "hour": 12,
      "type": "'sunny' or 'cloudy' or 'rain'",
      "fog_density": 0,
      "day_cycle_length": 86400
   },
   "window_width":  1280,
   "window_height": 720
}
```
`window_width/height` 控制创建环境时打开的窗口的大小。


!!! 注意
    agents 数组中的第一个代理是“主代理”。


## 帧率

您可以配置两个参数来控制帧率的变化：每秒节拍数`ticks_per_sec` 和 每秒帧数`frames_per_sec`。

`ticks_per_sec` 参数用于设置模拟每秒的节拍数。该值必须高于所用传感器的采样率（以 Hz 为单位）。默认值为 30。

`frames_per_sec` 参数是环境可以运行的最大帧率 (FPS)。如果设置为 *true*，则帧率将与 `ticks_per_sec` 相同。如果设置为 *false*，则帧率不受限制，环境将以尽可能快的速度运行。如果设置为一个数值，则该数值将作为帧率上限。

以下是一些配置示例。如果您手动控制机器人，则可能希望它以实时速度运行，因此需要将 `frames_per_sec` 设置为 true。使用高性能 GPU 时，模拟运行速度可能远超实时速度，否则将难以控制。如果你运行的是无头/自主模式，你可能希望模拟运行得尽可能快，因此良好的帧率（`frames_per_sec`）应该是 false。


## 配置八叉树 <span id="configure_octree"></span>

使用声呐传感器并初始化世界时，系统会创建一个八叉树或从缓存加载一个八叉树。可以使用 `env_min`、`env_max`、`octree_min` 和 `octree_max` 设置这些参数。八叉树缓存在 worlds 文件夹下的 `LinuxNoEditor/Holodeck/Octrees` 文件夹中。请参阅[软件包安装位置](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/packages/docs/installation.html#package-locations)。

`env​​_min`/`env_max` 用于设置环境的上限/下限。它们应该在[软件包结构](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/packages/docs/package-structure.html#id2)中设置，但此处设置的值会覆盖该设置。

`octree_min`/`octree_max` 用于设置八叉树的最小/中间尺寸。`octree_min` 可以低至 0.01（1 厘米），然后八叉树的尺寸将翻倍，直到达到 `octree_max`。

### 代理对象

```json
{
   "agent_name": "uav0",
   "agent_type": "{agent types}",
   "sensors": [
      "array of sensor objects"
   ],
   "control_scheme": "{control scheme type}",
   "location": [1.0, 2.0, 3.0],
   "rotation": [1.0, 2.0, 3.0],
   "location_randomization": [1, 2, 3],
   "rotation_randomization": [10, 10, 10]
}
```

!!! 注意
    HoloOcean 坐标系采用右手坐标，单位为米。请参阅坐标系。

### 位置随机化

`location_randomization` 和 `rotation_randomization` 为可选参数。如果提供，智能体的起始位置和/或旋转角度将根据所提供的随机化值（取自均匀分布的正负值）随机变化。

位置值以米为单位，格式为 `[dx, dy, dz]`；旋转角度为 `[roll, pitch, yaw]`，绕 XYZ 固定轴旋转，即 \(R_z\) \(R_y\) \(R_x\)。

### 代理类型

以下是有效的代理类型`agent_type` s：

| 代理类型  | agent_type 中的字符串 |
|-------|--------|
| [HoveringAUV](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/hovering-auv-agent.html#hovering-auv-agent)     | `HoveringAUV`  |
| [TorpedoAUV](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/torpedo-auv-agent.html#torpedo-auv-agent)     | `TorpedoAUV`  |
| [TurtleAgent](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/turtle-agent.html#turtle-agent)     | `TurtleAgent`  |
| [UavAgent](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/uav-agent.html#uav-agent)     | `UAV`  |

### 控制方案

控制方案以整数形式表示。有关有效值以及每种方案的工作原理说明，请参阅各代理的文档页面。

### 传感器对象

```json
{
   "sensor_type": "RGBCamera",
   "sensor_name": "FrontCamera",
   "location": [1.0, 2.0, 3.0],
   "rotation": [1.0, 2.0, 3.0],
   "socket": "socket name or \"\"",
   "Hz": 5,
   "lcm_channel": "channel_name",
   "configuration": {

   }
}
```

传感器有几种安装方式。

**1.提供套接字名称**

这将把传感器安装到指定的套接字中。
```json
{
   "sensor_type": "RGBCamera",
   "socket": "CameraSocket"
}
```

**2.提供套接字、位置和/或旋转参数**

传感器将根据指定的位置和旋转参数相对于插座进行偏移放置。旋转参数为`[roll, pitch, yaw]`（以度为单位），绕XYZ固定轴旋转，即 \(R_z\) \(R_y\) \(R_x\)。


**3.只需提供位置和/或旋转角度即可**

传感器将放置在给定的坐标处，相对于代理的根节点进行偏移。
```json
{
   "sensor_type": "RGBCamera",
   "location": [1.0, 2.0, 3.0],
   "rotation": [1.0, 2.0, 3.0]
}
```

**4.提供传感器采样率**

传感器将以该采样率进行采样。请注意，该值必须小于 `ticks_per_sec`，并且最好是 `ticks_per_sec` 的倍数。有关 `ticks_per_sec` 的更多信息，请参阅[帧率](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/usage/scenarios.html#configure-framerate)部分。
```json
{
   "sensor_type": "RGBCamera",
   "Hz": 20
}
```

**5.发布消息**

目前，HoloOcean 支持向 LLM 发布消息（新版本已支持 ROS 包）。要向 LCM 发布传感器数据，请指定要发布的类型。
```shell
{
   "sensor_type": "RGBCamera",
   "lcm_channel": "CAMERA"
}
```

channel 参数指定要将传感器数据发布到哪个通道。

传感器对象中唯一必需的键是`"sensor_type"`，其余键将使用默认值，如下所示。
```json
{
   "sensor_name": "sensor_type",
   "location": [0, 0, 0],
   "rotation": [0, 0, 0],
   "socket": "",
   "publish": "",
   "lcm_channel": "",
   "configuration": {}
}
```

### 配置块

配置`configuration`块的内容与传感器密切相关。该配置块会原封不动地传递给传感器，由传感器进行解析。

例如，[RGBCamera](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.RGBCamera) 的文档字符串指出它接受 `CaptureWidth` 和 `CaptureHeight` 参数，因此一个示例传感器配置如下：

```json
{
   "sensor_name": "RBGCamera",
   "socket": "CameraSocket",
   "configuration": {
      "CaptureHeight": 1920,
      "CaptureWidth": 1080
   }
}
```

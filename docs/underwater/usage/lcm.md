# 发布传感器数据

目前，HoloOcean 支持将数据发布到 LCM（正在考虑添加 ROS 封装）。所有配置都在[场景](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/usage/scenarios.html#scenarios)文件中完成。我们将在下文中概述具体步骤。


LCM 将数据发布到称为提供者的特定介质。提供者可以是本地、网络、日志文件等。可以在场景文件的头部指定提供者。有关选项，请参阅此处。如果未指定提供者，HoloOcean 将使用默认的 LCM udqm。

```json
{
   "name": "{Scenario Name}",
   "world": "{world it is associated with}",
   "lcm_provider": "file:///home/lcm.log"
   "agents":[
      "array of agent objects"
   ]
}
```

选定提供者后，HoloOcean 会逐个发布每个传感器。然后，lcm_channel 由传感器配置决定。如果未指定通道，则不会发布该传感器。

```json
{
   "sensor_type": "RGBCamera",
   "sensor_name": "FrontCamera",
   "lcm_channel": "CAMERA",
}
```
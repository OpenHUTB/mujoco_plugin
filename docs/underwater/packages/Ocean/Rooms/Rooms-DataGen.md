# 房间数据生成器（Rooms-DataGen）

此场景以一个配备位置、旋转和测距传感器的 TurtleAgent 开始。所有传感器均未包含噪声。

* turtle0：主 [Turtle](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/turtle-agent.html#turtle-agent) 代理

* 位置传感器 [LocationSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.LocationSensor)

* 旋转传感器 [RotationSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.RotationSensor)

* 测距仪 RangeFinder 配置有 64 个光束，最大距离为 20 米。
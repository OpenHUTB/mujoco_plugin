# 开放水域鱼雷型机器人（OpenWater-Torpedo）

此场景开始时，一艘鱼雷型自主水下航行器（TorpedoAUV）位于潜艇附近。除非另有说明，所有传感器的名称均与其类名相同，例如，IMUSensor 的名称为“IMUSensor”。

* auv0：主[悬停自主水下航行器](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/hovering-auv-agent.html#hovering-auv-agent)代理

    * [IMUSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.IMUSensor) 配置了噪声和偏差，并返回偏差值。

    * [GPSSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.GPSSensor) 获取表面 N(1, 0.25) 范围内的测量值，实际测量值也包含噪声。

    * [DVLSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.DVLSensor) 配置了 22.5 度仰角和噪声，并返回 4 个距离测量值。

    * [DepthSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.DepthSensor) 配置了噪声。

    * [PoseSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.PoseSensor) 用于获取真实值。

    * [VelocitySensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.VelocitySensor) 用于获取真实值。

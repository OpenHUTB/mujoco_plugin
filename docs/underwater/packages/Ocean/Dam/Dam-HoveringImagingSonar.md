# 大坝附近悬停的成像声呐（Dam-HoveringImagingSonar）

此场景开始时，一艘悬停式自主水下航行器 (HoveringAUV) 位于实际水坝附近。它与基础版本相同，只是加装了声呐。八叉树叶片大小为 2 厘米。除非另有说明，所有传感器的名称均与其类名相同，例如，IMUSensor 的名称为“IMUSensor”。

* auv0：主悬停式自主水下航行器代理

    * [IMUSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.IMUSensor) 配置了噪声和偏差，并返回偏差值。

    * [GPSSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.GPSSensor) 使用 N(1, 0.25) 的方位角获取表面测量值，实际测量值也包含噪声。

    * [DVLSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.DVLSensor) 配置了 22.5 度的仰角和噪声，并返回 4 个距离测量值。

    * [ImagingSonar](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.ImagingSonar) 配置了仰角为 20 度，方位角为 130 度，测量范围为 1-40 米，初始八叉树生成范围为 40 米，并启用所有噪声。

    * [DepthSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.DepthSensor) 配置了噪声。

    * [PoseSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.PoseSensor) 用于获取真实值。

    * [VelocitySensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.VelocitySensor) 用于获取真实值。

![](../../../../img/underwater/starting.png)
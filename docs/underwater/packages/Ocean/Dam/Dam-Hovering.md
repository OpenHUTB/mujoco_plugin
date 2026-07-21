# 大坝附近悬停（Dam-Hovering）

此场景开始时，一艘悬停式自主水下航行器 (Hovering Autonomous Underwater Vehicle, HoveringAUV) 位于实际大坝附近。除非另有说明，所有传感器的名称均与其类名相同，例如，IMUSensort 的名称为“IMUSensor”。

* `auv0`：主悬停AUV代理

    * [IMUSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.IMUSensor) 配置了噪声和偏差，并返回偏差值。

    * [GPSSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.GPSSensor) 使用N(1, 0.25)的方差获取表面测量值，实际测量值也包含噪声。

    * [DVLSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.DVLSensor) 配置了22.5度的仰角和噪声，并返回4个距离测量值。

    * [DepthSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.DepthSensor) 配置了噪声。

    * [PoseSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.PoseSensor) 用于获取**实地测量真实值**（ground truth）。

    * [VelocitySensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.VelocitySensor)用于获取实地测量真实值。

![](../../../../img/underwater/starting.png)
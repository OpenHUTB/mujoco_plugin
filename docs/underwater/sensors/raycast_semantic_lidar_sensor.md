# Raycast 语义激光雷达传感器

使用光线投射模拟激光雷达传感器。返回传感器范围内所有被探测到的物体的点云，以及每个被探测到物体的语义数据，包括被探测到物体的唯一对象 ID 和语义标签/类别。点云会根据环境的语义地图进行分类。此外，还会返回每个点的强度和环/通道数。

有关参数和如何使用此传感器的更多信息，请参阅 [Raycast LIDAR](./raycast_lidar_sensor.md)。

有关如何使用基础非语义传感器的示例，请参阅[可视化 Raycast LIDAR](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/examples/examples/raycast-lidar.html#visualizing-raycast-lidar)。将传感器类型更改为 RaycastSemanticLidar 即可返回语义信息。

!!! 注意
    所有 HoloOcean 关卡均已应用语义标签。如果您正在创建自定义关卡，则必须启用语义标签并定义任何新标签。有关说明和我们当前的语义标签列表，请参阅[添加自定义语义标签](./custom_semantics.md)。

有关 Python API，请参阅 [RaycastSemanticLidar](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/holoocean/sensors.html#holoocean.sensors.RaycastSemanticLidar)。

传感器定义示例：

```json
{
    "sensor_type": "RaycastSemanticLidar",
    "configuration": {
        "socket": "CameraSocket",
        "Channels": 128,
        "Range": 200,
        "PointsPerSecond": 20000,
        "RotationFrequency": 10,
        "UpperFovLimit": 10,
        "LowerFovLimit": -30,
        "HorizontalFov": 360.0,
        "AtmospAttenRate": 0.4,
        "RandomSeed": 42,
        "DropOffGenRate": 0.45,
        "DropOffIntensityLimit": 0.8,
        "DropOffAtZeroIntensity": 0.4,
        "ShowDebugPoints": True,
        "NoiseStdDev": 0.0
    },
    "Hz": 10
}
```
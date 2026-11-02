# 光线投射激光雷达

使用光线投射模拟激光雷达传感器。返回传感器探测范围内“命中”对象的点云。同时返回每个点的强度和环/通道数。目前强度仅基于大气衰减（由 `AtmospAttenRate` 参数设置）和到对象的距离。

可以通过更改 `DropOffGenRate` 参数来设置点云的总体衰减率。此外，还可以根据 `DropOffIntensityLimit` 和 `DropOffAtZeroIntensity` 参数对点云应用基于强度的衰减率。这些参数在 `DropOffIntensityLimit`（强度衰减的起始强度）和 `DropOffAtZeroIntensity`（强度为零时的衰减率）之间创建线性衰减。要禁用所有衰减，请将 `DropOffGenRate` 和 `DropOffIntensityLimit` 都设置为 0.0。


请注意，要获得完整的 360 度扫描（或由 `Horizo​​ntalFov` 设置的完整水平视场），需要调整 `RotationFrequency` 和 `TicksPerSecond` 参数。将它们设置为相等即可获得完整的 360 度扫描。或者，如果您不希望传感器以与环境相同的频率运行，可以更改每次捕获的刻度数（请参阅下面的示例传感器定义，其中参数列为 Hz）。`Hz` 参数控制传感器捕获和返回数据的每次捕获节拍数。如果 `Hz` 设置为与 `RotationFrequency` 相同的值，则传感器将在每个刻度返回完整的 360 度扫描。

有关如何使用此传感器的示例，请参阅[可视化 Raycast LiDAR](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/examples/examples/raycast-lidar.html#visualizing-raycast-lidar)。

有关 Python API，请参阅 [RaycastLidar](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/holoocean/sensors.html#holoocean.sensors.RaycastLidar)。

示例传感器定义：
```json
{
    "sensor_type": "RaycastLidar",
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
    "Hz": 10 #TicksPerCapture
}
```

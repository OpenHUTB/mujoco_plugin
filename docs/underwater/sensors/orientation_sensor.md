# 朝向传感器

该**传感器**返回其在**全局坐标系**中的前向、右向和上向向量，以 3x3 矩阵的形式表示。如果传感器位于 COM 以外的插槽中，则返回的矩阵将反映插槽的全局方向（车辆方向加上车辆到所用插槽的方向偏移量）。

!!! 注意
    在我们提供的使用此传感器的配置中，传感器位于 IMU 插槽中，该插槽的方向为 NED（非垂直）。

有关 Python API 和更多详细信息，请参阅 [OrientationSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.OrientationSensor)。

传感器定义示例：
```json
{
    "sensor_type": "OrientationSensor",
    "socket": "IMUSocket",
}
```
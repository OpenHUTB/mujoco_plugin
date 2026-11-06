# 姿态传感器

返回**传感器**在**全局坐标系**中的朝向（参见 [OrientationSensor](./orientation_sensor.md)）和位置，以 4x4 齐次矩阵的形式表示。如果传感器位于 COM 插槽以外的插槽中，则返回其所在插槽的全局位姿（车辆位置加上车辆 COM 到插槽的偏移量）。

4x4 矩阵的形式如下：
```
[R, p]
[0, 1]
```

其中 R 是一个 3x3 旋转矩阵，p 是一个 3x1 位置向量。最后一行始终为 [0, 0, 0, 1]。

有关 Python API 和更多详细信息，请参阅 [PoseSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.PoseSensor)。

传感器定义示例：
```json
{
    "sensor_type": "PoseSensor",
    "socket": "COM"
}
```

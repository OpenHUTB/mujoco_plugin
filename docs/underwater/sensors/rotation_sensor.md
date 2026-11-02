# 旋转传感器

获取**传感器**在**全局坐标系**中的[横滚角、俯仰角、偏航角]旋转角度。如果传感器位于车辆质心以外的插槽中，则返回其所在插槽的全局旋转角度（车辆旋转角度加上车辆质心到插槽的旋转偏移量）。

角度单位为度。

有关 Python API，请参阅 [RotationSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.RotationSensor)。

传感器定义示例：
```json
{
    "sensor_type": "RotationSensor",
    "socket": "COM",
}
```
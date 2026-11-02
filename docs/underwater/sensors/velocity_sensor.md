# 速度传感器

返回**传感器**在**全局坐标系**中的 [x,y,z] 速度。如果传感器位于车辆质心以外的插槽中，则返回所用插槽的速度（车辆速度加上车辆质心与所用插槽之间的相对速度）。

有关 Python API，请参阅 [VelocitySensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.VelocitySensor)。

传感器定义示例：

```json
{
    "sensor_type": "VelocitySensor",
    "socket": "IMUSocket"
}
```


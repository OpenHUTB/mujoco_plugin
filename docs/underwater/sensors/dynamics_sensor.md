# 动力学传感器

该传感器返回实现自定义动态模型所需的真实值。动态传感器按顺序返回线加速度、速度和位置，然后是角加速度、速度和位置。

!!! 注意
    无论传感器位于哪个接口，它始终返回车辆质心 (COM) 处的值，且这些值采用全局坐标系。

有关 Python API 和更多详细信息，请参阅 [DynamicsSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.DynamicsSensor)。

传感器定义示例：

```json
{
    "sensor_type": "DynamicsSensor",
    "socket": "COM",
    "configuration": {
       "UseCOM": true,
       "UseRPY": true
    }
}
```
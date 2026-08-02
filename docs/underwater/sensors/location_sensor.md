# 位置传感器

返回**传感器**在**全局坐标系**中的 [x,y,z] 坐标。如果传感器位于 COM 接口以外的其他接口，则返回其所在接口的全局位置（车辆位置加上车辆 COM 接口到接口的偏移量）。

有关 Python API，请参阅 [LocationSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.LocationSensor)。


传感器定义示例：

```json
{
    "sensor_type": "LocationSensor",
    "socket": "COM",
    "configuration": {
        "Sigma": 0
    }
}
```
# 多普勒测速仪 (DVL)

多普勒测速仪传感器。

有关 Python API，请参阅 [DVLSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.DVLSensor)。

https://byu-holoocean.github.io/holoocean-docs/v2.0.0/holoocean/sensors.html#holoocean.sensors.DVLSensor

传感器定义示例：

```json
{
    "sensor_type": "DVLSensor",
    "socket": "DVLSocket",
    "Hz": 20,
    "configuration": {
        "Elevation": 22.5,
        "DebugLines": false,
        "VelSigma": 0.02626,
        "ReturnRange": true,
        "MaxRange": 50,
        "RangeSigma": 0.1
    }
}
```
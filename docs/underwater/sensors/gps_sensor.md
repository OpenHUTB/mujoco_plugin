# 全球定位系统 (GPS)

模拟 GPS 传感器，包括水下信号接收。

请参阅 Python API 中的 [GPSSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.GPSSensor) 类。

传感器定义示例：
```json
{
    "sensor_type": "GPSSensor",
    "socket": "IMUSocket",
    "Hz": 5,
    "configuration":{
        "Sigma": 0.5,
        "Depth": 1,
        "DepthSigma": 0.25
    }
}
```
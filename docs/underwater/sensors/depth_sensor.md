# 深度传感器

一种深度传感器，能够模拟无噪声或有噪声环境下的水下深度测量。

更多信息请参见[深度传感器](https://openhutb.github.io/doc/python_api/#holoocean.sensors.DepthSensor)部分。

传感器定义示例：

```json
{
    "sensor_type": "DepthSensor",
    "socket": "DepthSocket",
    "Hz": 100,
    "configuration": {
        "Sigma": 0.255
    }
}
```

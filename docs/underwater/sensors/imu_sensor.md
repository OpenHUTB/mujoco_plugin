# 惯性测量单元 (IMU)

模拟 IMU 传感器，可添加噪声，但默认不添加噪声。返回值是一个二维 NumPy 数组，大小为 2x3（默认）或 4x3（带偏置）。

有关 Python API 和更多详细信息，请参阅 [IMUSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.IMUSensor)。


传感器定义示例：
```json
{
    "sensor_type": "IMUSensor",
    "socket": "IMUSocket",
    "Hz": 200,
    "configuration": {
        "AccelSigma": 0.00277,
        "AngVelSigma": 0.00123,
        "AccelBiasSigma": 0.00141,
        "AngVelBiasSigma": 0.00388,
        "ReturnBias": true
    }
}
```
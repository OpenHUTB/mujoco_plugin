# 光调制解调器

用于空中或水面代理通信的光纤调制解调器。

命令 [holoocean.environments.HoloOceanEnvironment.send_optical_message()](https://openhutb.github.io/doc/python_api/#send_optical_message) 用于在光调制解调器之间发送消息。

!!! 注意
    为了成功发送消息，两个传感器必须对齐。

此外，如果需要，还可以使用以下辅助函数：

* [holoocean.environments.HoloOceanEnvironment.modems](https://openhutb.github.io/doc/python_api/#modems) 返回所有调制解调器。

* [holoocean.environments.HoloOceanEnvironment.modems_id](https://openhutb.github.io/doc/python_api/#modems_id) 返回所有调制解调器 ID。

有关如何使用此传感器的示例，请参阅[多代理示例](../example/multi_agent.md)。

有关 Python API，请参阅[OpticalModemSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.OpticalModemSensor)。

传感器定义示例：
```json
{
    "sensor_type": "OpticalModemSensor",
    "location": [0,0,0],
    "configuration": {
        "id": 1
    }
}
```
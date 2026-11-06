# 声学信标

用于水下代理间通信的声学调制解调器。

命令 [holoocean.environments.HoloOceanEnvironment.send_acoustic_message()](https://openhutb.github.io/doc/python_api/#send_acoustic_message) 用于在声学信标之间发送消息。可以发送多种消息类型，每种消息类型的功能各不相同。详情请参阅 [holoocean.sensors.AcousticBeaconSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.AcousticBeaconSensor)。

此外，还有一些辅助函数可供使用：

* [holoocean.environments.HoloOceanEnvironment.beacons](https://openhutb.github.io/doc/python_api/#beacons) 返回所有信标。

* [holoocean.environments.HoloOceanEnvironment.beacons_id](https://openhutb.github.io/doc/python_api/#beacons_id) 返回所有信标的 ID。

* [holoocean.environments.HoloOceanEnvironment.beacons_status](https://openhutb.github.io/doc/python_api/#beacons_status) 返回所有信标的状态（是否正在传输）。

有关如何使用此传感器的示例，请参阅[多代理通信](../example/multi_coms.md)。

请参阅 [AcousticBeaconSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.AcousticBeaconSensor) 以获取 Python API。

传感器定义示例：

```json
{
    "sensor_type": "AcousticBeaconSensor",
    "location": [0,0,0],
    "configuration": {
        "id": 1
    }
}
```

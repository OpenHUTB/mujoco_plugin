# 多代理通信

多代理之间往往需要进行通信。这可以通过**声学信标传感器** AcousticBeaconSensor（通过声学信号进行通信的虚拟声学调制解调器；信标即信号标记点，也就是信号源）或**光调制解调器传感器** OpticalModemSensor（距离短、带宽大）来实现。以下是相关示例：

## 发送声学消息

[holoocean.environments.HoloOceanEnvironment.send_acoustic_message()](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.send_acoustic_message) 命令用于在声学信标之间发送消息。系统支持发送多种类型的消息，且各自具有不同的功能；具体详情请参阅 [holoocean.sensors.AcousticBeaconSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.AcousticBeaconSensor)。

此外，如有需要，还可以使用以下辅助函数：

* [holoocean.environments.HoloOceanEnvironment.beacons](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.beacons)：返回所有信标。

* [holoocean.environments.HoloOceanEnvironment.beacons_id](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.beacons_id)：返回所有信标的 ID。

* [holoocean.environments.HoloOceanEnvironment.beacons_status](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.beacons_status)：返回所有信标的状态（即是否正在发送信号）。

```python
import holoocean

cfg = {
    "name": "test_acou_coms",
    "world": "SimpleUnderwater",
    "package_name": "Ocean",
    "main_agent": "auv0",
    "ticks_per_sec": 200,
    "agents": [
        {
            "agent_name": "auv0",
            "agent_type": "HoveringAUV",
            "sensors": [
                {
                    "sensor_type": "AcousticBeaconSensor",
                    "location": [0,0,0],
                    "configuration": {
                        "id": 0
                    }
                },
            ],
            "control_scheme": 0,
            "location": [0, 0, -5]
        },
        {
            "agent_name": "auv1",
            "agent_type": "HoveringAUV",
            "sensors": [
                {
                    "sensor_type": "AcousticBeaconSensor",
                    "location": [0,0,0],
                    "configuration": {
                        "id": 1
                    }
                },
            ],
            "control_scheme": 0,
            "location": [0, 100, -5]
        }
    ]
}

env = holoocean.make(scenario_cfg=cfg)
env.reset()

# 这就是如何从一个声学通信设备向另一个发送消息的方法。
# 此操作将消息从 ID 0 发送至 ID 1（ID 在上文已配置），消息类型为“OWAY”，数据内容为“my_data_payload”。
env.send_acoustic_message(0, 1, "OWAY", "my_data_payload")

for i in range(300):
    states = env.tick()
    if "AcousticBeaconSensor" in states['auv1']:
        # 针对此消息，应收到 [message_type, from_sensor, data_payload] 的回复。
        print(i, "Received:", states['auv1']["AcousticBeaconSensor"])
        break
    else:
        print(i, "No message received")
```

## 发送光通信消息

[holoocean.environments.HoloOceanEnvironment.send_optical_message()](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.send_optical_message) 命令用于在光调制解调器（optical modems）之间发送消息。有关配置详情，请参阅 [holoocean.sensors.OpticalModemSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.OpticalModemSensor)。请注意，若要成功传输消息，两个传感器必须处于对齐状态。

此外，如有需要，还可以使用以下辅助函数：

* [holoocean.environments.HoloOceanEnvironment.modems](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.modems) 返回所有调制解调器。

* [holoocean.environments.HoloOceanEnvironment.modems_id](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.modems_id) 返回所有调制解调器的 ID。

```python
import holoocean

cfg = {
    "name": "test_acou_coms",
    "world": "SimpleUnderwater",
    "package_name": "Ocean",
    "main_agent": "auv0",
    "ticks_per_sec": 200,
    "agents": [
        {
            "agent_name": "auv0",
            "agent_type": "HoveringAUV",
            "sensors": [
                {
                    "sensor_type": "OpticalModemSensor",
                    "location": [0,0,0],
                    "socket": "SonarSocket",
                    "configuration": {
                        "id": 0
                    }
                },
            ],
            "control_scheme": 0,
            "location": [25, 0, -5],
            "rotation": [0, 0, 180]
        },
        {
            "agent_name": "auv1",
            "agent_type": "HoveringAUV",
            "sensors": [
                {
                    "sensor_type": "OpticalModemSensor",
                    "location": [0,0,0],
                    "socket": "SonarSocket",
                    "configuration": {
                        "id": 1
                    }
                },
            ],
            "control_scheme": 0,
            "location": [0, 0, -5]
        }
    ]
}

env = holoocean.make(scenario_cfg=cfg)
env.reset()

# 这就是如何从一个光通信模块向另一个发送消息的方法。
# 此操作将数据“my_data_payload”从 ID 0 发送至 ID 1（ID 在上文已配置）。
env.send_optical_message(0, 1, "my_data_payload")

for i in range(300):
    states = env.tick()
    if "OpticalModemSensor" in states['auv1']:
        print(i, "Received:", states['auv1']["OpticalModemSensor"])
        break
    else:
        print(i, "No message received")
```

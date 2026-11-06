# 磁力计

返回局部坐标系中的全局 x 轴（或配置向量）。

有关 Python API 和更多详细信息，请参阅 [MagnetometerSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.MagnetometerSensor)。

传感器定义示例：

```json
{
    "sensor_type": "MagnetometerSensor",
    "socket": "IMUSocket",
    "configuration": {
       "Sigma": 0,
       "MagnetixVector": [1,0,0]
    }
}
```
# 单波束声呐

该传感器使用八叉树模拟单个锥形声呐波束，并返回每个距离区间内的回波强度一维数组。


有关如何使用此传感器的示例，请参阅[可视化单波束声呐](../example/sonar_singlebeam.md)。

有关 Python API，请参阅 [SinglebeamSonar](https://openhutb.github.io/doc/python_api/#holoocean.sensors.SinglebeamSonar)。

传感器定义示例：

```json
{
    "sensor_type": "SinglebeamSonar",
    "socket": "SonarSocket",
    "Hz": 10,
    "configuration": {
        "OpeningAngle": 30,
        "RangeMin": 0.5,
        "RangeMax": 30,
        "RangeBins": 200,
        "AddSigma": 0,
        "MultSigma": 0,
        "RangeSigma": 0.1,
        "ShowWarning": true,
        "InitOctreeRange": 40,
        "ViewRegion": false,
        "ViewOctree": -10,
        "WaterDensity": 997,
        "WaterSpeedSound": 1480,
        "UseApprox": true
    }
}
```


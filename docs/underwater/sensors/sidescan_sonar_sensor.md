# 侧扫声呐

使用八叉树模拟侧扫声呐。具有较窄的仰角和较宽的横轴，并模拟两侧扫描。

有关如何使用此传感器的示例，请参阅[可视化侧扫声呐](../example/sonar_sidescan.md)。

有关 Python API，请参阅 [SidescanSonar](https://openhutb.github.io/doc/python_api/#holoocean.sensors.SidescanSonar)。

传感器定义示例：
```json
{
    "sensor_type": "SidescanSonar",
    "socket": "SonarSocket",
    "Hz": 10,
    "configuration": {
        "Azimuth": 170,
        "Elevation": 0.25,
        "RangeMin": 0.5,
        "RangeMax": 40,
        "RangeBins": 2000,
        "AddSigma": 0.05,
        "MultSigma": 0.05,
        "ShowWarning": true,
        "InitOctreeRange": 50,
        "ViewRegion": false,
        "ViewOctree": -10,
        "WaterDensity": 997,
        "WaterSpeedSound": 1480,
        "UseApprox": true
    }
}
```
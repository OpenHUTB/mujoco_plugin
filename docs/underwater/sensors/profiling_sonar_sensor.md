# 剖面声呐

使用八叉树模拟剖面声呐。

请参阅[可视化剖面声呐](../example/sonar_profiling.md)了解如何使用此传感器的示例。

请参阅[ProfilingSonar](https://openhutb.github.io/doc/python_api/#holoocean.sensors.ProfilingSonar)了解 Python API。

传感器定义示例：

```json
{
    "sensor_type": "ProfilingSonar",
    "socket": "SonarSocket",
    "Hz": 2,
    "configuration": {
        "Azimuth": 120,
        "Elevation": 1,
        "RangeMin": 1,
        "RangeMax": 60,
        "RangeBins": 512,
        "AzimuthBins": 512,
        "AddSigma": 0.15,
        "MultSigma": 0.2,
        "MultiPath": true,
        "ClusterSize": 5,
        "ScaleNoise": true,
        "AzimuthStreaks": -1,
        "RangeSigma": 0.1,
        "ShowWarning": true,
        "InitOctreeRange": 70,
        "ViewRegion": false,
        "ViewOctree": -10,
    }
}
```
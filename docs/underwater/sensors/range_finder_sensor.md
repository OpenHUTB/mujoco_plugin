# 测距传感器

测距传感器是一种激光传感器。它会返回参数指定方向上最近碰撞点的距离。如果传感器在有效范围内未检测到任何目标，则返回负值。例如，如果一个代理有两个不同角度的测距传感器，每个传感器有 24 个激光束，则测距传感器的调试跟踪信息可能如下所示：

![](https://openhutb.github.io/doc/img/water/UAVRangeFinder.png)


也就是说，如果只有一个激光器，则只有一个激光器朝前；如果有三个激光器，则有一个激光器朝前，另外两个激光器沿圆周均匀分布，间隔 120 度；如果有三个激光器，则每隔 15 度就有一个激光器。

有关 Python API 和更多详细信息，请参阅 [RangeFinderSensor](https://openhutb.github.io/doc/python_api/#holoocean.sensors.RangeFinderSensor)。

传感器定义示例：

```json
{
    "socket": "COM",
    "configuration": {
        "LaserMaxDistance": 10,
        "LaserCount": 1,
        "LaserAngle": 0,
        "LaserDebug": false
    }
}
```

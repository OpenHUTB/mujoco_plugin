# 房间数据生成器（Rooms-DataGen）

此场景以一个配备位置、旋转和测距传感器的 TurtleAgent 开始。所有传感器均未包含噪声。

* turtle0：主 [Turtle](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/turtle-agent.html#turtle-agent) 代理

* 位置传感器 [LocationSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.LocationSensor)

* 旋转传感器 [RotationSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.RotationSensor)

* 测距仪 RangeFinder 配置有 64 个光束，最大距离为 20 米。

!!! 注意                                 
    本场景的代理是 TurtleAgent，控制命令为 **2 维**浮点向量（前向推力、旋转力），与水下 AUV 常见的 8 维不同。若传入 8 维命令，会报 `ValueError: could not broadcast input array from shape (8,) into shape (2,)`。各代理的命令维度见[控制方案](../../../agents/control_schemes.md)。

```python
import holoocean
import numpy as np

env = holoocean.make("Rooms-DataGen")
for _ in range(100):
    state = env.step(np.zeros(2))   # 2 维，不是 8 维
```
# 入门与示例

首先，请参阅安装以安装 holocean 包和 Ocean。

HoloOcean的最小使用示例（[getting_started.py](https://github.com/OpenHUTB/mujoco_plugin/blob/main/src/underwater/holo_ocean/getting_started.py)）如下：

```python
import holoocean
import numpy as np

env = holoocean.make("PierHarbor-Hovering")

# 悬停的AUV对每个推进器发出指令
command = np.array([10,10,10,10,0,0,0,0])

for _ in range(180):
   state = env.step(command)
```
![](../img/underwater/getting_started.gif)

请注意：

1. 您将场景的名称传递给 holoocean.make

   请参阅可用的所有不同世界和场景的软件包。

2. HoloOcean 的界面旨在让 OpenAI Gym 熟悉

您可以使用状态字典访问特定传感器的数据：

```python
dvl = state["DVLSensor"]
```

**就是这样！**HoloOcean的使用相当简单。

查看可用的不同[世界](./packages/packages.md#all_packages)，阅读[API文档](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/index.html#holoocean-api-index)，或者开始制作自己的自定义[场景](./usage/scenarios.md#scenarios)。


[这里](./example/examples.md)是一些片段，展示了如何使用 HoloOcean 的不同方面。





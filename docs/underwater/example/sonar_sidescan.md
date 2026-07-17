# 侧扫声纳可视化（Sidescan Sonar）

在仿真过程中，将声纳传感器的输出进行可视化通常很有用。本脚本即可实现这一功能，在每次接收到声纳数据时进行绘图。

请注意，运行此脚本期间会生成八叉树（octree），这可能会导致短暂的停顿。有关解决方案及更多信息，请参阅[八叉树生成](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/usage/octree.html#octree)相关内容。

```python
import holoocean
import matplotlib.pyplot as plt
import numpy as np

#### 获取声呐配置
scenario = "OpenWater-TorpedoSidescanSonar"
config = holoocean.packagemanager.get_scenario(scenario)
config = config['agents'][0]['sensors'][-1]["configuration"]
maxR = config['RangeMax']
binsR = config['RangeBins']

#### 准备好绘图
plt.ion()

t = np.arange(0,50)
r = np.linspace(-maxR, maxR, binsR)
R, T = np.meshgrid(r, t)
data = np.zeros_like(R)

plt.grid(False)
plot = plt.pcolormesh(R, T, data, cmap='copper', shading='auto', vmin=0, vmax=1)
plt.tight_layout()
plt.gca().invert_yaxis()
plt.gcf().canvas.flush_events()

#### 运行模拟
command = np.array([0,0,0,0,20])
with holoocean.make(scenario) as env:
    for i in range(1000):
        env.act("auv0", command)
        state = env.tick()

        if 'SidescanSonar' in state:
            data = np.roll(data, 1, axis=0)
            data[0] = state['SidescanSonar']

            plot.set_array(data.ravel())

            plt.draw()
            plt.gcf().canvas.flush_events()

print("Finished Simulation!")
plt.ioff()
plt.show()
```

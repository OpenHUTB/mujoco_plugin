# 八叉树生成

运行带有声呐传感器的环境时，必须生成八叉树。这些八叉树通常会占用数 GB 的存储空间，因此无法作为下载包的一部分提供。

启动时，会创建 `InitOctreeRange` 参数范围内的所有八叉树，然后随着智能体在环境中移动，会生成更多八叉树。这可能会导致首次运行模拟时出现停顿。屏幕上会显示警告信息，可以使用 `ShowWarning` 参数禁用此警告。所有后续的模拟运行都将使用缓存的八叉树，速度会快得多。

避免等待时间的一种方法是在不显示视窗的情况下运行模拟，让其在后台生成八叉树。以下是一个示例脚本，它正是这样做的，只需将场景更改为您想要为其创建八叉树的场景即可。

```python
import holoocean
import numpy as np
from tqdm import tqdm

command = np.array([0,0,0,0,-20,-20,-20,-20])
print("Building octrees...")
with holoocean.make("PierHarbor-HoveringImagingSonar", show_viewport=False) as env:
    for i in tqdm(range(1000)):
        env.act("auv0", command)
        state = env.tick()

print("Finished Simulation")
```

八叉树生成后，会保存在[软件包安装目录](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/packages/docs/installation.html#package-locations)下的一个名为“octree”的文件夹中。具体如下：

| 平台  | 八叉树保存位置 | 
|-------|--------|
| Linux     | ~/.local/share/holoocean/{holoocean_version}/worlds/{world_name}/LinuxNoEditor/Holodeck/Octrees  |
| Windows     | %USERPROFILE%\AppData\Local\holoocean\{holoocean_version}\worlds\{world_name}\WindowsNoEditor\Holodeck\Octrees  |


在这个八叉树文件夹中，每个层级名称都会有对应的子文件夹，每个层级名称下又会有一个子文件夹，每个子文件夹里又会有一个对应不同大小的八叉树。如果文件正在被保存，则表示模拟仍在运行，并未冻结。

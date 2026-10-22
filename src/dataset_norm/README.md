# dataset_norm

AirSea 合成数据集的**数据规范库**：目录布局、字段定义、增量落盘、合法性校验。

不依赖 HoloOcean / ROS，纯 Python 标准库即可运行。

## 目录约定（EuRoC 风格）

```
<root>/<world>/<agent>/<track>/
├── settings.json
├── imu0/
│   ├── sensor.yaml
│   └── data.csv
├── pose_groundtruth/
│   ├── sensor.yaml
│   └── data.csv
└── rgb/
    └── cam0/
        ├── sensor.yaml
        ├── data.csv          # timestamp[ns], filename
        └── data/*.png
```

## 快速使用

```python
from dataset_norm import SequenceWriter, Settings
from PIL import Image

settings = Settings(
    world="SimpleUnderwater",
    package="Ocean",
    ticks_per_sec=60,
    frames_per_sec=20,
    agents=("auv0",),
)

with SequenceWriter(
    root="out/AirSea-UV",
    world=settings.world,
    agent="auv0",
    track="track0",
    settings=settings,
) as w:
    w.register_pose(name="pose_groundtruth", rate_hz=20.0, frame_id="world")
    w.register_imu(name="imu0", rate_hz=200.0, frame_id="auv0/imu")

    for i in range(100):
        t_ns = 50_000_000 * i  # 20 Hz
        w.add_pose("pose_groundtruth", t_ns, (0.1 * i, 0.0, -1.0), (1, 0, 0, 0))
        # IMU 可比 pose 更密，这里示意对齐写入
        w.add_imu("imu0", t_ns, (0.0, 0.0, 0.01), (0.0, 0.0, -9.81))

print(w.stats())
```

## 校验

```bash
python -m dataset_norm.validate out/AirSea-UV/SimpleUnderwater/auv0/track0
python -m dataset_norm.validate <seq> --json report.json
```

退出码 `0` = PASS，`1` = FAIL。校验项包括：

- `settings.json` 关键字段齐全
- 每个传感器目录有 `sensor.yaml` + `data.csv`
- 时间戳严格递增、单位 ns、无 NaN/Inf
- IMU 7 列 / 位姿 8 列（四元数单位长）
- 相机：`data/` 内图像文件与 `data.csv` 一一对应
- 实际频率相对 `rate_hz` 偏差 >30% 时给出 warn

## 字段

| 传感器 | data.csv 列 |
|--------|-------------|
| imu | timestamp[ns], w_x, w_y, w_z, a_x, a_y, a_z |
| pose | timestamp[ns], p_x, p_y, p_z, q_w, q_x, q_y, q_z |
| 相机 | timestamp[ns], filename |

时间戳一律 **纳秒整数**；位姿四元数 **wxyz** 顺序；加速度 **m/s²**，角速度 **rad/s**，位置 **m**。

## 自测

```bash
python -m tests.test_dataset_norm
```

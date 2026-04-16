# URLab Bridge

URLab Bridge 是同一 GitHub 组织下的独立配套仓库（`urlab_bridge`）。它在外部系统和 URLab 的 MuJoCo 仿真之间提供 Python 侧的中间件，通过 ZMQ 进行通信，用于强化学习策略部署、远程遥操作、数据记录、传感器监控和自定义控制流程。

## 功能

- 双向 ZMQ 通信：从 Unreal 接收关节状态、传感器数据、基座状态和相机图像；向 Unreal 发送执行器指令和 PD 增益
- 远程控制：从 Python 脚本、Jupyter notebook、ROS 2 节点或任何支持 ZMQ 的系统驱动机器人
- 策略部署：针对 Unreal 仿真运行预训练的强化学习策略（运动、动作模仿、四足步态）
- 传感器监控：实时仪表盘（DearPyGui），用于可视化关节状态、传感器读数和相机画面
- 自动处理关节发现、关节映射和执行器 ID 解析
- 提供用于身体位置计算的正向运动学
- 面向多关节机构场景的前缀式消息过滤机制
- 同时支持位置目标（适用于位置执行器）与力矩目标（适用于运动 + PD 控制）。

## 架构

```
┌─────────────────────────────────┐     ZMQ      ┌──────────────────┐
│  Python (URLab Bridge)          │◄────────────►│  Unreal (URLab)  │
│                                 │              │                  │
│  Your Control System            │  joint state │  MuJoCo physics  │
│    ├─ RL Policy (RoboJuDo)      │◄─────────────│  ZMQ Broadcaster │
│    ├─ Custom Controller         │              │                  │
│    └─ Teleoperation             │  ctrl targets│  ZMQ Subscriber  │
│                                 │─────────────►│  → d->ctrl       │
└─────────────────────────────────┘              └──────────────────┘         
```

## 安装

```bash
cd Plugins/UnrealRoboticsLab/urlab_bridge
uv python install 3.11
uv venv --python 3.11 .venv
uv pip install numpy pyzmq
```

用于强化学习策略支持（RoboJuDo）
```bash
uv pip install -e RoboJuDo
uv pip install dearpygui opencv-python
cd RoboJuDo && git submodule update --init --recursive
```

## ZMQ 协议

有关 ZMQ 协议的详细信息、主题格式和消息结构，请参阅 ZMQ 网络文档。(zmq_networking.md).

## 直接使用 Bridge

无需 RoboJuDo 的自定义控制器示例：

```python
from urlab_policy.unreal_env import ZmqLink
import struct, time, numpy as np

zmq = ZmqLink("tcp://127.0.0.1:5555", "tcp://127.0.0.1:5556")
time.sleep(1)  # Wait for connection

# Read state
messages = zmq.drain()
for topic, payload in messages.items():
    if "/joint/" in topic and len(payload) == 16:
        jid, pos, vel, acc = struct.unpack("<Ifff", payload)
        print(f"Joint {jid}: pos={pos:.3f}")

# Send control (12 actuators, all to zero)
targets = np.zeros(12)
zmq.send_control("my_robot_prefix", targets)

zmq.close()
```

## RoboJuDo 集成

为了运行预训练的 RL 策略,该 bridge 将[RoboJuDo](https://github.com/HansZ8/RoboJuDo)封装为策略运行时。 

**GUI(图形界面):**
```powershell
.venv\Scripts\activate
$env:PYTHONPATH = "src"
python src\urlab_policy\policy_gui.py
```

**CLI(命令行):**
```bash
python src/run_policy.py --policy unitree --prefix g1
```

可用策略在`policy_registry.py`中注册。每个条目定义了策略配置类、环境配置、自由度数量和控制器类型。

### Go2 Walk-These-Ways 策略

12 自由度的四足策略，支持步态调节。提供预设步态：Trot（小跑）、Pronk（跳跃）、Bound（弹跳）和 Pace（侧对步）。需要下载检查点文件(详见文件  `RoboJuDo/checkpoints/` README).

## 运动执行器 vs 位置执行器

|    方式      |       MJCF 执行器 |                控制信号                  |            PD 位置              |
|----------   |------------------------------------|------------------------|---------------------------------|
|  Position   |   `<position kp="100" kv="5">`     |      位置目标（弧度）    |           MuJoCo 内部           |
|  Motor + PD |   `<motor forcerange="-88 88">`    |      位置目标（弧度 ）   |        C++ UMjPDController      |

位置执行器更简单、更稳定。运动+PD 方式与训练动力学完全匹配，但需要配置增益。使用 GUI 中的复选框进行切换。

## 配置

`env_config.py`中的关键设置：

| 字段 | 默认值 | 必须匹配 |
|-------|---------|------------|
| `sim_dt` | 0.002 | Unreal 管理器时间步长 |
| `sim_decimation` | 10 | 策略频率 = 1/(sim_dt * decimation) |
| `state_endpoint` | tcp://127.0.0.1:5555 | ZmqSensorBroadcaster 端点 (PUB) |
| `control_endpoint` | tcp://127.0.0.1:5556 | ZmqControlSubscriber 端点 (SUB) |

所有套接字在虚幻引擎端进行绑定，Python 桥接端负责连接。话题格式与端口分配详见[ZMQ Networking](zmq_networking.md) 


## 强制速度覆盖

策略 GUI 提供了强制速度覆盖功能，允许您直接发送手动速度指令（vx, vy, yaw_rate），绕过键盘操作输入。适用于脚本化运动或在 Unreal 中无需操作铰链即可进行测试。

## 多铰链场景

ZMQ 话题采用前缀匹配过滤机制（如`<prefix>/joint/...`, `<prefix>/control`,等）。在多铰链设备场景中，每个设备均以自身专属前缀进行消息的发布与订阅；Python 端会根据该前缀对接收的消息进行过滤，将状态数据路由至对应的策略实例。

## 网格处理

在导入之前，使用 `Scripts/clean_meshes.py`  将网格转换为 GLB 格式并解决文件名冲突。

## 调试工具

| 脚本 | 用途 |
|--------|---------|
| `zmq_visualizer_gui.py` | 独立的 ZMQ 状态查看器，带滑块 |
| `policy_gui.py` | 完整的策略运行器，带可视化 |
| `test_native_mujoco.py` | 在原生 MuJoCo 查看器中运行策略（真实情况对比） |
| `test_compare_targets.py` | 记录原生与 Unreal 的目标值以便比较 |

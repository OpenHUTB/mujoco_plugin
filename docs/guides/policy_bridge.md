# URLab 桥接器

URLab 桥接器是同一 GitHub 组织下的一个独立配套仓库 (`urlab_bridge`)。 它在外部系统与 URLab 的 MuJoCo 仿真之间提供 Python 端中间件，通过 ZMQ 进行通信，用于强化学习策略部署、远程遥操作、数据记录、传感器监控以及自定义控制流程。

##功能说明

- 双向 ZMQ 通信：从虚幻引擎接收关节状态、传感器数据、基座状态和相机图像； 向虚幻引擎回传执行器控制指令与 PD 增益
- 远程控制：通过 Python 脚本、Jupyter 笔记本、ROS 2 节点或任何支持 ZMQ 的系统控制机器人
- 策略部署：在虚幻仿真环境中运行预训练的强化学习策略（移动、动作模仿、四足步态等）
- 传感器监控：使用实时仪表盘（DearPyGui）可视化关节状态、传感器读数和相机画面
- 自动处理机械结构识别、关节映射和执行器 ID 解析
- 提供正运动学计算，用于获取机身位置
- 支持多机械结构场景下的基于前缀的消息过滤
- 同时支持位置目标（用于位置执行器）和扭矩目标（用于电机 + PD 控制）

## 架构

```
┌─────────────────────────────────┐     ZMQ      ┌──────────────────┐
│  Python（URLab 桥接器）         │◄────────────►│  虚幻引擎（URLab）│
│                                 │              │                  │
│  你的控制系统                   │  关节状态     │  MuJoCo 物理引擎 │
│    ├─ 强化学习策略 (RoboJuDo)   │◄─────────────│  ZMQ 广播器      │
│    ├─ 自定义控制器              │              │                  │
│    └─ 遥操作                    │  控制目标    │  ZMQ 订阅者      │
│                                 │─────────────►│  → d->ctrl       │
└─────────────────────────────────┘              └──────────────────┘
```

## 环境配置

```bash
cd Plugins/UnrealRoboticsLab/urlab_bridge
uv python install 3.11
uv venv --python 3.11 .venv
uv pip install numpy pyzmq
```

如需支持强化学习策略（RoboJuDo）：
```bash
uv pip install -e RoboJuDo
uv pip install dearpygui opencv-python
cd RoboJuDo && git submodule update --init --recursive
```

## ZMQ 协议

FZMQ 协议详情、主题格式和消息结构请参见 [ZMQ Networking](zmq_networking.md).

## 直接使用桥接器
如需在不使用 RoboJuDo 的情况下编写自定义控制器：
```python
from urlab_policy.unreal_env import ZmqLink
import struct, time, numpy as np

zmq = ZmqLink("tcp://127.0.0.1:5555", "tcp://127.0.0.1:5556")
time.sleep(1)  # 等待连接建立

# 读取状态
messages = zmq.drain()
for topic, payload in messages.items():
    if "/joint/" in topic and len(payload) == 16:
        jid, pos, vel, acc = struct.unpack("<Ifff", payload)
        print(f"Joint {jid}: pos={pos:.3f}")

# 发送控制指令（12 个执行器，全部置零）
targets = np.zeros(12)
zmq.send_control("my_robot_prefix", targets)

zmq.close()
```

## RoboJuDo 集成

为运行预训练强化学习策略，该桥接器封装了[RoboJuDo](https://github.com/HansZ8/RoboJuDo)作为策略运行环境。

**图形界面:**
```powershell
.venv\Scripts\activate
$env:PYTHONPATH = "src"
python src\urlab_policy\policy_gui.py
```

**命令行界面：**
```bash
python src/run_policy.py --policy unitree --prefix g1
```

可用的策略均在 `policy_registry.py`中注册。每一项都定义了策略配置类、环境配置、自由度数量和控制器类型。

### Go2 行走策略

12 自由度四足机器人步态策略。支持预设步态：小跑、腾跃、跳跃和平步。需要下载模型权重（链接见 `RoboJuDo/checkpoints/` 下的 README）。

## 运动执行器 vs 位置执行器
|----------|--------------|----------------|-------------|
|控制方式|	MJCF 执行器|	控制信号|	PD 控制位置|
|位置控制|	'<position kp="100" kv="5">'|	位置目标（弧度）|	MuJoCo 内部|
|运动 + PD|	 '<motor forcerange="-88 88">'|	位置目标（弧度）|	C++ UMjPDController|

位置执行器更简单、更稳定。 运动 + PD 与训练动力学完全一致，但需要配置控制增益。可通过图形界面复选框进行切换。

##配置项

 `env_config.py`中的关键配置：

|字段|	默认值|	必须匹配|
|-------|---------|------------|
|'sim_dt'|	0.002|	虚幻引擎管理器时间步长|
|'sim_decimation'|	10|	策略频率 = 1/(sim_dt * decimation)|
|'state_endpoint'|	tcp://127.0.0.1:5555|	ZMQ 传感器广播器地址（PUB）|
|'control_endpoint'|	tcp://127.0.0.1:5556|	ZMQ 控制订阅者地址（SUB）|
|
虚幻引擎端所有套接字均为绑定模式，Python 桥接器为连接模式。主题格式与端口分配请参见 [ZMQ Networking](zmq_networking.md) 。

## 强制运动覆盖

策略图形界面提供强制运动覆盖功能，允许直接发送手动速度指令（vx、vy、偏航速率）， 绕过键盘操控输入。适用于脚本化运动，或无需在虚幻中操控机械结构即可进行测试。

## 多机械结构场景
ZMQ 主题使用基于前缀的过滤 (`<prefix>/joint/...`, `<prefix>/control`, 等)。在包含多个机械结构的场景中，每个结构都使用自己的前缀进行发布和订阅。Python 端按前缀过滤接收消息，将状态分发给对应的策略实例。

## 网格模型预处理

在导入前使用 `Scripts/clean_meshes.py` o convert meshes to GLB and resolve filename conflicts before import.

## 调试工具

| 脚本 |	用途|
|--------|---------|
|'zmq_visualizer_gui.py'|	带滑动条的独立 ZMQ 状态查看器|
|'policy_gui.py'|	带可视化界面的完整策略运行工具|
|'test_native_mujoco.py'|	在原生 MuJoCo 查看器中运行策略（基准真值）|
|'test_compare_targets.py'|	记录控制目标，用于原生与虚幻版本对比|
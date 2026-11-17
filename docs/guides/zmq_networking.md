# ZMQ 网络与 ROS 2


Unreal Robotics Lab 使用 [ZeroMQ](https://zeromq.org) 进行所有外部通信。其设计理念是：保持虚幻引擎端快速、二进制且无依赖——然后由一个独立的桥接器负责将其转换为用户偏好的任何框架。


---

## 为什么选择 ZMQ？

- **速度快。** 采用二进制发布/订阅模式，无序列化开销。控制循环以物理线程频率（通常为 500–1000 Hz）运行，不会因消息编码而出现瓶颈。
- **依赖项极少。** libzmq是插件内部唯一的网络依赖项。无需 ROS、中间件或构建系统集成。
- **用户选择。** 该插件不强制要求使用机器人框架。ZMQ 是原生传输协议；如果您需要 ROS 2，则可以使用单独的 urlab_bridge 进行转换。如果您需要纯 Python 代码，只需使用 `pyzmq` 即可。如果您需要其他格式，二进制格式也很容易解析。

---

## 插件端组件

三个组件负责网络连接。BeginPlay 时如果 `AAMjManager` 上还没有任何 ZMQ 组件，会自动创建 `UZmqSensorBroadcaster` 和 `UZmqControlSubscriber`：

| 组件 | 套接字 | 默认端点 | 目的 |
|-----------|--------|-------------------|---------|
| `UZmqSensorBroadcaster` | PUB | `tcp://*:5555` | 发布传感器数据、关节状态、扭转、动作 |
| `UZmqControlSubscriber` | SUB + PUB | `tcp://*:5556` (SUB), `tcp://*:5557` (info PUB) | 接收控制向量和增益更新；发布执行器信息 JSON |
| `UMjCamera` (ZMQ mode) | PUB | per-camera endpoint | 在专用线程上流式传输渲染的相机帧（使用 `SCS_FinalToneCurveHDR` 捕获源，因此会考虑后处理体积） |

所有虚幻引擎端的套接字都使用 `zmq_bind()` 函数。外部客户端使用 `zmq_connect()` 函数。

### 时间顺序

ZMQ回调直接在物理线程上运行:

1. **PreStep（前置步骤）** — `UZmqControlSubscriber` 读取传入指令 → 写入 `mjData.ctrl`
2. **mj_step()** — 执行物理步骤（仿真推进）
3. **PostStep（后置步骤）** — `UZmqSensorBroadcaster` 读取 `mjData` →发布

指令与响应之间存在单步延迟。相机画面在独立的后台线程中运行，因此不会阻塞物理循环。

### 话题（传感器广播）
所有消息均为多部分组成：主题字符串+二进制有效负载。话题以铰链参与者名称作为前缀：

| 话题模式 | 有效负载 | 来源 |
|---------------|---------|--------|
| `{Name}/joint/{JointName}` | `int32 id, float pos, float vel, float acc` (16 bytes) | `UMjJoint::BuildBinaryPayload` |
| `{Name}/sensor/{SensorName}` | `int32 id, float[] values` (4 + 4*dim bytes) | `UMjSensor::BuildBinaryPayload` |
| `{Name}/base_state/{JointName}` | `7 x float64` (pos xyz + quat wxyz) | `UMjFreeJoint::BuildBinaryPayload` |
| `{Name}/twist` | `3 x float32`: vx, vy, yaw_rate | TwistController |
| `{Name}/actions` | `int32` bitmask | TwistController (仅非零时发送) |

### 话题（控制接收）

控制订阅器会对 `{Name}/control` 和 `{Name}/set_gains` 进行话题过滤：

| 话题模式  | 有效负载  |
|---------------|---------|
| `{Name}/control` | `int32 count`, then `count` x `(int32 actuator_id, float value)` |
| `{Name}/set_gains` | JSON: `{"joint_name": {"kp": float, "kv": float, "torque_limit": float}, ...}` |

### 信息广播（端口 5557）
控制订阅器会通过信息端点周期性发布 JSON 格式的发现消息，内容包含执行器名称、ID、取值范围以及相机端点。启动阶段发送频率较高（前 5 秒内每 50 个物理步发送一次），之后改为每 500 个物理步发送一次（约 1 秒）。

> **多铰链过滤：** 在多机器人场景中，使用铰链名称前缀进行订阅（例如 `sub.setsockopt_string(zmq.SUBSCRIBE, "Robot_A/")`），即可仅接收对应机器人的数据。

### 控制源
`EControlSource` 用于确定执行器是响应 ZMQ 指令还是仪表板输入。可在管理器上进行全局设置，也可按单个铰链体分别设置：

```
Manager->SetControlSource(EControlSource::ZMQ);
```

---

## urlab_bridge （ROS 2）
**urlab_bridge**（独立的配套仓库，同一个 GitHub 组织）是 Python 端的中间件。它位于插件的 ZMQ 流和任何外部系统（ROS 2、强化策略、自定义脚本）之间：

```
Unreal (ZMQ binary) → urlab_bridge → ROS 2 topics
```

它订阅 ZMQ 传感器和相机端点，解包二进制有效负载，并发布到标准 ROS 2 话题（`/joint_states`、`/sensor_data`、`/camera/image_raw`）。多机器人的命名空间会自动处理。

**为什么要单独建立渠道？**

* 保持Unreal插件免受ROS构建依赖（如ament、colcon等）
* 桥接器是基于 `pyzmq` + `rclpy` 的纯 Python 实现——安装简单，修改也容易
* 不需要ROS的用户根本不用考虑
* 需要ROS的用户则获得标准话题界面，无需插件更改


### 快速测试（无需ROS）

```bash
uv run src/zmq_visualizer.py \
    --main_endpoint="tcp://127.0.0.1:5555" \
    --camera_endpoint="tcp://127.0.0.1:5558"
```

打印实时关节状态，并打开 OpenCV 窗口以显示相机帧

### ROS 2 转发器

```bash
# Source your ROS 2 environment first (Humble, Jazzy, etc.)
uv run src/ros2_broadcaster.py \
    --main_endpoint="tcp://127.0.0.1:5555" \
    --camera_endpoint="tcp://127.0.0.1:5558"
```

---

## 从Python连接

简单的 `pyzmq` 例子:

```python
import zmq, struct, numpy as np

ctx = zmq.Context()

# Receive sensor data (Unreal binds, we connect)
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:5555")
sub.setsockopt_string(zmq.SUBSCRIBE, "MyRobot/")

# Send controls (Unreal binds SUB on 5556, we connect PUB)
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://127.0.0.1:5556")

while True:
    topic, data = sub.recv_multipart()
    topic_str = topic.decode()

    if "/joint/" in topic_str:
        jid, pos, vel, acc = struct.unpack("<Ifff", data)
        print(f"Joint {jid}: pos={pos:.3f}")

    # Send control: 3 actuators example
    num = 3
    payload = struct.pack("<I", num)  # count
    for i in range(num):
        payload += struct.pack("<If", i, 0.0)  # (id, value) pairs
    pub.send_multipart([b"MyRobot/control ", payload])
```

---

## 故障排除

**没有数据到达** — 检查端点是否匹配（协议、IP、端口）。所有虚幻引擎端的套接字都*绑定*（bind）；外部客户端*连接*（connect）。

**控制不起作用** — 确认 `ControlSource` 已设置为 `ZMQ`。注意，控制话题的订阅过滤器需要带一个尾部空格（例如 `"MyRobot/control "`）。

**相机帧空白** — 确保相机组件上设置了 `bEnableZmqBroadcast = true`，并且模型已成功编译。

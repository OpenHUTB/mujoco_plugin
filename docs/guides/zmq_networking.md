# ZMQ 网络与 ROS 2


Unreal Robotics Lab 使用 [ZeroMQ](https://zeromq.org) 进行所有外部通信。其设计理念是：保持虚幻引擎端快速、二进制且无依赖——然后由一个独立的桥接器负责将其转换为用户偏好的任何框架。


---

## 为什么选择 ZMQ？

- **速度快。** 采用二进制发布/订阅模式，无序列化开销。控制循环以物理线程频率（通常为 500–1000 Hz）运行，不会因消息编码而出现瓶颈。
- **依赖项极少。** libzmq是插件内部唯一的网络依赖项。无需 ROS、中间件或构建系统集成。
- **用户选择。** 该插件不强制要求使用机器人框架。ZMQ 是原生传输协议；如果您需要 ROS 2，则可以使用单独的 urlab_bridge 进行转换。如果您需要纯 Python 代码，只需使用 `pyzmq` 即可。如果您需要其他格式，二进制格式也很容易解析。

---

## 插件端组件

三个组件负责网络连接，如果 `AAMjManager` 在 BeginPlay 时不存在，则所有组件都会自动创建：

| 组件 | 套接字 | 默认端点 | 目的 |
|-----------|--------|-------------------|---------|
| `UZmqSensorBroadcaster` | PUB | `tcp://*:5555` | 发布传感器数据、关节状态、扭转、动作 |
| `UZmqControlSubscriber` | SUB + PUB | `tcp://*:5556` (SUB), `tcp://*:5557` (info PUB) | 接收控制向量和增益更新；发布执行器信息 JSON |
| `UMjCamera` (ZMQ mode) | PUB | per-camera endpoint | 在专用线程上流式传输渲染的相机帧（使用 `SCS_FinalToneCurveHDR` 捕获源，因此会考虑后处理体积） |

所有虚幻引擎端的套接字都使用 `zmq_bind()` 函数。外部客户端使用 `zmq_connect()` 函数。

### 时序

ZMQ 回调直接运行在物理线程上：

1. **PreStep** — `UZmqControlSubscriber` 读取传入命令 → 写入 `mjData.ctrl`
2. **mj_step()** — 物理推进
3. **PostStep** — `UZmqSensorBroadcaster` 读取 `mjData` → 发布
命令与响应之间固定为一个时间步的延迟。相机帧在独立后台线程运行，因此不会阻塞物理循环。

###主题（传感器广播）

所有消息都是多部分：主题字符串 + 二进制负载。
主题以机械臂 Actor 名称为前缀：

| Topic Pattern | Payload | Source |
|---------------|---------|--------|
| `{Name}/joint/{JointName}` | `int32 id, float pos, float vel, float acc` (16 字节) | `UMjJoint::BuildBinaryPayload` |
| `{Name}/sensor/{SensorName}` | `int32 id, float[] values` (4 + 4*dim 字节) | `UMjSensor::BuildBinaryPayload` |
| `{Name}/base_state/{JointName}` | `7 x float64` (位置 xyz + 四元数 wxyz) | `UMjFreeJoint::BuildBinaryPayload` |
| `{Name}/twist` | `3 x float32`: vx, vy, yaw_rate | TwistController |
| `{Name}/actions` | `int32` 位掩码 | TwistController (only sent when non-zero) |

### 主题（控制接收）

控制订阅者过滤 {Name}/control 和 {Name}/set_gains：

| Topic Pattern | Payload |
|---------------|---------|
| `{Name}/control` | `int32 count`, then `count` x `(int32 actuator_id, float value)` |
| `{Name}/set_gains` | JSON: `{"joint_name": {"kp": float, "kv": float, "torque_limit": float}, ...}` |

### 信息广播（端口 5557）
控制订阅者定期在 info 端点上发布一个 JSON 发现消息，包含执行器名称、ID、范围以及相机端点。启动时频繁发送（前 5 秒内每 50 步一次），之后每 500 步（约 1 秒）一次。

> **多机械臂过滤:** 在多机器人场景中，使用机械臂名称前缀订阅（例如 sub.setsockopt_string(zmq.SUBSCRIBE, "Robot_A/")）以仅接收该机器人的数据。

### 控制源

`EControlSource`  决定执行器响应 ZMQ 还是仪表盘输入
可在管理器上全局设置，或按每个机械臂设置：
```
Manager->SetControlSource(EControlSource::ZMQ);
```

---

## urlab_bridge (ROS 2)

**urlab_bridge** 同一 GitHub 组织下的独立配套仓库）是 Python 端的中间件。它位于插件的 ZMQ 数据流与任何外部系统（ROS 2、强化学习策略、自定义脚本）之间：

```
Unreal (ZMQ binary) → urlab_bridge → ROS 2 topics
```

它订阅 ZMQ 传感器和相机端点，解包二进制负载，并发布到标准 ROS 2 话题 (`/joint_states`, `/sensor_data`, `/camera/image_raw`). 多机器人命名空间会自动处理。

**为什么使用独立的桥接器？**

- 保持虚幻引擎插件无需 ROS 构建依赖（ament、colcon 等）
- 桥接器是纯 Python，使用 pyzmq + rclpy — 易于安装，易于修改
- 不需要 ROS 的用户永远不必考虑它
- 需要 ROS 的用户无需任何插件更改即可获得标准话题接口

### 快速测试（无需 ROS）

```bash
uv run src/zmq_visualizer.py \
    --main_endpoint="tcp://127.0.0.1:5555" \
    --camera_endpoint="tcp://127.0.0.1:5558"
```

实时打印关节状态并打开一个 OpenCV 窗口显示相机画面。
### ROS 2 rebroadcaster

```bash
# 先加载您的 ROS 2 环境（Humble、Jazzy 等）
uv run src/ros2_broadcaster.py \
    --main_endpoint="tcp://127.0.0.1:5555" \
    --camera_endpoint="tcp://127.0.0.1:5558"
```

---

## 从 Python 连接
最简 `pyzmq` 示例：
```python
import zmq, struct, numpy as np

ctx = zmq.Context()

#  接收传感器数据（Unreal 绑定，我们连接）
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:5555")
sub.setsockopt_string(zmq.SUBSCRIBE, "MyRobot/")

# 发送控制（Unreal 在 5556 上绑定 SUB，我们连接 PUB）
pub = ctx.socket(zmq.PUB)
pub.connect("tcp://127.0.0.1:5556")

while True:
    topic, data = sub.recv_multipart()
    topic_str = topic.decode()

    if "/joint/" in topic_str:
        jid, pos, vel, acc = struct.unpack("<Ifff", data)
        print(f"Joint {jid}: pos={pos:.3f}")

    # 发送控制：3 个执行器示例
    num = 3
    payload = struct.pack("<I", num)  # count
    for i in range(num):
        payload += struct.pack("<If", i, 0.0)  # (id, value) pairs
    pub.send_multipart([b"MyRobot/control ", payload])
```

---

## 故障排除
**无数据到达** —检查端点是否匹配（协议、IP、端口）。所有虚幻引擎端套接字均执行*bind*; 外部客户端执行*connect*.

**控制无效** —确认`ControlSource` 已设置为 `ZMQ`. 注意控制主题在订阅过滤器中需要尾部空格 (例如, `"MyRobot/control "`).

**相机帧空白** — 确保相机组件上`bEnableZmqBroadcast = true` 且模型编译成功。
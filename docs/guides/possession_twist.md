# 持有和扭转控制

URLab 关节是虚幻引擎的棋子——它们可以被玩家控制器控制，从而实现直接输入控制。扭转控制器可以捕获WASD/游戏手柄输入，并通过 ZMQ 广播速度指令。

## 持有关节

**在 MjSimulate 小部件中：** 点击关节选择器旁边的**持有(Possess)**按钮。该按钮会在被控制时切换为**释放(Release)**状态。

**来自 蓝图/C++:**
```cpp
APlayerController* PC = GetWorld()->GetFirstPlayerController();
PC->Possess(MyArticulation);
// 之后
PC->UnPossess();
```

当持有时：

- 添加增强型**输入映射上下文**（Input mapping context, IMC） (`IMC_TwistControl`)

- 弹簧臂 + 摄像头连接到根 MjBody 以实现跟随摄像头功能

- WASD/QE 输入信号传输至扭转控制器

当释放时：

- 映射上下文已移除，扭曲状态已清零

- 相机组件已清理

- 原始棋子已重新获得控制权


## UMjTwistController

每次 AMjArticulation 操作在 BeginPlay 时自动创建。捕获输入并存储线程安全的扭转状态。

**属性（可在“详细信息”面板或通过移动滑块编辑）：**

| 属性 | 默认值 | 描述 |
|----------|---------|-------------|
| `MaxVx` | 0.8 米/秒 | 最大前进速度 |
| `MaxVy` | 0.5 米/秒 | 最大横向移动速度 |
| `MaxYawRate` | 1.57 弧度/秒 | 最大转弯率 |

**输入映射：**

| 键 | 操作 |
|-----|--------|
| W/S | 前进/后退 |
| A/D | 左右扫射 |
| Q/E | 左转/右转 |
| 1-0 | 操作键（10槽位位掩码） |

**ZMQ 广播：** 传感器广播器在每个物理步骤中发布扭矩状态：

| 主题 | 有效载荷 |
|-------|---------|
| `<prefix>/twist` | `3 x float32`: vx (m/s), vy (m/s), yaw_rate (rad/s) |
| `<prefix>/actions` | `int32` 按下的操作键的 int32 位掩码 |

## 跟随相机

获得控制权后，一个弹簧臂+摄像机组件会附加到根 MjBody 上：

- **摄像机延迟**: 速度 8，启用旋转延迟以实现平滑跟踪
- **臂长**: 后方 300 个单位，上方 100 个单位
- 已标记 `PossessCamera` 以便在发布时进行清理

摄像机跟随实际物理物体的位置，而不是静态的参与者者根位置。


## 连接到策略

Python 策略桥接器通过**扭矩控制类**`UnrealTwistCtrl` 读取 Twist 命令：

```python
# 在 policy_gui.py 中，Twist 控制器伪装成 JoystickCtrl。
# 因此，Unitree 策略的 _get_commands() 函数可以找到坐标轴数据。
ctrl_list = [UnrealTwistCtrlCfg()]
```

扭转值对应策略指令：

- `vx` → 前进速度指令

- `vy` → 侧向速度指令

- `yaw_rate` →  转弯指令

该策略将这些解读为步行方向/速度。

## 移动滑块

当在 MjSimulate 小部件中选择带有 TwistController 的关节时，会出现一个**移动**部分，其中包含三个滑块：

- **最大前进速度** (0.0 – 2.0 米/秒)
- **最大平移速度** (0.0 – 1.0 米/秒)
- **最大转弯速率** (0.0 – 3.14 弧度/秒)

这些参数控制着完整按键按下时产生的力度。

## 全局模拟热键

请参阅 [快捷键](blueprint_reference.md#hotkeys) 了解所有键盘快捷键。

## MjKeyframeCameraActor

对于脚本化的相机操作（例如拍摄演示），请使用 `MjKeyframeCameraActor` 而不是附身跟随镜头。它会播放预定义的镜头关键帧并进行插值，且不受任何被持有棋子的影响。

## 输入资产

位于 `Content/Input/` 目录下：

- `IA_TwistMove` — Axis2D 输入动作 (WASD)

- `IA_TwistTurn` — Axis1D 输入动作 (Q/E)

- `IMC_TwistControl` — 输入映射上下文绑定两个动作

创建 TwistController 时，从插件内容自动加载。

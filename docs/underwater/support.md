# 水下机器人 MuJoCo 仿真模块

本文档面向**新 clone 仓库的人**，目标是按下面步骤操作后，能够直接跑通水下仿真、看到图表，并在需要时打开 MuJoCo Viewer。

---

## 最小运行路径

### 1）准备依赖

在纯 Windows 环境下，先安装 Python 依赖：

```bash
pip install mujoco matplotlib numpy
```

### 2）确认 Menagerie 模型已自带

本仓库已经自带 `assets/mujoco_menagerie/`，新 clone 后请直接确认下面两个目录存在：

```bash
assets/mujoco_menagerie/universal_robots_ur5e/
assets/mujoco_menagerie/robotiq_2f85/
```

只要这两个目录存在，并且里面有对应的 mesh 文件（`universal_robots_ur5e/assets/` 下的 `.obj` 与 `robotiq_2f85/assets/` 下的 `.stl`），就可以继续往下跑。

### 3）运行唯一推荐入口

进入仓库后，直接运行：

```bash
python src/underwater/underwater_sim.py
```

这个脚本是**唯一推荐入口**。首次运行时，如果 `data/underwater_rov_with_arm.xml` 还不存在，会先自动完成模型拼装（UR5e + 夹爪 → 挂到 ROV 底座，不弹出 Viewer），然后按顺序执行：

1. 四组基础流体场景对比（含洋流）
2. 6-DOF 各向异性阻力测试
3. PID 深度悬浮控制测试
4. 是否启动 MuJoCo Viewer 的交互验证

### 4）选择是否打开 Viewer

脚本跑完后台测试后，会提示：

```text
所有后台物理测试完毕。是否启动交互式 Viewer 进行视觉验证？(y/n):
```

- 输入 `y`：打开 Viewer
- 输入 `n`：结束运行

---

## 项目结构

```text
mujoco_plugin/
├── src/
│   └── underwater/
│       ├── underwater_sim.py
│       ├── depth_controller.py
│       ├── plot_results.py
│       ├── build_underwater_rov.py
│       ├── ur5e_industrial_grasp.py
│       ├── arm_grasp_sandbox.py
│       └── data/
│           ├── config.json
│           ├── rov_base.xml
│           ├── underwater_rov_with_arm.xml
│           └── ur5e_scene.xml
├── assets/
│   └── mujoco_menagerie/
│       ├── universal_robots_ur5e/
│       └── robotiq_2f85/
└── docs/
    ├── img/
    └── underwater/
        └── README.md
```

---

## 架构图

```text
config.json
   │
   ├──────────────► underwater_sim.py
   │                    │
   │                    ├──────────────► depth_controller.py
   │                    │
   │                    ├──────────────► plot_results.py
   │                    │
   │                    └──────────────► 运行四类物理验证 + PID 悬浮 + Viewer
   │
   └──────────────► build_underwater_rov.py
                        │
                        └──────────────► underwater_rov_with_arm.xml
```

补充说明：

- `config.json` 提供密度、粘度、重力、仿真步长、ROV 尺寸和测试场景参数。
- `build_underwater_rov.py` 负责把 ROV 底座与 UR5e + 夹爪拼成完整模型。
- `underwater_sim.py` 是主控脚本，负责加载模型、跑测试、触发绘图、打开 Viewer。
- `depth_controller.py` 提供 PID 深度控制器。
- `plot_results.py` 负责把结果保存成图片。

---

## 各脚本职责

### `underwater_sim.py`

#### 输入
- `data/config.json`
- `data/underwater_rov_with_arm.xml`

#### 处理
- 读取配置
- `data/underwater_rov_with_arm.xml` 不存在时，调用 `build_underwater_rov.py` 自动生成
- 动态注入流体参数和物理参数
- 执行四组基础场景测试（含洋流）
- 执行 6-DOF 各向异性阻力测试
- 执行 PID 悬浮控制测试
- 询问是否打开 Viewer

#### 输出
- `docs/img/underwater_test_results.png`
- `docs/img/anisotropic_drag_test.png`
- `docs/img/depth_control_result.png`
- MuJoCo Viewer 窗口

### `depth_controller.py`

#### 输入
- 目标深度
- 当前深度
- 时间步长 `dt`

#### 处理
- 计算 PID 误差
- 做积分限幅，避免积分发散
- 做推力限幅，避免输出过大

#### 输出
- Z 轴推力值

### `plot_results.py`

#### 输入
- 仿真记录的时间序列、深度、速度等数据

#### 处理
- 使用 Matplotlib 绘制结果图
- 保存成 PNG

#### 输出
- 三张结果图，自动保存到 `docs/img/`

### `build_underwater_rov.py`

#### 输入
- `data/rov_base.xml`
- `assets/mujoco_menagerie/universal_robots_ur5e/ur5e_with_gripper.xml`（每次运行时先调用 `ur5e_industrial_grasp.py` 重新生成）

#### 处理
- 解析 XML 树
- 把 UR5e 机械臂挂到 ROV 上
- 把 mesh 路径改成绝对路径
- 合并 asset / actuator / sensor / contact 等标签
- 增加碰撞排除对
- 输出完整装配体

#### 输出
- `data/underwater_rov_with_arm.xml`

### `ur5e_industrial_grasp.py`

#### 输入
- `assets/mujoco_menagerie/universal_robots_ur5e/ur5e.xml`
- `assets/mujoco_menagerie/robotiq_2f85/2f85.xml`
- `data/ur5e_scene.xml`

#### 处理
- 给夹爪元素统一加前缀，避免命名冲突
- 在 UR5e 末端挂载夹爪
- 合并场景和资源
- 启动 Viewer

#### 输出
- `ur5e_with_gripper.xml`
- `industrial_scene.xml`
- MuJoCo Viewer 窗口

### `arm_grasp_sandbox.py`

#### 输入
- 无外部文件依赖，模型直接写在脚本里

#### 处理
- 从内嵌 MJCF 字符串编译模型
- 通过 MuJoCo 控制回调，用余弦平滑轨迹驱动机械臂完成抓取演示：
    1. 0–2 s：从竖直初始姿态移动到小球正上方
    2. 2–3 s：夹爪竖直朝下下探，两指包住小球
    3. 3–4 s：收拢夹爪夹紧小球
    4. 4–6 s：把小球举到约 0.27 m 高，之后保持该姿态
- 摩擦锥采用 `cone="elliptic"`、`impratio="10"`：默认的金字塔锥下软接触蠕滑明显，小球举起后十几秒就会滑落

在 Viewer 中按 `Backspace` 重置仿真后，动作会从头重新播放。

#### 输出
- MuJoCo Viewer 窗口

#### 运行

```bash
python src/underwater/arm_grasp_sandbox.py
```

---

## 物理验证内容

这个模块保留了四类核心物理验证。

### 1）基础流体场景对比

对比三种场景：

- 无流体环境：纯重力下沉
- 水中环境：只看流体阻力
- 水中环境：流体阻力 + 手动浮力补偿

这部分会生成 `underwater_test_results.png`。

### 2）6-DOF 各向异性阻力验证

通过脉冲阶跃力测试不同方向上的阻力差异，用来观察：

- 纵向平移
- 横向平移
- 横向翻滚

这部分会生成 `anisotropic_drag_test.png`。

### 3）PID 深度悬浮验证

通过深度控制器做闭环悬浮测试，观察目标深度与实际深度的跟踪效果。

这部分会生成 `depth_control_result.png`。

### 4）洋流干扰场景测试

在洋流环境中测试 PID 深度保持和无控制漂移情况：

- **洋流+PID 深度保持** — 洋流存在时 PID 控制器的深度跟踪能力
- **洋流漂移** — 无控制时洋流对机器人的拖曳漂移效果

这部分会生成额外的 `ocean_current_speed.png`（洋流速度曲线图）。

---

## 为什么浮力要手动加

MuJoCo 的流体参数主要负责阻力和相关流体效应，浮力这里采用手动注入方式实现。  
所以仿真里会在每一步通过 `xfrc_applied` 施加向上的浮力，这也是这个模块里最关键的一点。

---

## 常见问题

### 1）找不到 Menagerie 模型

先确认下面两个目录是否存在：

```bash
assets/mujoco_menagerie/universal_robots_ur5e/
assets/mujoco_menagerie/robotiq_2f85/
```

如果目录缺失或里面没有 mesh 文件，就先把仓库自带资源补齐，再运行主脚本。

### 2）`underwater_rov_with_arm.xml` 没生成

这通常说明模型资源没准备完整，或者模型拼接流程中某个 XML 文件缺失。  
先确认 Menagerie 目录存在，再重新运行：

```bash
python src/underwater/underwater_sim.py
```

`underwater_sim.py` 只在装配体缺失时自动生成。修改了 `data/rov_base.xml` 或 Menagerie 模型后，删除 `data/underwater_rov_with_arm.xml` 再运行主脚本，或直接运行 `python src/underwater/build_underwater_rov.py`（生成后会打开 Viewer）即可重新生成。

### 3）Viewer 打不开

Viewer 是可选步骤，不影响前面的物理测试和图片生成。  
先确认前面三张图是否已经保存到 `docs/img/`，再决定是否重试 Viewer。

### 4）图表没保存

先检查：

- `docs/img/` 目录是否存在
- 当前用户是否对仓库目录有写权限
- 脚本是否正常执行结束

如果后台测试中途报错，图表也不会生成。

---

## 输出产物

运行完成后，`docs/img/` 下会生成：

- `underwater_test_results.png` — 基础流体场景对比
- `anisotropic_drag_test.png` — 6-DOF 各向异性阻力
- `depth_control_result.png` — PID 深度悬浮控制
- `ocean_current_speed.png` — 洋流速度曲线（洋流模块启用时）

---

## 参考

- [MuJoCo 流体受力官方文档](https://mujoco.readthedocs.io/en/stable/computation/fluid.html)
- [MuJoCo Menagerie 官方模型资源](https://github.com/google-deepmind/mujoco_menagerie)
- [UNav-Sim 水下机器人仿真相关资料](https://github.com/open-airlab/UNav-Sim)

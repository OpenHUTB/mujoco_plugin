import os
import mujoco
import mujoco.viewer
import numpy as np

# ──────────────────────────────────────────────────────────────────
# 💡 核心物理骨架定义 (内嵌 MJCF 字符串)
# 解释：
# 1. 采用通用 6 自由度串联运动学架构（底座旋转+大臂偏航+小臂偏航+腕部3自由度）。
# 2. 核心求解器微调：设置 solref="0.01 1" 和 solimp="0.95 0.99 0.001"。
#    这会把刚性碰撞软化为高度阻尼的弹簧接触，彻底吸收物体碰撞瞬间的动能，防止弹飞。
# 3. 增大摩擦系数 friction="1.5 0.005 0.0001"，为末端夹爪提供极强的切向和扭转摩擦，防止小球异常旋转。
# 4. 摩擦锥采用 cone="elliptic" 并设置 impratio="10"：默认的金字塔锥下软接触蠕滑明显，
#    夹住的小球举起后十几秒就会滑落；椭圆锥 + 较大的 impratio 是 MuJoCo 推荐的抓取配置，可稳定夹持。
# ──────────────────────────────────────────────────────────────────
MJCF_ARM_SANDBOX = """
<mujoco model="underwater_arm_sandbox">
    <compiler angle="degree" coordinate="local"/>
    <option timestep="0.002" gravity="0 0 -9.81" cone="elliptic" impratio="10"/>
    
    <default>
        <joint armature="0.05" damping="5" stiffness="0"/>
        <geom condim="4" friction="1.5 0.005 0.0001" solref="0.01 1" solimp="0.95 0.99 0.001" rgba="0.8 0.8 0.8 1"/>
        <position ctrlrange="-180 180" kp="400"/>
    </default>

    <worldbody>
        <light directional="true" diffuse=".8 .8 .8" specular=".2 .2 .2" pos="0 0 5" dir="0 0 -1"/>
        <geom name="floor" type="plane" size="2 2 .25" rgba=".2 .3 .3 1"/>

        <body name="target_ball" pos="0.55 0 0.05">
            <freejoint name="ball_free"/>
            <geom name="ball_geom" type="sphere" size="0.03" mass="0.1" rgba="1 0 0 1"/>
        </body>

        <body name="base_link" pos="0 0 0">
            <geom name="base_geom" type="cylinder" size="0.1 0.05" pos="0 0 0.025"/>
            
            <body name="link1" pos="0 0 0.05">
                <joint name="joint1" type="hinge" axis="0 0 1"/>
                <geom name="link1_geom" type="cylinder" size="0.06 0.08" pos="0 0 0.04"/>
                
                <body name="link2" pos="0 0 0.08">
                    <joint name="joint2" type="hinge" axis="0 1 0" range="-90 90"/>
                    <geom name="link2_geom" type="box" size="0.04 0.04 0.2" pos="0 0 0.2"/>
                    
                    <body name="link3" pos="0 0 0.4">
                        <joint name="joint3" type="hinge" axis="0 1 0" range="-120 120"/>
                        <geom name="link3_geom" type="box" size="0.03 0.03 0.15" pos="0 0 0.15"/>
                        
                        <body name="link4" pos="0 0 0.3">
                            <joint name="joint4" type="hinge" axis="0 1 0"/>
                            <geom name="link4_geom" type="cylinder" size="0.025 0.04" pos="0 0 0.04"/>
                            
                            <body name="link5" pos="0 0 0.08">
                                <joint name="joint5" type="hinge" axis="0 0 1"/>
                                <geom name="link5_geom" type="box" size="0.02 0.02 0.04" pos="0 0 0.04"/>
                                
                                <body name="link6" pos="0 0 0.08">
                                    <joint name="joint6" type="hinge" axis="0 1 0"/>
                                    <geom name="link6_geom" type="box" size="0.04 0.015 0.01" pos="0 0 0.005" rgba="0.2 0.2 0.2 1"/>
                                    
                                    <body name="left_finger" pos="0 -0.06 0.01">
                                        <joint name="joint_left_finger" type="slide" axis="0 1 0" range="0 0.55"/>
                                        <geom name="left_finger_geom" type="box" size="0.005 0.008 0.04" pos="0 0 0.04" rgba="0.3 0.3 0.3 1"/>
                                    </body>
                                    
                                    <body name="right_finger" pos="0 0.06 0.01">
                                        <joint name="joint_right_finger" type="slide" axis="0 -1 0" range="0 0.55"/>
                                        <geom name="right_finger_geom" type="box" size="0.005 0.008 0.04" pos="0 0 0.04" rgba="0.3 0.3 0.3 1"/>
                                    </body>
                                </body>
                            </body>
                        </body>
                    </body>
                </body>
            </body>
        </body>
    </worldbody>

    <actuator>
        <position name="act_j1" joint="joint1" ctrlrange="-180 180"/>
        
        <position name="act_j2" joint="joint2" ctrlrange="0 1.5"/>
        <position name="act_j3" joint="joint3" ctrlrange="0 1.5"/>
        
        <position name="act_j4" joint="joint4" ctrlrange="-1 1"/>
        <position name="act_j5" joint="joint5" ctrlrange="-1 1"/>
        <position name="act_j6" joint="joint6" ctrlrange="-1 1"/>
        
        <position name="act_f_left" joint="joint_left_finger" ctrlrange="0 0.06" kp="800"/>
        <position name="act_f_right" joint="joint_right_finger" ctrlrange="0 0.06" kp="800"/>
    </actuator>
</mujoco>
"""

# ──────────────────────────────────────────────────────────────────
# 抓取动作的关键姿态 (Target Positions)，顺序与 <actuator> 一致：
#   [j1, j2, j3, j4, j5, j6, 左指, 右指]，关节单位为弧度，手指单位为米
# 手臂在 XZ 平面内工作 (j1 = j5 = 0)，j2、j3、j4、j6 由逆运动学求得：
#   两指中点对准目标高度、夹爪竖直朝下；j4 已到执行器上限 1 rad，余量由 j6 补偿。
# 位置执行器在重力作用下存在稳态误差，实际位置比下面注释中的目标高度低约 1.5 cm。
# ──────────────────────────────────────────────────────────────────
CTRL_HOME = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
# 预抓取：两指中点位于小球正上方 z = 0.17 m，避免下探途中扫到小球
CTRL_PREGRASP = [0.0, 0.585, 1.287, 1.0, 0.0, 0.269, 0.0, 0.0]
# 下探：两指中点目标 z = 0.06 m，下沉后指尖刚好不触地，手指覆盖小球球心高度 (z = 0.03 m)
CTRL_REACH = [0.0, 0.772, 1.311, 1.0, 0.0, 0.059, 0.0, 0.0]
# 夹紧：手指滑移约 0.022 m 时接触半径 0.03 m 的小球，指令取 0.03 m，
# 由位置执行器 (kp=800) 的剩余误差产生约 6 N 的夹持力
GRIP_CLOSED = 0.03
CTRL_CLAMP = CTRL_REACH[:6] + [GRIP_CLOSED, GRIP_CLOSED]
# 举起：保持夹爪竖直，两指中点升至 z = 0.30 m
CTRL_LIFT = [0.0, 0.430, 1.164, 1.0, 0.0, 0.548, GRIP_CLOSED, GRIP_CLOSED]

# 动作时间表：(起始姿态, 目标姿态, 持续时间 s)，结束后保持 CTRL_LIFT
GRASP_SEGMENTS = [
    (CTRL_HOME, CTRL_PREGRASP, 2.0),   # 0~2 s：从竖直初始姿态移动到小球正上方
    (CTRL_PREGRASP, CTRL_REACH, 1.0),  # 2~3 s：竖直下探，让手指包住小球
    (CTRL_REACH, CTRL_CLAMP, 1.0),     # 3~4 s：保持手臂不动，收拢夹爪
    (CTRL_CLAMP, CTRL_LIFT, 2.0),      # 4~6 s：夹持小球竖直举起
]


def smooth_interp(start, end, progress):
    """余弦缓动 (Cosine Easing)，让电机的启动和停止像真实机械臂一样丝滑"""
    progress = np.clip(progress, 0.0, 1.0)
    ease = (1.0 - np.cos(progress * np.pi)) / 2.0
    return start + (end - start) * ease


def scripted_grasp_ctrl(t):
    """返回时刻 t (s) 的执行器目标：把离散的关键姿态转化为基于时间的连续平滑轨迹"""
    for start, end, duration in GRASP_SEGMENTS:
        if t < duration:
            return smooth_interp(np.array(start), np.array(end), t / duration)
        t -= duration
    return np.array(CTRL_LIFT)


class ArmGraspSandbox:
    def __init__(self):
        # 从内嵌字符串直接编译模型，消除外部依赖文件
        self.model = mujoco.MjModel.from_xml_string(MJCF_ARM_SANDBOX)
        self.data = mujoco.MjData(self.model)

    @staticmethod
    def controller_callback(model, data):
        """MuJoCo 控制回调：每个仿真步按当前仿真时间写入执行器目标"""
        data.ctrl[:] = scripted_grasp_ctrl(data.time)

    def execute_scripted_grasp(self):
        """控制机械臂顺序执行：移到上方 -> 竖直下探 -> 稳定夹紧 -> 垂直举起目标物体"""
        print("=" * 60)
        print("  正在拉起多自由度机械臂物理接触控制沙盒...")
        print("  已启用 Cosine 平滑轨迹插补算法")
        print("=" * 60)

        # 控制回调是全局设置，关闭 Viewer 后需要清除，避免影响同一进程中的其他模型
        mujoco.set_mjcb_control(self.controller_callback)
        try:
            mujoco.viewer.launch(self.model, self.data)
        finally:
            mujoco.set_mjcb_control(None)


if __name__ == "__main__":
    sandbox = ArmGraspSandbox()
    sandbox.execute_scripted_grasp()

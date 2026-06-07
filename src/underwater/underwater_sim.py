"""
水下机器人力学模拟引擎层 (Simulator)
=====================================
职责：加载装配体、步进物理计算、注入环境力、收集仿真测试数据
"""

import os
import json
import mujoco
import mujoco.viewer
import numpy as np
from pathlib import Path

# 导入解耦的控制器和可视化模块
from depth_controller import PIDDepthController
from plot_results import plot_basic_scenarios, plot_anisotropic_drag, plot_depth_tracking
from ocean_current import OceanCurrentCascade, apply_current_drag

_HERE = Path(__file__).resolve().parent
_DEFAULT_CONFIG = _HERE / "data" / "config.json"
# 指向我们拼接了机械臂并修改了绝对路径的最终装配体
_DEFAULT_MODEL = _HERE / "data" / "underwater_rov_with_arm.xml"

class UnderwaterSimulation:
    def __init__(self, config_path=_DEFAULT_CONFIG, model_path=_DEFAULT_MODEL):
        # 读取参数化配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.model_path = str(model_path)

        # 预先计算几何特征
        rov_cfg = self.config["rov_body"]
        # 长方体体积计算公式 V = (2*dx) * (2*dy) * (2*dz)
        self.volume = (rov_cfg["half_size"][0] * 2) * (rov_cfg["half_size"][1] * 2) * (rov_cfg["half_size"][2] * 2)
        self.mass   = rov_cfg["mass"]
        self.g      = self.config["gravity"]

        # 实例化外置的 PID 控制器
        self.depth_controller = PIDDepthController(kp=1500.0, ki=10.0, kd=800.0)

        # 实例化洋流模型
        self.ocean_current = None
        oc_cfg = self.config.get("ocean_current", {})
        if oc_cfg.get("enabled", False):
            self.ocean_current = OceanCurrentCascade(oc_cfg)

    def load_and_setup_model(self, density, viscosity):
        """动态加载 XML 并注入配置文件中的流体力学参数"""
        model = mujoco.MjModel.from_xml_path(self.model_path)

        # 动态注入全局环境参数
        model.opt.gravity    = np.array([0, 0, -self.g])
        model.opt.timestep   = self.config["simulation_timestep"]
        model.opt.density    = density
        model.opt.viscosity  = viscosity

        # 动态重载几何体物理特征 (注入长方体 3D 尺寸)
        rov_cfg = self.config["rov_body"]
        geom_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, rov_cfg["geom_name"])
        model.geom_size[geom_id] = rov_cfg["half_size"]
        model.body_mass[model.geom_bodyid[geom_id]] = self.mass
        model.geom_fluid[geom_id, :5] = np.array(rov_cfg["fluid_coef"])

        return model

    def init_robot_pose(self, model, data):
        """设定机械臂初始收纳姿态 (同步物理位置与控制器目标)"""
        # 数据来源：基于 GUI 调试截取的完美收纳参数
        target_pose = {
            "shoulder_pan_joint": ("shoulder_pan", -0.0628),
            "shoulder_lift_joint": ("shoulder_lift", 0.126),
            "elbow_joint": ("elbow", -2.67),
            "wrist_1_joint": ("wrist_1", -0.691),
            "wrist_2_joint": ("wrist_2", -1.63),
            "wrist_3_joint": ("wrist_3", -3.27)
        }
        
        for jnt_name, (act_name, val) in target_pose.items():
            # 1. 设定物理关节初始位置 (qpos)
            jnt_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, jnt_name)
            if jnt_id != -1:
                data.qpos[model.jnt_qposadr[jnt_id]] = val
                
            # 2. 设定驱动器初始目标指令 (ctrl)，无需地址映射，直接索引
            act_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, act_name)
            if act_id != -1:
                data.ctrl[act_id] = val
                
        # 强制更新前向运动学状态
        mujoco.mj_forward(model, data)

    def run_scenario(self, density, viscosity, apply_buoyancy):
        """测试用例 1：执行基础场景的仿真并返回数据字典"""
        model   = self.load_and_setup_model(density, viscosity)
        data    = mujoco.MjData(model)
        
        # 注入初始收纳姿态
        self.init_robot_pose(model, data)
        
        body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "rov")

        # 计算静态阿基米德浮力
        buoyancy_force = density * self.g * self.volume if apply_buoyancy else 0.0

        log_t, log_z, log_vz = [], [], []
        steps = int(self.config["duration_seconds"] / model.opt.timestep)
        dt = model.opt.timestep
        # 洋流阻力系数 (kg/s)，可按需从 config 读取
        drag_coeff = self.config.get("ocean_drag_coeff", 10.0)

        for i in range(steps):
            # 1. 浮力
            if apply_buoyancy and density > 0:
                data.xfrc_applied[body_id, 2] = buoyancy_force

            # 2. 洋流拖曳力 (叠加在浮力之后)
            if self.ocean_current:
                robot_x, robot_y, robot_z = data.sensor("pos").data[:3]
                v_current = self.ocean_current.get_velocity(robot_x, robot_y, robot_z, dt)
                apply_current_drag(data, body_id, v_current, drag_coeff)

            mujoco.mj_step(model, data)

            if i % 5 == 0:
                log_t.append(data.time)
                log_z.append(data.sensor("pos").data[2])
                log_vz.append(data.sensor("vel").data[2])

        return np.array(log_t), np.array(log_z), np.array(log_vz)

    def test_anisotropic_drag(self):
        """测试用例 2：验证流体阻力的各向异性 (6-DOF 脉冲阶跃测试) 并返回数据字典"""
        print("\n" + "=" * 60)
        print("  正在执行：第二阶段目标 - 复杂受力与阻力衰减测试")
        print("=" * 60)

        density = self.config["fluid_density"]
        viscosity = self.config["fluid_viscosity"]
        buoyancy_force = density * self.g * self.volume

        scenarios = {
            "纵向平移 (端面迎水，阻力小)": {"force": [0, 0, 500, 0, 0, 0], "track_axis": 2},
            "横向平移 (侧面迎水，阻力大)": {"force": [500, 0, 0, 0, 0, 0], "track_axis": 0},
            "横向翻滚 (大面积拨水，角阻力)": {"force": [0, 0, 0, 0, 50, 0], "track_axis": 4}
        }

        drag_results = {}
        
        for label, config in scenarios.items():
            model = self.load_and_setup_model(density, viscosity)
            data = mujoco.MjData(model)
            
            # 注入初始收纳姿态
            self.init_robot_pose(model, data)
            
            body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "rov")
            
            # 安全反查 freejoint 的基地址，防止无名 joint 导致 IndexError
            joint_id = model.body_jntadr[body_id]
            qvel_addr = model.jnt_dofadr[joint_id]

            log_t, log_v = [], []
            steps = int(3.0 / model.opt.timestep)
            dt = model.opt.timestep
            drag_coeff = self.config.get("ocean_drag_coeff", 10.0)

            for i in range(steps):
                data.xfrc_applied[body_id, 2] = buoyancy_force
                
                if data.time < 0.1:
                    data.xfrc_applied[body_id] = np.array(config["force"])
                else:
                    data.xfrc_applied[body_id][:2] = 0.0
                    data.xfrc_applied[body_id][3:] = 0.0

                # 洋流拖曳力
                if self.ocean_current:
                    robot_x, robot_y, robot_z = data.sensor("pos").data[:3]
                    v_current = self.ocean_current.get_velocity(robot_x, robot_y, robot_z, dt)
                    apply_current_drag(data, body_id, v_current, drag_coeff)

                mujoco.mj_step(model, data)

                if i % 5 == 0:
                    log_t.append(data.time)
                    current_vel = data.qvel[qvel_addr + config["track_axis"]]
                    log_v.append(current_vel)
            
            drag_results[label] = (log_t, log_v)
            
        return drag_results

    def run_hover_test(self, target_depth=-1.0, duration=10.0):
        """测试用例 3：执行主动悬浮闭环控制测试并返回数据"""
        print(f"\n▶ 正在执行: 第三阶段目标 - 主动悬浮闭环控制测试 (目标深度: {target_depth}m)")
        model = self.load_and_setup_model(self.config["fluid_density"], self.config["fluid_viscosity"])
        data = mujoco.MjData(model)
        
        # 注入初始收纳姿态
        self.init_robot_pose(model, data)
        
        body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "rov")
        joint_id = model.body_jntadr[body_id]
        qpos_addr = model.jnt_qposadr[joint_id]
        
        buoyancy_force = model.opt.density * self.g * self.volume
        dt = model.opt.timestep
        steps = int(duration / dt)
        drag_coeff = self.config.get("ocean_drag_coeff", 10.0)

        log_t, log_z = [], []

        for i in range(steps):
            current_z = data.qpos[qpos_addr + 2]
            
            # 1. 叠加环境浮力
            data.xfrc_applied[body_id, 2] = buoyancy_force
            
            # 2. 洋流拖曳力 + 洋流前馈补偿
            v_current_z = 0.0
            if self.ocean_current:
                robot_x, robot_y, robot_z = data.sensor("pos").data[:3]
                v_current = self.ocean_current.get_velocity(robot_x, robot_y, robot_z, dt)
                apply_current_drag(data, body_id, v_current, drag_coeff)
                v_current_z = v_current[2]  # Z 分量用于前馈
                
            # 3. PID 闭环控制力（带洋流前馈补偿）
            thrust_z = self.depth_controller.compute(
                target_depth, current_z, dt, current_velocity=v_current_z)
            data.xfrc_applied[body_id, 2] += thrust_z

            mujoco.mj_step(model, data)

            if i % 10 == 0:
                log_t.append(data.time)
                log_z.append(current_z)
                
        return log_t, log_z

    def start_interactive_viewer(self):
        """启动 MuJoCo 交互窗口 (两阶段串行展示：无控制 vs PID控制)"""
        ans = input("\n所有后台物理测试完毕。是否启动交互式 Viewer 进行视觉验证？(y/n): ").strip().lower()
        if ans != 'y':
            return

        # ==========================================
        # 演示阶段一：无控制（纯正浮力上浮）
        # ==========================================
        print("\n" + "="*55)
        print(" ▶ 演示阶段 1/2：无控制（纯正浮力上浮）")
        print("="*55)
        
        model_passive = self.load_and_setup_model(self.config["fluid_density"], self.config["fluid_viscosity"])
        data_passive = mujoco.MjData(model_passive)
        self.init_robot_pose(model_passive, data_passive)
        
        body_id_passive = mujoco.mj_name2id(model_passive, mujoco.mjtObj.mjOBJ_BODY, "rov")
        buoyancy_force = self.config["fluid_density"] * self.g * self.volume
        drag_coeff = self.config.get("ocean_drag_coeff", 10.0)

        def passive_buoyancy_callback(m, d):
            d.xfrc_applied[body_id_passive, 2] = buoyancy_force
            if self.ocean_current:
                vx, vy, vz = d.sensor("pos").data[:3]
                v_cur = self.ocean_current.get_velocity(vx, vy, vz, m.opt.timestep)
                apply_current_drag(d, body_id_passive, v_cur, drag_coeff)

        mujoco.set_mjcb_control(passive_buoyancy_callback)
        mujoco.viewer.launch(model_passive, data_passive)
        
        # [关键修复]: 在关闭窗口后，必须注销全局回调，否则它会污染下一个阶段
        mujoco.set_mjcb_control(None) 


        # ==========================================
        # 演示阶段二：PID 闭环控制（动态悬停）
        # ==========================================
        print("\n" + "="*55)
        print(" ▶ 演示阶段 2/2：PID 闭环控制（绝对悬停）")
        print("="*55)

        model_active = self.load_and_setup_model(self.config["fluid_density"], self.config["fluid_viscosity"])
        data_active = mujoco.MjData(model_active)
        self.init_robot_pose(model_active, data_active)

        body_id_active = mujoco.mj_name2id(model_active, mujoco.mjtObj.mjOBJ_BODY, "rov")
        joint_id_active = model_active.body_jntadr[body_id_active]
        qpos_addr_active = model_active.jnt_qposadr[joint_id_active]
        target_depth = -1.5 
        
        self.depth_controller.integral_error = 0.0
        self.depth_controller.prev_error = 0.0

        def active_control_callback(m, d):
            d.xfrc_applied[body_id_active, 2] = buoyancy_force
            current_z = d.qpos[qpos_addr_active + 2]
            
            v_current_z = 0.0
            if self.ocean_current:
                vx, vy, vz = d.sensor("pos").data[:3]
                v_cur = self.ocean_current.get_velocity(vx, vy, vz, m.opt.timestep)
                apply_current_drag(d, body_id_active, v_cur, drag_coeff)
                v_current_z = v_cur[2]
            
            thrust_z = self.depth_controller.compute(
                target_depth, current_z, m.opt.timestep, current_velocity=v_current_z)
            d.xfrc_applied[body_id_active, 2] += thrust_z

        mujoco.set_mjcb_control(active_control_callback)
        mujoco.viewer.launch(model_active, data_active)
        
        # [关键修复]: 演示结束后同样注销
        mujoco.set_mjcb_control(None)
        
        print("\n✅ 所有视觉演示完毕！")
# ─────────────────────────────────────────────
# 统一测试调度入口
# ─────────────────────────────────────────────
if __name__ == "__main__":
    sim = UnderwaterSimulation()

    print("=" * 60)
    print("  水下机器人 MuJoCo 模块化物理仿真中枢")
    print("=" * 60)

    # 创建图片保存路径
    save_dir = str(_HERE.parents[1] / "docs" / "img")
    os.makedirs(save_dir, exist_ok=True)

    # ----- 1. 执行基础环境对比测试并画图 -----
    results = {}
    for _, sc in sim.config["test_scenarios"].items():
        print(f"\n▶ 正在执行: 第一阶段目标 - {sc['label']}")
        t, z, vz = sim.run_scenario(sc["density"], sc["viscosity"], sc["apply_buoyancy"])
        results[sc['label']] = (t, z, vz)
    
    # 触发外部渲染
    plot_basic_scenarios(results, save_dir)

    # ----- 2. 执行复杂受力 6-DOF 测试并画图 -----
    drag_results = sim.test_anisotropic_drag()
    
    # 触发外部渲染
    plot_anisotropic_drag(drag_results, save_dir)

    # ----- 3. 执行 PID 闭环悬浮控制测试并画图 -----
    target_z = -1.5
    hover_t, hover_z = sim.run_hover_test(target_depth=target_z, duration=15.0)
    
    # 触发外部渲染
    plot_depth_tracking(hover_t, hover_z, target_z, save_dir)

    # ----- 4. 洋流干扰测试 -----
    if sim.ocean_current:
        print("\n" + "=" * 60)
        print("  正在执行：第四阶段目标 - 洋流干扰场景测试")
        print("=" * 60)
        
        # 4a. 洋流中的 PID 深度保持（与无洋流对比）
        print("\n▶ 洋流 + PID 深度保持测试")
        hover_t_oc, hover_z_oc = sim.run_hover_test(
            target_depth=-1.0, duration=20.0)
        plot_depth_tracking(hover_t_oc, hover_z_oc, -1.0, save_dir)
        
        # 4b. 洋流漂移测试（无控制，记录洋流速度）
        print("\n▶ 洋流漂移测试（无控制）")
        oc = sim.ocean_current
        oc.reset()
        drift_t, drift_z, drift_vz = sim.run_scenario(
            sim.config["fluid_density"],
            sim.config["fluid_viscosity"],
            apply_buoyancy=True
        )
        
        # 记录洋流速度曲线
        from plot_results import plot_ocean_current
        if oc:
            # 重新运行一次，收集洋流速度数据
            from ocean_current import OceanCurrentCascade, apply_current_drag
            import mujoco as _mujoco
            model = sim.load_and_setup_model(sim.config["fluid_density"], sim.config["fluid_viscosity"])
            data = _mujoco.MjData(model)
            sim.init_robot_pose(model, data)
            body_id = _mujoco.mj_name2id(model, _mujoco.mjtObj.mjOBJ_BODY, "rov")
            buoyancy_force = sim.config["fluid_density"] * sim.g * sim.volume
            
            log_oc_t, log_oc_v = [], []
            steps = int(20.0 / model.opt.timestep)
            for i in range(steps):
                robot_x, robot_y, robot_z = data.sensor("pos").data[:3]
                v_cur = oc.get_velocity(robot_x, robot_y, robot_z, model.opt.timestep)
                log_oc_t.append(data.time)
                log_oc_v.append(np.linalg.norm(v_cur))
                
                data.xfrc_applied[body_id, 2] = buoyancy_force
                apply_current_drag(data, body_id, v_cur, 10.0)
                _mujoco.mj_step(model, data)
                
                if i % 10 == 0:
                    pass  # 已在上面记录
            
            plot_ocean_current(np.array(log_oc_t), np.array(log_oc_v), save_dir)
            
            # 打印洋流统计
            v_arr = np.array(log_oc_v)
            print(f"\n[洋流统计] 平均速度: {v_arr.mean():.4f} m/s, "
                  f"最大速度: {v_arr.max():.4f} m/s, "
                  f"最小速度: {v_arr.min():.4f} m/s")
    
    # ----- 5. 最后拉起 Viewer 进行直观视觉验证 -----
    sim.start_interactive_viewer()
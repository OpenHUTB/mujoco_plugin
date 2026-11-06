"""
水下测绘任务仿真 (Survey Mission Simulation)
===========================================
在已有 ROV 流体力学模型 (data/rov_base.xml) 上叠加测绘任务：
  规划弓字形测线 → LOS 制导 → 水平速度/艏向控制 + 深度 PID → 覆盖统计

与已有模块的关系：
  * 力学/媒体参数注入方式与 underwater_sim.py 保持一致
  * 深度控制复用 depth_controller.PIDDepthController
  * 绘图复用 plot_results.py

运行：
  python survey_mission_sim.py            # 无界面，跑完输出指标与图片
  python survey_mission_sim.py --viewer   # 额外拉起 MuJoCo Viewer 观看
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path

import numpy as np
import mujoco

from depth_controller import PIDDepthController
from survey_mission import (CoverageTracker, LOSGuidance, evaluate_mission,
                            lawnmower_waypoints, wrap_to_pi)
from plot_results import (plot_coverage_map, plot_cross_track,
                          plot_survey_trajectory)

_HERE = Path(__file__).resolve().parent
_DEFAULT_CONFIG = _HERE / "data" / "config.json"
_BASE_MODEL = _HERE / "data" / "rov_base.xml"


class SurveySimulation:
    """测绘任务仿真器：装配模型、闭环控制、记录航迹"""

    def __init__(self, config_path=_DEFAULT_CONFIG, model_path=_BASE_MODEL):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.mission = self.config["survey_mission"]
        self.model_path = str(model_path)

        rov = self.config["rov_body"]
        half = np.asarray(rov["half_size"], dtype=float)
        self.volume = float(np.prod(half * 2.0))   # 长方体体积
        self.mass = float(rov["mass"])
        self.g = float(self.config["gravity"])

        ctrl = self.mission["controller"]
        # 水平速度环（PI）+ 艏向环参数
        self.kp_vel = float(ctrl["kp_vel"])
        self.ki_vel = float(ctrl["ki_vel"])
        self.max_force = float(ctrl["max_force"])
        self.kp_yaw = float(ctrl["kp_yaw"])
        self.kd_yaw = float(ctrl["kd_yaw"])
        self.max_torque = float(ctrl["max_torque"])
        self.vel_integral = np.zeros(2)

        self.depth_controller = PIDDepthController(kp=1500.0, ki=10.0, kd=800.0)

    # ── 模型装配 ──────────────────────────────────────────────
    def load_model(self) -> mujoco.MjModel:
        model = mujoco.MjModel.from_xml_path(self.model_path)
        model.opt.gravity = np.array([0.0, 0.0, -self.g])
        model.opt.timestep = self.config["simulation_timestep"]
        model.opt.density = self.config["fluid_density"]
        model.opt.viscosity = self.config["fluid_viscosity"]

        rov = self.config["rov_body"]
        geom_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, rov["geom_name"])
        model.geom_size[geom_id] = rov["half_size"]
        model.body_mass[model.geom_bodyid[geom_id]] = self.mass
        model.geom_fluid[geom_id, :5] = np.array(rov["fluid_coef"])
        return model

    # ── 闭环控制 ──────────────────────────────────────────────
    def _control(self, data, guidance_state, target_depth, dt, buoyancy):
        """
        单步控制律。

        Returns:
            (force, tau_z)：世界坐标系下的推力 (Fx, Fy, Fz) 与绕 Z 轴力矩
        """
        pos = data.sensor("pos").data[:3]
        vel = data.sensor("vel").data[:3]          # 世界系线速度
        w, x, y, z = data.qpos[self._qpos_adr + 3:self._qpos_adr + 7]
        yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

        # 1) 水平速度环（PI）：把期望世界速度转换成世界系推力
        speed = float(self.mission["cruise_speed"])
        psi_d = guidance_state.desired_heading
        v_des = speed * np.array([math.cos(psi_d), math.sin(psi_d)])
        v_err = v_des - vel[:2]

        # 积分抗饱和：限幅 ±2 m/s·s，避免大偏差时积分爆掉
        self.vel_integral += v_err * dt
        np.clip(self.vel_integral, -2.0, 2.0, out=self.vel_integral)

        f_world_xy = self.kp_vel * v_err + self.ki_vel * self.vel_integral

        norm = float(np.linalg.norm(f_world_xy))
        if norm > self.max_force:
            f_world_xy *= self.max_force / norm

        # 投影到机体系并限幅（模拟推进器能力上限），再转回世界系
        body_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "rov")
        rot = data.xmat[body_id].reshape(3, 3)
        f_body = rot.T @ np.array([f_world_xy[0], f_world_xy[1], 0.0])
        f_world = rot @ f_body

        # 2) 艏向环：PD 得到绕世界 Z 轴的力矩
        e_psi = wrap_to_pi(psi_d - yaw)
        jnt_id = self.model.body_jntadr[body_id]
        dof = self.model.jnt_dofadr[jnt_id]
        yaw_rate = float(data.qvel[dof + 5])
        tau_z = self.kp_yaw * e_psi - self.kd_yaw * yaw_rate
        tau_z = float(np.clip(tau_z, -self.max_torque, self.max_torque))

        # 3) 深度 PID + 静态浮力补偿
        thrust_z = self.depth_controller.compute(
            target_depth, float(pos[2]), dt, current_velocity=0.0)

        return np.array([f_world[0], f_world[1], buoyancy + thrust_z]), tau_z

    # ── 主流程 ────────────────────────────────────────────────
    def run(self, out_dir: str, show_viewer: bool = False):
        m = self.mission
        waypoints = lawnmower_waypoints(
            m["area_width"], m["area_height"], m["lane_spacing"],
            origin=m["origin"], heading=m["heading"])
        guidance = LOSGuidance(waypoints, lookahead=m["lookahead"],
                               accept_radius=m["accept_radius"])
        coverage = CoverageTracker(
            m["area_width"], m["area_height"], resolution=m["grid_resolution"],
            origin=m["origin"], heading=m["heading"], swath_width=m["swath_width"])

        self.model = self.load_model()
        data = mujoco.MjData(self.model)
        body_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "rov")
        jnt_id = self.model.body_jntadr[body_id]
        qpos_adr = self.model.jnt_qposadr[jnt_id]
        self._qpos_adr = int(qpos_adr)

        # 初始位姿：作业区起点、目标深度、艏向沿 +X
        data.qpos[qpos_adr:qpos_adr + 3] = [waypoints[0][0], waypoints[0][1], m["target_depth"]]
        data.qpos[qpos_adr + 3:qpos_adr + 7] = [1.0, 0.0, 0.0, 0.0]
        mujoco.mj_forward(self.model, data)

        buoyancy = self.config["fluid_density"] * self.g * self.volume
        dt = self.model.opt.timestep
        max_steps = int(m["timeout_seconds"] / dt)
        self.vel_integral[:] = 0.0

        times, traj, ctes, speeds = [], [], [], []
        finished = False

        viewer_ctx = mujoco.viewer.launch_passive(self.model, data) if show_viewer else None

        try:
            for step in range(max_steps):
                pos = data.sensor("pos").data[:3]
                gs = guidance.update(pos[:2])

                force, tau_z = self._control(data, gs, m["target_depth"], dt, buoyancy)
                data.xfrc_applied[body_id, 0:3] = force
                data.xfrc_applied[body_id, 5] = tau_z

                mujoco.mj_step(self.model, data)

                if step % 10 == 0:
                    p = data.sensor("pos").data[:3]
                    times.append(float(data.time))
                    traj.append((float(p[0]), float(p[1])))
                    ctes.append(float(gs.cross_track_error))
                    speeds.append(float(np.linalg.norm(data.sensor("vel").data[:3])))
                    coverage.add_point(p[:2])

                if viewer_ctx is not None:
                    if not viewer_ctx.is_running():
                        break
                    viewer_ctx.sync()

                # 到达终点即收工
                if np.linalg.norm(pos[:2] - waypoints[-1]) <= m["accept_radius"]:
                    finished = True
                    break
        finally:
            if viewer_ctx is not None:
                viewer_ctx.close()

        metrics = evaluate_mission(times, traj, ctes, waypoints,
                                   coverage.coverage, finished)

        os.makedirs(out_dir, exist_ok=True)
        self._save_csv(os.path.join(out_dir, "survey_track.csv"), times, traj, ctes, speeds)
        plot_survey_trajectory(waypoints, np.asarray(traj), out_dir)
        plot_cross_track(np.asarray(times), np.asarray(ctes), out_dir)
        plot_coverage_map(coverage, out_dir)

        return metrics, waypoints, np.asarray(traj), coverage

    @staticmethod
    def _save_csv(path: str, times, traj, ctes, speeds) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["time_s", "x_m", "y_m", "speed_m_s", "cross_track_error_m"])
            for t, p, v, e in zip(times, traj, speeds, ctes):
                w.writerow([f"{t:.3f}", f"{p[0]:.3f}", f"{p[1]:.3f}",
                            f"{v:.3f}", f"{e:.4f}"])
        print(f"[数据] 航迹已保存至: {os.path.abspath(path)}")


def main() -> int:
    ap = argparse.ArgumentParser(description="水下机器人测绘任务仿真")
    ap.add_argument("--config", default=str(_DEFAULT_CONFIG))
    ap.add_argument("--model", default=str(_BASE_MODEL))
    ap.add_argument("--out-dir", default=str(_HERE.parents[1] / "docs" / "img" / "underwater"))
    ap.add_argument("--viewer", action="store_true", help="同时打开 MuJoCo Viewer")
    args = ap.parse_args()

    sim = SurveySimulation(args.config, args.model)
    print("=" * 62)
    print("  水下机器人测绘任务仿真 (弓字形测线 + LOS 制导)")
    print("=" * 62)

    metrics, _, _, _ = sim.run(args.out_dir, show_viewer=args.viewer)
    print("\n[任务指标] " + metrics.summary())
    return 0 if metrics.finished else 2


if __name__ == "__main__":
    raise SystemExit(main())

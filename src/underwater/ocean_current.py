"""
洋流模型 — 三层级联 (Ocean Current Model)
=========================================
模型组成：
  1. Gauss-Markov 过程：模拟洋流随时间的随机波动（均值回归 + 高斯噪声）
  2. 分层模型 (Stratified)：不同深度有不同流速（海洋剖面）
  3. 湍流扰动 (Turbulent)：空间各位置速度不一致（需求文档 §9）

总洋流速度：
  V_current(x, y, z, t) = V_GM(t) + V_stratified(z) + V_turbulent(x, y, z, t)

相对流速（核心）：
  V_rel = V_robot - V_current  →  喂给 MuJoCo 椭球流体模型自动计算阻力

参考：
  - UUV Simulator / DAVE  (Gauss-Markov + Stratified)
  - Gazebo UnderwaterCurrentPlugin
  - https://field-robotics-lab.github.io/dave.doc/contents/dave_env/Ocean-Current/
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import List


# ──────────────────────────────────────────────────────────────
# 1. 数据结构
# ──────────────────────────────────────────────────────────────

@dataclass
class CurrentLayer:
    """单一深度层洋流参数"""
    depth_m: float           # 深度 (m, 负值表示水下深度)
    speed_ms: float          # 流速大小 (m/s)
    horizontal_angle_rad: float = 0.0   # 水平角度 (rad)
    vertical_angle_rad: float = 0.0     # 垂直角度 (rad)


# ──────────────────────────────────────────────────────────────
# 2. Gauss-Markov 过程
# ──────────────────────────────────────────────────────────────

class GaussMarkovCurrent:
    """
    一阶 Gauss-Markov 洋流过程
    
    公式：
        V̇ + μ·V = ω,   ω ~ N(0, σ²)
    
    离散化（欧拉法）：
        V_{t+dt} = V_t + μ·(V_mean - V_t)·dt + σ·√dt·N(0,1)
    
    参考：UUV Simulator UnderwaterCurrentPlugin
    
    参数：
        mean_speed: 洋流平均速度 (m/s)
        mean_horizontal_angle: 水平平均角度 (rad)，0 = +X 方向
        mean_vertical_angle: 垂直平均角度 (rad)，0 = 水平，+ = 向下
        mu: Gauss-Markov 衰减常数 (>=0)，0 = 纯随机游走，>0 = 均值回归
        noise_amp: 噪声幅度 σ
        seed: 随机种子（用于可复现性）
    """

    def __init__(self, mean_speed: float = 0.0,
                 mean_horizontal_angle: float = 0.0,
                 mean_vertical_angle: float = 0.0,
                 mu: float = 0.0,
                 noise_amp: float = 0.1,
                 seed: int | None = None):
        self.mean_speed = mean_speed
        self.mean_horizontal_angle = mean_horizontal_angle
        self.mean_vertical_angle = mean_vertical_angle
        self.mu = mu
        self.noise_amp = noise_amp

        # 当前状态（初始化为均值）
        self._speed = float(mean_speed)
        self._horiz_angle = float(mean_horizontal_angle)
        self._vert_angle = float(mean_vertical_angle)

        self._rng = np.random.default_rng(seed)

    # ── 公共接口 ──────────────────────────────────────────

    def update(self, dt: float) -> np.ndarray:
        """
        更新洋流状态并返回当前速度向量
        
        Args:
            dt: 仿真时间步长 (s)
        
        Returns:
            np.ndarray: [vx, vy, vz] 洋流速度向量 (m/s)
                        MuJoCo 坐标系：Z 轴向上，NED 到 MuJoCo 已转换
        """
        # ── 速度幅值 ──
        noise_s = self.noise_amp * np.sqrt(dt) * self._rng.standard_normal()
        self._speed += self.mu * (self.mean_speed - self._speed) * dt + noise_s
        self._speed = max(0.0, self._speed)  # 速度非负

        # ── 水平角度 ──
        noise_h = self.noise_amp * np.sqrt(dt) * self._rng.standard_normal()
        self._horiz_angle += (self.mu * (self.mean_horizontal_angle - self._horiz_angle)
                              + noise_h) * dt

        # ── 垂直角度 ──
        noise_v = self.noise_amp * np.sqrt(dt) * self._rng.standard_normal()
        self._vert_angle += (self.mu * (self.mean_vertical_angle - self._vert_angle)
                             + noise_v) * dt

        # ── 计算笛卡尔速度向量 ──
        # NED 坐标系：X=北, Y=东, Z=向下
        # MuJoCo 坐标系：Z 向上 → vz_mujoco = -vz_ned
        cos_v = np.cos(self._vert_angle)
        return np.array([
            self._speed * cos_v * np.cos(self._horiz_angle),
            self._speed * cos_v * np.sin(self._horiz_angle),
            -self._speed * np.sin(self._vert_angle),   # NED(Z↓) → MuJoCo(Z↑)
        ])

    # ── 状态重置 ──────────────────────────────────────────

    def reset(self):
        """重置为均值状态（仿真重置时调用）"""
        self._speed = self.mean_speed
        self._horiz_angle = self.mean_horizontal_angle
        self._vert_angle = self.mean_vertical_angle

    # ── 只读属性 ──────────────────────────────────────────

    @property
    def current_speed(self) -> float:
        return self._speed

    @property
    def current_horizontal_angle(self) -> float:
        return self._horiz_angle

    @property
    def current_vertical_angle(self) -> float:
        return self._vert_angle


# ──────────────────────────────────────────────────────────────
# 3. 分层洋流模型
# ──────────────────────────────────────────────────────────────

class StratifiedCurrent:
    """
    分层洋流 — 按深度插值
    
    不同深度有不同的平均流速，之间线性插值。
    每层使用独立的 Gauss-Markov 模型来模拟该层的随机波动。
    
    参考：UUV Simulator stratified current database
    
    参数：
        layers: CurrentLayer 列表，必须按深度升序排列（最深到最浅）
    """

    def __init__(self, layers: List[CurrentLayer]):
        if len(layers) < 2:
            raise ValueError("分层洋流至少需要 2 层数据")

        self.layers = sorted(layers, key=lambda l: l.depth_m)
        self.n_layers = len(layers)

        # 为每层创建独立的 Gauss-Markov 模型（无内部噪声，波动由湍流层处理）
        self._gm_models = [
            GaussMarkovCurrent(
                mean_speed=l.speed_ms,
                mean_horizontal_angle=l.horizontal_angle_rad,
                mean_vertical_angle=l.vertical_angle_rad,
                mu=0.0,
                noise_amp=0.0,
            )
            for l in self.layers
        ]

    def get_velocity_at(self, depth_m: float, dt: float) -> np.ndarray:
        """
        获取指定深度的洋流速度（线性插值）
        
        Args:
            depth_m: 深度 (m)，负值表示水下
            dt: 时间步长
        
        Returns:
            洋流速度向量 [vx, vy, vz] (m/s, MuJoCo Z向上)
        """
        # 边界处理：浅于最浅层 → 使用最浅层
        if depth_m <= self.layers[0].depth_m:
            return self._gm_models[0].update(dt)

        # 在两层之间线性插值
        for i in range(self.n_layers - 1):
            if self.layers[i].depth_m <= depth_m <= self.layers[i + 1].depth_m:
                # 插值系数 (0 = 当前层, 1 = 下一层)
                t = (depth_m - self.layers[i].depth_m) / \
                    (self.layers[i + 1].depth_m - self.layers[i].depth_m)

                v1 = self._gm_models[i].update(dt)
                v2 = self._gm_models[i + 1].update(dt)

                return v1 * (1.0 - t) + v2 * t

        # 深于最深层 → 使用最深层
        return self._gm_models[-1].update(dt)

    def reset(self):
        """重置所有层的 Gauss-Markov 状态"""
        for gm in self._gm_models:
            gm.reset()


# ──────────────────────────────────────────────────────────────
# 4. 湍流扰动模型
# ──────────────────────────────────────────────────────────────

class TurbulentCurrent:
    """
    湍流扰动 — 简化随机涡度场
    
    使用基于相关长度尺度的指数衰减随机场：
    
        V_turb(x, y, z) = σ_turb · exp(-||x-x0|| / L) · η
    
    其中 η 是标准正态分布随机数，L 是湍流积分尺度。
    
    该模型保证：
    - 空间连续：相邻位置的湍流速度相关
    - 各向同性：三个方向扰动强度相同
    - 可重置：仿真重置时清除历史状态
    
    参数：
        intensity: 湍流强度，表示为平均洋流速度的比例
        integral_scale: 湍流积分尺度 (m)，表征涡旋大小
        seed: 随机种子
    """

    def __init__(self, intensity: float = 0.15,
                 integral_scale: float = 1.0,
                 seed: int | None = None):
        self.intensity = intensity
        self.integral_scale = integral_scale
        self._last_pos = None  # 上次位置
        self._rng = np.random.default_rng(seed)

    def get_velocity_at(self, x: float, y: float, z: float,
                        dt: float) -> np.ndarray:
        """
        获取空间位置处的湍流速度扰动
        
        Args:
            x, y, z: 机器人位置 (m, MuJoCo 坐标系 Z向上)
            dt: 时间步长（当前未使用，预留用于时间相关湍流）
        
        Returns:
            湍流速度扰动向量 (m/s)
        """
        pos = np.array([float(x), float(y), float(z)])

        if self._last_pos is not None:
            dist = np.linalg.norm(pos - self._last_pos)
            # 指数衰减相关模型
            correlation = np.exp(-dist / max(self.integral_scale, 1e-6))
            # 新湍流分量 = 不相关部分
            noise_strength = self.intensity * np.sqrt(1.0 - correlation ** 2)
        else:
            noise_strength = self.intensity

        noise = noise_strength * self._rng.standard_normal(3)
        self._last_pos = pos

        return noise * 0.5  # 缩放因子

    def reset(self):
        """重置湍流历史状态（仿真重置时调用）"""
        self._last_pos = None


# ──────────────────────────────────────────────────────────────
# 5. 洋流级联模型 (对外接口)
# ──────────────────────────────────────────────────────────────

class OceanCurrentCascade:
    """
    洋流模型 — 三层级联 (对外接口)
    
    V_current(x, y, z, t) = V_GM(t) + V_stratified(z) + V_turbulent(x, y, z, t)
    
    这是被 underwater_sim.py 调用的统一接口。
    
    参数：
        config: ocean_current 配置字典（来自 config.json）
        seed: 随机种子
    """

    def __init__(self, config: dict, seed: int = 42):
        gm_cfg = config.get("gauss_markov", {})
        strat_cfg = config.get("stratified_layers", [])
        turb_cfg = config.get("turbulent", {})

        # Layer 1: Gauss-Markov 基础洋流
        self._gm = GaussMarkovCurrent(
            mean_speed=gm_cfg.get("mean_speed", 0.0),
            mean_horizontal_angle=gm_cfg.get("mean_horizontal_angle", 0.0),
            mean_vertical_angle=gm_cfg.get("mean_vertical_angle", 0.0),
            mu=gm_cfg.get("mu", 0.0),
            noise_amp=gm_cfg.get("noise_amp", 0.1),
            seed=seed,
        )

        # Layer 2: 分层洋流
        layers = [
            CurrentLayer(
                l["depth_m"],
                l["speed_ms"],
                l.get("horizontal_angle_rad", 0.0),
                l.get("vertical_angle_rad", 0.0),
            )
            for l in strat_cfg
        ]
        self._stratified = StratifiedCurrent(layers) if layers else None

        # Layer 3: 湍流扰动
        self._turbulent = TurbulentCurrent(
            intensity=turb_cfg.get("intensity", 0.1),
            integral_scale=turb_cfg.get("integral_scale_m", 1.0),
            seed=seed + 1,
        )

        # 缓存上一次位置（用于湍流空间相关性）
        self._last_x = 0.0
        self._last_y = 0.0
        self._last_z = -1.0

    def get_velocity(self, x: float, y: float, z: float,
                     dt: float) -> np.ndarray:
        """
        获取空间位置 (x, y, z) 处的总洋流速度
        
        Args:
            x, y, z: 机器人位置 (m)
            dt: 仿真时间步长 (s)
        
        Returns:
            np.ndarray: 总洋流速度 [vx, vy, vz] (m/s, MuJoCo Z向上)
        """
        # 更新缓存位置（湍流使用）
        self._last_x, self._last_y, self._last_z = x, y, z

        # Layer 1: Gauss-Markov（全局，时间变化）
        v_gm = self._gm.update(dt)

        # Layer 2: 分层（深度变化）
        depth = -z  # z 向上，深度为正数取反
        v_strat = self._stratified.get_velocity_at(depth, dt) if self._stratified \
            else np.zeros(3)

        # Layer 3: 湍流（空间变化）
        v_turb = self._turbulent.get_velocity_at(x, y, z, dt)

        return v_gm + v_strat + v_turb

    def reset(self):
        """重置所有洋流状态（仿真重置时调用）"""
        self._gm.reset()
        if self._stratified:
            self._stratified.reset()
        self._turbulent.reset()

    # ── 只读属性（用于可视化和日志）──────────────────────

    @property
    def current_speed(self) -> float:
        """当前洋流速度幅值 (m/s)"""
        return self._gm.current_speed

    @property
    def current_horizontal_angle(self) -> float:
        """当前洋流水平角度 (rad)"""
        return self._gm.current_horizontal_angle

    @property
    def current_vertical_angle(self) -> float:
        """当前洋流垂直角度 (rad)"""
        return self._gm.current_vertical_angle


# ──────────────────────────────────────────────────────────────
# 6. 辅助工具函数
# ──────────────────────────────────────────────────────────────

def apply_current_drag(data: "mujoco.MjData", body_id: int,
                       current_velocity: np.ndarray,
                       drag_coeff: float = 10.0) -> None:
    """
    将洋流速度作为拖曳力注入 xfrc_applied
    
    简单线性模型：F_drag = -drag_coeff * V_current
    更精确的模型应使用 V_rel = V_robot - V_current
    
    Args:
        data: MuJoCo MjData 实例
        body_id: 受影响的 body ID
        current_velocity: 洋流速度 [vx, vy, vz] (m/s)
        drag_coeff: 拖曳系数 (kg/s)
    """
    data.xfrc_applied[body_id, 0] -= drag_coeff * current_velocity[0]
    data.xfrc_applied[body_id, 1] -= drag_coeff * current_velocity[1]
    data.xfrc_applied[body_id, 2] -= drag_coeff * current_velocity[2]


def compute_relative_velocity(robot_vel: np.ndarray,
                              current_vel: np.ndarray) -> np.ndarray:
    """
    计算相对流速 V_rel = V_robot - V_current
    
    这是 MuJoCo 椭球流体模型计算阻力的基础。
    
    Args:
        robot_vel: 机器人速度 [vx, vy, vz] (m/s)
        current_vel: 洋流速度 [vx, vy, vz] (m/s)
    
    Returns:
        np.ndarray: 相对流速
    """
    return robot_vel - current_vel


# ──────────────────────────────────────────────────────────────
# 7. 测试入口
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  洋流模型自检")
    print("=" * 60)

    config = {
        "gauss_markov": {
            "mean_speed": 0.5,
            "mean_horizontal_angle": 0.0,
            "mean_vertical_angle": 0.0,
            "mu": 0.0,
            "noise_amp": 0.1,
        },
        "stratified_layers": [
            {"depth_m": 0,   "speed_ms": 0.0,  "horizontal_angle_rad": 0.0,  "vertical_angle_rad": 0.0},
            {"depth_m": -10, "speed_ms": 0.5,  "horizontal_angle_rad": 0.3,  "vertical_angle_rad": 0.0},
            {"depth_m": -50, "speed_ms": 1.0,  "horizontal_angle_rad": 0.5,  "vertical_angle_rad": 0.1},
        ],
        "turbulent": {
            "intensity": 0.15,
            "integral_scale_m": 1.0,
        },
    }

    ocean = OceanCurrentCascade(config, seed=42)
    dt = 0.002

    print("\n▶ 模拟 10 秒洋流变化...")
    for i in range(int(10.0 / dt)):
        depth = -1.0 + np.sin(i * 0.01) * 0.5
        v = ocean.get_velocity(0.0, 0.0, depth, dt)
        if i % 500 == 0:
            print(f"  t={i*dt:.1f}s | speed={v[0]:.4f} {v[1]:.4f} {v[2]:.4f} "
                  f"| 幅值={np.linalg.norm(v):.4f} m/s")

    print("\n▶ 重置后...")
    ocean.reset()
    v = ocean.get_velocity(0.0, 0.0, -1.0, dt)
    print(f"  重置后速度: {v[0]:.6f} {v[1]:.6f} {v[2]:.6f} (应接近初始值)")

    print("\n✅ 自检完成")

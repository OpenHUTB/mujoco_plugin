"""
水下测绘任务层 (Survey Mission)
================================
职责：
  1. 覆盖路径规划：往返式 (lawnmower) 测线生成
  2. 制导：视线法 (LOS, Line-Of-Sight) 追踪，输出期望艏向与横向偏差
  3. 覆盖评估：栅格化统计测线对作业区域的覆盖比例
  4. 任务指标：横向偏差 RMS/峰值、航程、耗时、覆盖率

设计原则：
  * 本模块只做纯数学计算，不依赖 MuJoCo，可脱离仿真单独进行单元测试
  * 与已有模块解耦：仿真层 (survey_mission_sim.py) 负责力学积分，
    控制层复用 depth_controller.PIDDepthController
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Sequence

import numpy as np


# ──────────────────────────────────────────────────────────────
# 1. 覆盖路径规划
# ──────────────────────────────────────────────────────────────

def lawnmower_waypoints(width: float,
                        height: float,
                        lane_spacing: float,
                        origin: Sequence[float] = (0.0, 0.0),
                        heading: float = 0.0) -> np.ndarray:
    """
    生成往返式 (lawnmower / 弓字形) 测线路径点。

    路径在局部坐标系中沿 +X 逐条测线往返，测线沿 +Y 等间距排布，
    最后整体旋转 heading 并平移 origin，便于把作业区域摆到任意位置。

    Args:
        width:        单条测线长度 (m, 局部 X 方向)
        height:       作业区域宽度 (m, 局部 Y 方向)
        lane_spacing: 期望测线间距 (m)，实际间距会取 <= 该值
        origin:       作业区域左下角在世界坐标系中的位置 (x, y)
        heading:      作业区域朝向 (rad)，0 表示测线沿世界 +X

    Returns:
        (N, 2) 的路径点数组，按航行顺序排列（已含转弯角点）
    """
    if width <= 0 or height <= 0 or lane_spacing <= 0:
        raise ValueError("width / height / lane_spacing 必须为正数")

    # 保证实际间距不超过期望间距：向上取整后再均分
    n_lanes = max(1, int(math.ceil(height / lane_spacing)))
    lane_ys = [height * i / n_lanes for i in range(n_lanes + 1)]

    local: List[tuple] = []
    for i, y in enumerate(lane_ys):
        if i % 2 == 0:
            local.append((0.0, y))
            local.append((width, y))
        else:
            local.append((width, y))
            local.append((0.0, y))

    pts = np.asarray(local, dtype=float)
    c, s = math.cos(heading), math.sin(heading)
    rot = np.array([[c, -s], [s, c]])
    return pts @ rot.T + np.asarray(origin, dtype=float)


# ──────────────────────────────────────────────────────────────
# 2. LOS 制导
# ──────────────────────────────────────────────────────────────

def wrap_to_pi(angle: float) -> float:
    """把角度归一化到 [-pi, pi)"""
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


@dataclass
class GuidanceState:
    """LOS 制导单步输出"""
    desired_heading: float      # 期望艏向 (rad, 世界系)
    cross_track_error: float    # 横向偏差 (m)，路径左侧为正
    segment_index: int          # 当前跟踪的测线段索引
    lookahead_point: np.ndarray # 前视点 (x, y)
    distance_to_goal: float     # 到当前段终点的距离 (m)
    finished: bool              # 是否已完成全部路径


class LOSGuidance:
    """
    视线法 (LOS) 路径跟踪制导。

    对当前位置投影到当前测线段，得到横向偏差；
    在投影点前方 lookahead 处取前视点，以“当前位置 → 前视点”的方向
    作为期望艏向，从而在存在横向偏差时自然产生回中趋势。
    """

    def __init__(self, waypoints: np.ndarray,
                 lookahead: float = 3.0,
                 accept_radius: float = 1.0):
        self.waypoints = np.asarray(waypoints, dtype=float)
        if self.waypoints.ndim != 2 or self.waypoints.shape[0] < 2:
            raise ValueError("waypoints 至少需要 2 个点")
        self.lookahead = float(lookahead)
        self.accept_radius = float(accept_radius)
        self.segment_index = 0

    def reset(self) -> None:
        self.segment_index = 0

    def update(self, position_xy: Sequence[float], heading: float = 0.0) -> GuidanceState:
        """
        Args:
            position_xy: 当前水平位置 (x, y)
            heading:     当前艏向 (rad)，仅用于外部记录，不参与制导计算
        """
        p = np.asarray(position_xy, dtype=float)[:2]
        last = len(self.waypoints) - 2

        # 到达当前段终点则切换到下一段（可连续跨越多个短段）
        while self.segment_index < last:
            if np.linalg.norm(p - self.waypoints[self.segment_index + 1]) <= self.accept_radius:
                self.segment_index += 1
            else:
                break

        i = self.segment_index
        a = self.waypoints[i]
        b = self.waypoints[i + 1]
        ab = b - a
        seg_len = float(np.linalg.norm(ab))
        if seg_len < 1e-9:
            raise ValueError(f"第 {i} 段路径长度为 0")

        u = ab / seg_len
        # 投影参数（夹紧到线段内）
        t = float(np.clip(np.dot(p - a, u) / seg_len, 0.0, 1.0))
        foot = a + t * seg_len * u

        # 二维叉积：路径左侧为正
        cross = u[0] * (p - a)[1] - u[1] * (p - a)[0]

        # 前视点：投影点沿测线方向前伸 lookahead
        target = foot + self.lookahead * u
        if np.dot(target - b, u) > 0:      # 不要越过当前段终点
            target = b

        desired = math.atan2(target[1] - p[1], target[0] - p[0])
        distance_to_goal = float(np.linalg.norm(p - self.waypoints[-1]))

        return GuidanceState(
            desired_heading=wrap_to_pi(desired),
            cross_track_error=float(cross),
            segment_index=i,
            lookahead_point=target,
            distance_to_goal=distance_to_goal,
            finished=False,
        )


# ──────────────────────────────────────────────────────────────
# 3. 覆盖率评估
# ──────────────────────────────────────────────────────────────

class CoverageTracker:
    """
    栅格化覆盖率统计。

    把作业区域离散成 resolution × resolution 的栅格，
    船只每走过一个位置，就把以该点为圆心、swath_width 为直径的
    圆内栅格标记为已覆盖；段内按 resolution/2 插值，避免漏格。
    """

    def __init__(self, width: float, height: float,
                 resolution: float = 0.5,
                 origin: Sequence[float] = (0.0, 0.0),
                 heading: float = 0.0,
                 swath_width: float = 2.0):
        self.width = float(width)
        self.height = float(height)
        self.res = float(resolution)
        self.origin = np.asarray(origin, dtype=float)[:2]
        self.heading = float(heading)
        self.radius = max(self.res, float(swath_width) / 2.0)

        self.nx = max(1, int(math.ceil(self.width / self.res)))
        self.ny = max(1, int(math.ceil(self.height / self.res)))
        self.visited = np.zeros((self.nx, self.ny), dtype=bool)
        self._last: np.ndarray | None = None

    # 世界坐标 → 栅格坐标
    def _to_grid(self, p: np.ndarray) -> np.ndarray:
        d = p - self.origin
        c, s = math.cos(-self.heading), math.sin(-self.heading)
        local = np.array([c * d[0] - s * d[1], s * d[0] + c * d[1]])
        return local / self.res  # 以栅格为单位

    def _mark_disc(self, gx: float, gy: float) -> None:
        r = self.radius / self.res
        i0 = max(0, int(math.floor(gx - r)))
        i1 = min(self.nx - 1, int(math.ceil(gx + r)))
        j0 = max(0, int(math.floor(gy - r)))
        j1 = min(self.ny - 1, int(math.ceil(gy + r)))
        if i0 > i1 or j0 > j1:
            return
        xs = np.arange(i0, i1 + 1) + 0.5
        ys = np.arange(j0, j1 + 1) + 0.5
        mask = (xs[:, None] - gx) ** 2 + (ys[None, :] - gy) ** 2 <= r * r
        self.visited[i0:i1 + 1, j0:j1 + 1] |= mask

    def add_point(self, position_xy: Sequence[float]) -> None:
        """记录一个航迹点（会自动与上一个点之间插值补格）"""
        p = np.asarray(position_xy, dtype=float)[:2]
        if self._last is None:
            self._last = p
            g = self._to_grid(p)
            self._mark_disc(g[0], g[1])
            return

        seg = p - self._last
        dist = float(np.linalg.norm(seg))
        steps = max(1, int(math.ceil(dist / (self.res * 0.5))))
        for k in range(1, steps + 1):
            q = self._last + seg * (k / steps)
            g = self._to_grid(q)
            self._mark_disc(g[0], g[1])
        self._last = p

    @property
    def coverage(self) -> float:
        """已覆盖栅格占作业区域总栅格的比例 [0, 1]"""
        return float(self.visited.sum()) / float(self.visited.size)

    @property
    def uncovered_cells(self) -> int:
        return int((~self.visited).sum())


# ──────────────────────────────────────────────────────────────
# 4. 任务指标
# ──────────────────────────────────────────────────────────────

@dataclass
class MissionMetrics:
    """一次测绘任务的统计指标"""
    cross_track_rms: float = 0.0     # 横向偏差 RMS (m)
    cross_track_max: float = 0.0     # 横向偏差峰值 (m)
    traveled_distance: float = 0.0   # 实际航程 (m)
    planned_distance: float = 0.0    # 规划航程 (m)
    duration: float = 0.0            # 任务耗时 (s)
    coverage: float = 0.0            # 覆盖率 [0, 1]
    finished: bool = False           # 是否走完全部路径

    def summary(self) -> str:
        return (f"覆盖率 {self.coverage * 100:.1f}% | "
                f"横向偏差 RMS {self.cross_track_rms:.3f} m (峰值 {self.cross_track_max:.3f} m) | "
                f"航程 {self.traveled_distance:.1f} / 规划 {self.planned_distance:.1f} m | "
                f"耗时 {self.duration:.1f} s | "
                f"{'已完成' if self.finished else '未完成'}")


def path_length(waypoints: np.ndarray) -> float:
    """路径总长度 (m)"""
    w = np.asarray(waypoints, dtype=float)
    return float(np.sum(np.linalg.norm(np.diff(w, axis=0), axis=1)))


def evaluate_mission(times: Sequence[float],
                     positions: Sequence[Sequence[float]],
                     cross_track_errors: Sequence[float],
                     planned: np.ndarray,
                     coverage: float,
                     finished: bool) -> MissionMetrics:
    """
    汇总任务指标。

    Args:
        times:               采样时刻 (s)
        positions:           采样位置序列 (N, 2)
        cross_track_errors:  与 times 对齐的横向偏差序列
        planned:             规划路径点
        coverage:            统计得到的覆盖率
        finished:            是否完成全部测线
    """
    t = np.asarray(times, dtype=float)
    pos = np.asarray(positions, dtype=float)
    cte = np.asarray(cross_track_errors, dtype=float)

    traveled = float(np.sum(np.linalg.norm(np.diff(pos, axis=0), axis=1))) if len(pos) > 1 else 0.0
    duration = float(t[-1] - t[0]) if len(t) > 1 else 0.0

    return MissionMetrics(
        cross_track_rms=float(np.sqrt(np.mean(cte ** 2))) if cte.size else 0.0,
        cross_track_max=float(np.max(np.abs(cte))) if cte.size else 0.0,
        traveled_distance=traveled,
        planned_distance=path_length(planned),
        duration=duration,
        coverage=float(coverage),
        finished=bool(finished),
    )

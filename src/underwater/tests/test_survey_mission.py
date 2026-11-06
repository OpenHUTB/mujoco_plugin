"""
测绘任务层单元测试 (不依赖 MuJoCo)

运行：
    cd src/underwater
    python -m pytest tests/ -v
"""

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from survey_mission import (CoverageTracker, LOSGuidance, evaluate_mission,
                            lawnmower_waypoints, path_length, wrap_to_pi)


# ── 路径规划 ──────────────────────────────────────────────

def test_lawnmower_covers_area_bounds():
    wp = lawnmower_waypoints(width=40.0, height=16.0, lane_spacing=8.0)
    assert wp.ndim == 2 and wp.shape[1] == 2
    assert np.isclose(wp[:, 0].min(), 0.0)
    assert np.isclose(wp[:, 0].max(), 40.0)
    assert np.isclose(wp[:, 1].min(), 0.0)
    assert np.isclose(wp[:, 1].max(), 16.0)


def test_lawnmower_lane_spacing_not_exceeded():
    wp = lawnmower_waypoints(width=10.0, height=11.0, lane_spacing=4.0)
    lanes = np.unique(np.round(wp[:, 1], 6))
    gaps = np.diff(np.sort(lanes))
    assert gaps.max() <= 4.0 + 1e-9
    assert np.isclose(lanes.max(), 11.0)


def test_lawnmower_returns_serpentine():
    """每条测线方向应交替，相邻测线用同一侧边相连"""
    wp = lawnmower_waypoints(width=10.0, height=6.0, lane_spacing=3.0)
    # 第 1 段沿 +X，第 3 段沿 -X
    assert wp[1][0] > wp[0][0]
    assert wp[2][0] > wp[3][0]
    # 第 1 段终点与第 2 段起点在同一条竖边上（转弯段）
    assert np.isclose(wp[1][0], wp[2][0])
    assert np.isclose(wp[3][0], wp[4][0])


def test_lawnmower_rotation_and_translation():
    wp = lawnmower_waypoints(width=10.0, height=10.0, lane_spacing=5.0,
                             origin=(100.0, -50.0), heading=math.pi / 2)
    # 旋转 90°：局部 X -> 世界 Y，局部 Y -> 世界 -X
    assert np.isclose(wp[:, 0].min(), 90.0)
    assert np.isclose(wp[:, 0].max(), 100.0)
    assert np.isclose(wp[:, 1].min(), -50.0)
    assert np.isclose(wp[:, 1].max(), -40.0)


def test_lawnmower_rejects_bad_input():
    with pytest.raises(ValueError):
        lawnmower_waypoints(0.0, 10.0, 1.0)
    with pytest.raises(ValueError):
        lawnmower_waypoints(10.0, 10.0, -1.0)


# ── LOS 制导 ──────────────────────────────────────────────

def straight_path():
    return np.array([[0.0, 0.0], [20.0, 0.0]])


def test_cross_track_sign_is_left_positive():
    g = LOSGuidance(straight_path(), lookahead=3.0, accept_radius=1.0)
    left = g.update((5.0, 2.0))
    g.reset()
    right = g.update((5.0, -2.0))
    assert left.cross_track_error == pytest.approx(2.0, abs=1e-9)
    assert right.cross_track_error == pytest.approx(-2.0, abs=1e-9)


def test_desired_heading_points_back_to_path():
    """位于路径左侧时，期望艏向应指向右前方（负角度）"""
    g = LOSGuidance(straight_path(), lookahead=3.0, accept_radius=1.0)
    st = g.update((5.0, 2.0))
    assert st.desired_heading < 0.0
    # 已经正中时艏向应约为 0
    g.reset()
    st2 = g.update((5.0, 0.0))
    assert abs(st2.desired_heading) < 1e-6


def test_los_converges_when_following_heading():
    """用简化运动学测试：沿期望艏向直行，横向偏差应快速收敛"""
    g = LOSGuidance(straight_path(), lookahead=4.0, accept_radius=1.0)
    pos = np.array([2.0, 3.0])
    ctes = []
    for _ in range(200):
        st = g.update(pos)
        ctes.append(abs(st.cross_track_error))
        pos = pos + 0.1 * np.array([math.cos(st.desired_heading),
                                    math.sin(st.desired_heading)])
    assert ctes[0] == pytest.approx(3.0, abs=1e-6)
    assert ctes[-1] < 0.05
    # 前 50 步应严格单调收敛（后期只是数值抖动）
    assert np.all(np.diff(ctes[:50]) < 0.0)


def test_waypoint_switch_and_finish():
    g = LOSGuidance(np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0]]),
                    lookahead=2.0, accept_radius=0.5)
    st = g.update((9.9, 0.0))
    assert st.segment_index == 1          # 到达第一段终点后自动切换
    st = g.update((10.0, 10.0))
    assert st.distance_to_goal == pytest.approx(0.0, abs=1e-9)


def test_wrap_to_pi():
    for angle in (0.5, 3 * math.pi, -3 * math.pi, 7.0, -7.0):
        w = wrap_to_pi(angle)
        assert -math.pi - 1e-12 <= w <= math.pi + 1e-12
        # 与原始角度等价（同一方向）
        assert abs(math.sin(w) - math.sin(angle)) < 1e-9
        assert abs(math.cos(w) - math.cos(angle)) < 1e-9
    assert wrap_to_pi(0.5) == pytest.approx(0.5)


# ── 覆盖率 ────────────────────────────────────────────────

def test_coverage_increases_along_lane():
    tracker = CoverageTracker(20.0, 10.0, resolution=1.0, swath_width=2.0)
    tracker.add_point((0.0, 0.0))
    first = tracker.coverage
    for x in np.arange(0.0, 20.0, 0.5):
        tracker.add_point((x, 0.0))
    assert tracker.coverage > first
    # 只走了一条测线，不应覆盖全图
    assert tracker.coverage < 0.5


def test_full_lawnmower_achieves_high_coverage():
    wp = lawnmower_waypoints(20.0, 10.0, lane_spacing=2.0)
    tracker = CoverageTracker(20.0, 10.0, resolution=1.0, swath_width=2.0)
    for a, b in zip(wp[:-1], wp[1:]):
        steps = max(2, int(np.linalg.norm(b - a) / 0.5))
        for k in range(steps + 1):
            tracker.add_point(a + (b - a) * k / steps)
    assert tracker.coverage > 0.95


# ── 指标汇总 ──────────────────────────────────────────────

def test_path_length():
    wp = np.array([[0.0, 0.0], [3.0, 4.0], [3.0, 4.0]])
    assert path_length(wp) == pytest.approx(5.0)


def test_evaluate_mission_metrics():
    planned = np.array([[0.0, 0.0], [10.0, 0.0]])
    times = [0.0, 1.0, 2.0]
    pos = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]
    ctes = [0.2, -0.2, 0.4]

    m = evaluate_mission(times, pos, ctes, planned, coverage=0.9, finished=True)
    assert m.traveled_distance == pytest.approx(2.0)
    assert m.planned_distance == pytest.approx(10.0)
    assert m.cross_track_max == pytest.approx(0.4)
    assert m.cross_track_rms == pytest.approx(math.sqrt((0.04 + 0.04 + 0.16) / 3))
    assert m.coverage == pytest.approx(0.9)
    assert m.finished is True
    assert "覆盖率" in m.summary()

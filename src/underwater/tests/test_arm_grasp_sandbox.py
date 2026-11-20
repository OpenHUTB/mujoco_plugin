"""
机械臂抓取沙盒测试 (需要 MuJoCo，不打开 Viewer)

运行：
    cd src/underwater
    python -m pytest tests/ -v
"""

import os
import sys

import numpy as np
import pytest

mujoco = pytest.importorskip("mujoco")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from arm_grasp_sandbox import (CTRL_HOME, CTRL_LIFT, GRASP_SEGMENTS,
                               ArmGraspSandbox, scripted_grasp_ctrl)

BALL_RADIUS = 0.03


def _run_scripted_grasp(duration):
    """不打开 Viewer，按与 Viewer 相同的方式（控制回调 + mj_step）运行抓取脚本"""
    sandbox = ArmGraspSandbox()
    model, data = sandbox.model, sandbox.data
    mujoco.set_mjcb_control(sandbox.controller_callback)
    try:
        while data.time < duration:
            mujoco.mj_step(model, data)
    finally:
        mujoco.set_mjcb_control(None)
    return model, data


def test_ctrl_follows_segments():
    assert np.allclose(scripted_grasp_ctrl(0.0), CTRL_HOME)
    t = 0.0
    for _, end, duration in GRASP_SEGMENTS:
        t += duration
        assert np.allclose(scripted_grasp_ctrl(t), end)
    assert np.allclose(scripted_grasp_ctrl(t + 10.0), CTRL_LIFT)


def test_ctrl_within_actuator_range():
    # 超出 ctrlrange 的目标会被 MuJoCo 截断，导致实际姿态与逆运动学结果不符
    model = ArmGraspSandbox().model
    lo, hi = model.actuator_ctrlrange[:, 0], model.actuator_ctrlrange[:, 1]
    total = sum(duration for _, _, duration in GRASP_SEGMENTS)
    for t in np.linspace(0.0, total + 1.0, 200):
        ctrl = scripted_grasp_ctrl(t)
        assert np.all(ctrl >= lo - 1e-9) and np.all(ctrl <= hi + 1e-9)


def test_ball_is_lifted_and_held_between_fingers():
    model, data = _run_scripted_grasp(duration=15.0)

    ball = data.body("target_ball").xpos
    left = data.geom("left_finger_geom").xpos
    right = data.geom("right_finger_geom").xpos

    # 小球被举离地面（静止时球心高度为半径 0.03 m），且在保持阶段没有滑落
    assert ball[2] > 0.25
    # 小球仍夹在两指之间
    assert np.linalg.norm(ball - (left + right) / 2.0) < BALL_RADIUS
    finger_ids = {model.geom("left_finger_geom").id, model.geom("right_finger_geom").id}
    ball_id = model.geom("ball_geom").id
    touching = set()
    for c in data.contact[:data.ncon]:
        pair = {int(c.geom1), int(c.geom2)}
        if ball_id in pair:
            touching |= pair & finger_ids
    assert touching == finger_ids

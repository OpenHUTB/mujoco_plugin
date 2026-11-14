"""
洋流模型单元测试

运行：
    cd src/underwater
    python -m pytest tests/ -v

最后两个仿真测试需要 MuJoCo（未安装时自动跳过），其余测试只依赖 numpy。
"""

import json
import math
import os
import sys
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ocean_current import (CurrentLayer, OceanCurrentCascade, StratifiedCurrent,
                           apply_current_drag)

DT = 0.002

# 与 data/config.json 中的分层剖面一致
LAYERS = [
    {"depth_m": 0,   "speed_ms": 0.0, "horizontal_angle_rad": 0.0, "vertical_angle_rad": 0.0},
    {"depth_m": -10, "speed_ms": 0.5, "horizontal_angle_rad": 0.3, "vertical_angle_rad": 0.0},
    {"depth_m": -50, "speed_ms": 1.0, "horizontal_angle_rad": 0.5, "vertical_angle_rad": 0.1},
]


def _layer_velocity(layer):
    """单层洋流速度向量（MuJoCo 坐标系，Z 向上）"""
    speed = layer["speed_ms"]
    h = layer["horizontal_angle_rad"]
    v = layer["vertical_angle_rad"]
    return np.array([speed * math.cos(v) * math.cos(h),
                     speed * math.cos(v) * math.sin(h),
                     -speed * math.sin(v)])


def _stratified_only_cascade():
    """关闭 Gauss-Markov 与湍流分量，只保留分层洋流"""
    return OceanCurrentCascade({
        "gauss_markov": {"mean_speed": 0.0, "noise_amp": 0.0},
        "stratified_layers": LAYERS,
        "turbulent": {"intensity": 0.0},
    })


# ── 分层洋流 ──────────────────────────────────────────────

def test_stratified_layer_values_at_layer_depths():
    strat = StratifiedCurrent([CurrentLayer(**l) for l in LAYERS])
    for layer in LAYERS:
        v = strat.get_velocity_at(layer["depth_m"], DT)
        assert np.allclose(v, _layer_velocity(layer))


def test_stratified_interpolates_between_layers():
    strat = StratifiedCurrent([CurrentLayer(**l) for l in LAYERS])
    v = strat.get_velocity_at(-30.0, DT)
    expected = 0.5 * _layer_velocity(LAYERS[1]) + 0.5 * _layer_velocity(LAYERS[2])
    assert np.allclose(v, expected)


def test_stratified_clamps_outside_profile():
    strat = StratifiedCurrent([CurrentLayer(**l) for l in LAYERS])
    # 深于最深层 → 最深层；高于水面（浅于最浅层）→ 最浅层
    assert np.allclose(strat.get_velocity_at(-80.0, DT), _layer_velocity(LAYERS[2]))
    assert np.allclose(strat.get_velocity_at(2.0, DT), _layer_velocity(LAYERS[0]))


def test_stratified_layer_order_does_not_matter():
    shuffled = [LAYERS[1], LAYERS[2], LAYERS[0]]
    strat = StratifiedCurrent([CurrentLayer(**l) for l in shuffled])
    assert np.allclose(strat.get_velocity_at(-10.0, DT), _layer_velocity(LAYERS[1]))


# ── 级联模型 ──────────────────────────────────────────────

@pytest.mark.parametrize("layer", LAYERS)
def test_cascade_uses_layer_at_robot_z(layer):
    """机器人位于某层深度 (z = depth_m) 时，应得到该层的流速"""
    ocean = _stratified_only_cascade()
    v = ocean.get_velocity(0.0, 0.0, layer["depth_m"], DT)
    assert np.allclose(v, _layer_velocity(layer))


def test_cascade_current_grows_with_depth():
    ocean = _stratified_only_cascade()
    speeds = [np.linalg.norm(ocean.get_velocity(0.0, 0.0, z, DT))
              for z in (-1.0, -5.0, -10.0, -30.0, -50.0)]
    assert speeds[0] > 0.0
    assert all(a < b for a, b in zip(speeds, speeds[1:]))


# ── 洋流拖曳力 ────────────────────────────────────────────

def test_drag_pushes_along_current():
    data = SimpleNamespace(xfrc_applied=np.zeros((2, 6)))
    apply_current_drag(data, 1, np.array([0.5, -0.2, 0.1]), drag_coeff=10.0)
    assert np.allclose(data.xfrc_applied[1, :3], [5.0, -2.0, 1.0])
    assert np.allclose(data.xfrc_applied[1, 3:], 0.0)
    assert np.allclose(data.xfrc_applied[0], 0.0)


def test_drag_adds_to_existing_force():
    """拖曳力应叠加在浮力等已施加的外力上"""
    data = SimpleNamespace(xfrc_applied=np.zeros((1, 6)))
    data.xfrc_applied[0, 2] = 100.0
    apply_current_drag(data, 0, np.array([0.0, 0.0, -1.0]), drag_coeff=10.0)
    assert np.isclose(data.xfrc_applied[0, 2], 90.0)


def test_rov_drifts_downstream_in_mujoco():
    """中性浮力的 ROV 在 +X 洋流中应顺流漂移"""
    mujoco = pytest.importorskip("mujoco")
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "data", "rov_base.xml")
    model = mujoco.MjModel.from_xml_path(model_path)
    model.opt.density = 1000.0
    model.opt.viscosity = 0.00089
    data = mujoco.MjData(model)
    body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "rov")
    weight = -model.opt.gravity[2] * model.body_subtreemass[body_id]

    for _ in range(int(2.0 / model.opt.timestep)):
        data.xfrc_applied[body_id] = 0.0
        data.xfrc_applied[body_id, 2] = weight  # 抵消重力，只看洋流的作用
        apply_current_drag(data, body_id, np.array([0.5, 0.0, 0.0]), drag_coeff=10.0)
        mujoco.mj_step(model, data)

    assert data.qpos[0] > 0.0
    assert data.qvel[0] > 0.0


def test_scenario_current_force_does_not_accumulate(tmp_path):
    """仿真循环每一步的洋流拖曳力应保持恒定，而不是逐步叠加"""
    pytest.importorskip("mujoco")
    pytest.importorskip("matplotlib")
    from underwater_sim import UnderwaterSimulation, _DEFAULT_CONFIG, _HERE

    with open(_DEFAULT_CONFIG, encoding="utf-8") as f:
        config = json.load(f)
    config["duration_seconds"] = 2.0
    config["ocean_drag_coeff"] = 10.0
    # 恒定的竖直向上洋流 1 m/s（垂直角 -pi/2 表示向上）
    config["ocean_current"] = {
        "enabled": True,
        "gauss_markov": {"mean_speed": 1.0, "mean_vertical_angle": -math.pi / 2,
                         "noise_amp": 0.0},
        "stratified_layers": [],
        "turbulent": {"intensity": 0.0},
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    sim = UnderwaterSimulation(config_path=config_path,
                               model_path=_HERE / "data" / "rov_base.xml")
    # 无流体、无浮力：只有重力和恒定的 10 N 向上拖曳力
    t, z, _ = sim.run_scenario(density=0.0, viscosity=0.0, apply_buoyancy=False)

    accel = -config["gravity"] + 10.0 * 1.0 / config["rov_body"]["mass"]
    assert np.allclose(z, -1.0 + 0.5 * accel * t ** 2, atol=0.05)

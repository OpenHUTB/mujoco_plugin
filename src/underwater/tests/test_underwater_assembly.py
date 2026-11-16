"""
水下机器人装配体（ROV + UR5e + Robotiq 2F-85）测试

运行：
    cd src/underwater
    python -m pytest tests/ -v

网格文件检查只依赖标准库；装配相关测试需要 MuJoCo（未安装时自动跳过）。
装配测试会像 build_underwater_rov.py 一样生成 ur5e_with_gripper.xml、
data/meshes/ 与 data/underwater_rov_with_arm.xml，这些文件均不纳入版本控制。
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_MENAGERIE = Path(__file__).resolve().parents[3] / "assets" / "mujoco_menagerie"


# ── 仓库自带的 Menagerie 模型 ─────────────────────────────

@pytest.mark.parametrize("model_xml", [
    "universal_robots_ur5e/ur5e.xml",
    "robotiq_2f85/2f85.xml",
])
def test_menagerie_mesh_files_are_bundled(model_xml):
    """模型引用的每个网格文件都必须随仓库提供"""
    xml_path = _MENAGERIE / model_xml
    root = ET.parse(xml_path).getroot()
    compiler = root.find("compiler")
    meshdir = compiler.get("meshdir", "") if compiler is not None else ""

    files = [mesh.get("file") for mesh in root.iter("mesh") if mesh.get("file")]
    assert files
    missing = [f for f in files if not (xml_path.parent / meshdir / f).is_file()]
    assert missing == []


# ── 装配流程 ──────────────────────────────────────────────

def test_build_assembly_without_viewer(monkeypatch):
    mujoco = pytest.importorskip("mujoco")
    import mujoco.viewer
    from build_underwater_rov import build_underwater_assembly

    def fail_launch(*args, **kwargs):
        raise AssertionError("launch_viewer=False 时不应打开 Viewer")

    monkeypatch.setattr(mujoco.viewer, "launch", fail_launch)

    model_path = build_underwater_assembly(launch_viewer=False)

    model = mujoco.MjModel.from_xml_path(str(model_path))
    for body in ("rov", "base", "wrist_3_link", "gripper_base"):
        assert mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, body) != -1
    for actuator in ("shoulder_pan", "wrist_3", "gripper_fingers_actuator"):
        assert mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, actuator) != -1


def _import_underwater_sim(monkeypatch, default_model):
    """导入 underwater_sim，并把默认模型路径与装配函数替换为可观测的版本"""
    pytest.importorskip("mujoco")
    pytest.importorskip("matplotlib")
    import underwater_sim

    calls = []
    monkeypatch.setattr(underwater_sim, "_DEFAULT_MODEL", default_model)
    monkeypatch.setattr(underwater_sim, "build_underwater_assembly",
                        lambda **kwargs: calls.append(kwargs))
    return underwater_sim, calls


def test_simulation_builds_missing_default_model(monkeypatch, tmp_path):
    default_model = tmp_path / "underwater_rov_with_arm.xml"
    underwater_sim, calls = _import_underwater_sim(monkeypatch, default_model)

    underwater_sim.UnderwaterSimulation(model_path=default_model)

    assert calls == [{"launch_viewer": False}]


def test_simulation_keeps_existing_default_model(monkeypatch, tmp_path):
    default_model = tmp_path / "underwater_rov_with_arm.xml"
    default_model.write_text("<mujoco/>", encoding="utf-8")
    underwater_sim, calls = _import_underwater_sim(monkeypatch, default_model)

    underwater_sim.UnderwaterSimulation(model_path=default_model)

    assert calls == []


def test_simulation_does_not_build_for_custom_model(monkeypatch, tmp_path):
    underwater_sim, calls = _import_underwater_sim(
        monkeypatch, tmp_path / "underwater_rov_with_arm.xml")

    underwater_sim.UnderwaterSimulation(model_path=tmp_path / "custom.xml")

    assert calls == []

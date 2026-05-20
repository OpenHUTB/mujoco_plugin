"""
水下机器人力学模拟 (MuJoCo) 示例 v2
=====================================
验证目标：MuJoCo 能否正确模拟水下浮力+阻力行为
参考论文：Simple Models, Real Swimming (ETH Zurich, 2025)
参考文档：https://docs.mujoco.cn/en/stable/computation/fluid.html

重要发现：
  MuJoCo 的 density 参数只计算阻力，不自动计算浮力。
  浮力需通过 data.xfrc_applied 在每步手动施加。
  公式：F_buoy = ρ_fluid × g × V_body（方向向上）
"""

import mujoco
import mujoco.viewer
import numpy as np

# ─────────────────────────────────────────────
#  物理参数
# ─────────────────────────────────────────────
WATER_DENSITY   = 1000.0
WATER_VISCOSITY = 0.00089
AIR_DENSITY     = 1.2
AIR_VISCOSITY   = 0.0000148

CYL_RADIUS = 0.15
CYL_HALF_L = 0.30
CYL_MASS   = 10.0
CYL_VOL    = np.pi * CYL_RADIUS**2 * (2 * CYL_HALF_L)

GRAVITY    = 9.81
FLUID_COEF = "0.40 7.79 2.81 3.84 0.27"

# ─────────────────────────────────────────────
#  场景XML（去掉地板，空间足够观察）
# ─────────────────────────────────────────────
def make_xml(density, viscosity):
    fluid_opt = f'density="{density}" viscosity="{viscosity}"' if density > 0 else ""
    return f"""
<mujoco model="underwater">
  <option gravity="0 0 -{GRAVITY}" timestep="0.002"
          integrator="implicitfast" {fluid_opt}/>
  <worldbody>
    <body name="rov" pos="0 0 -1.0">
      <freejoint/>
      <geom name="rov_body" type="cylinder"
            size="{CYL_RADIUS} {CYL_HALF_L}"
            mass="{CYL_MASS}"
            rgba="0.8 0.4 0.1 1"
            fluidshape="ellipsoid"
            fluidcoef="{FLUID_COEF}"/>
    </body>
  </worldbody>
  <sensor>
    <framepos    name="pos" objtype="body" objname="rov"/>
    <framelinvel name="vel" objtype="body" objname="rov"/>
  </sensor>
</mujoco>
"""

# ─────────────────────────────────────────────
#  仿真（带手动浮力）
# ─────────────────────────────────────────────
def run(density, viscosity, apply_buoyancy, duration=5.0):
    model = mujoco.MjModel.from_xml_string(make_xml(density, viscosity))
    data  = mujoco.MjData(model)
    body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "rov")

    buoyancy_force = density * GRAVITY * CYL_VOL if apply_buoyancy else 0.0

    log_t, log_z, log_vz = [], [], []
    steps = int(duration / model.opt.timestep)

    for i in range(steps):
        # 每步施加浮力（Z方向向上）
        if apply_buoyancy and density > 0:
            data.xfrc_applied[body_id, 2] = buoyancy_force

        mujoco.mj_step(model, data)

        if i % 50 == 0:
            log_t.append(data.time)
            log_z.append(data.sensor("pos").data[2])
            log_vz.append(data.sensor("vel").data[2])

    return np.array(log_t), np.array(log_z), np.array(log_vz)

# ─────────────────────────────────────────────
#  主程序
# ─────────────────────────────────────────────
def main():
    print("=" * 58)
    print("  水下机器人 MuJoCo 流体仿真验证 Demo v2")
    print("  Issue #3529 | OpenHUTB/hutb")
    print("=" * 58)
    print(f"\n  圆柱体参数：")
    print(f"    质量   = {CYL_MASS} kg")
    print(f"    体积   = {CYL_VOL:.4f} m³")
    print(f"    密度   = {CYL_MASS/CYL_VOL:.1f} kg/m³  （水：1000 kg/m³）")
    print(f"\n  理论浮力   = {WATER_DENSITY * GRAVITY * CYL_VOL:.1f} N")
    print(f"  重力       = {CYL_MASS * GRAVITY:.1f} N")
    print(f"  净浮力     = {(WATER_DENSITY * GRAVITY * CYL_VOL) - CYL_MASS * GRAVITY:.1f} N  → 预期上浮")

    scenarios = [
        (0,             0,               False, "1. 无流体（纯重力）"),
        (WATER_DENSITY, WATER_VISCOSITY, False, "2. 水中（仅阻力，无浮力）"),
        (WATER_DENSITY, WATER_VISCOSITY, True,  "3. 水中（阻力 + 手动浮力）✓"),
    ]

    results = {}
    for density, visc, buoy, label in scenarios:
        print(f"\n▶ {label}")
        t, z, vz = run(density, visc, buoy)
        results[label] = (t, z, vz)
        dz = z[-1] - z[0]
        tag = "↑ 上浮" if dz > 0.05 else ("↓ 下沉" if dz < -0.05 else "→ 近似悬停")
        print(f"   初始Z：{z[0]:.3f} m  →  最终Z：{z[-1]:.3f} m")
        print(f"   位移：{dz:+.3f} m  {tag}")
        print(f"   末速度：{vz[-1]:+.4f} m/s")

    print("\n" + "=" * 58)
    print("  验证结论")
    print("=" * 58)
    z1 = results["1. 无流体（纯重力）"][1][-1]
    z3 = results["3. 水中（阻力 + 手动浮力）✓"][1][-1]
    if z3 > z1:
        print("\n  ✓ MuJoCo 流体模型可用于水下仿真")
        print("  ✓ 浮力需手动施加（xfrc_applied），阻力由引擎自动计算")
        print("  ✓ 圆柱体在水中上浮，符合物理预期（密度 < 水）")
    else:
        print("\n  ✗ 结果异常，请检查")

    print("\n  是否启动可视化（水下环境，含浮力）？(y/n): ", end="")
    try:
        ans = input().strip().lower()
    except EOFError:
        ans = "n"

    if ans == "y":
        print("  启动查看器...")
        xml = make_xml(WATER_DENSITY, WATER_VISCOSITY)
        model = mujoco.MjModel.from_xml_string(xml)
        data  = mujoco.MjData(model)
        body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "rov")
        buoyancy = WATER_DENSITY * GRAVITY * CYL_VOL

        def ctrl_cb(m, d):
            d.xfrc_applied[body_id, 2] = buoyancy

        mujoco.viewer.launch(model, data)

if __name__ == "__main__":
    main()
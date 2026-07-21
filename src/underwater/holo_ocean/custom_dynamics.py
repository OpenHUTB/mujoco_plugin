import numpy as np
import holoocean
from holoocean.agents import HoveringAUV
from scipy.spatial.transform import Rotation

scenario = {
    "name": "hovering_dynamics",
    "package_name": "Ocean",
    "world": "SimpleUnderwater",
    "main_agent": "auv0",
    "agents": [
        {
            "agent_name": "auv0",
            "agent_type": "HoveringAUV",
            "sensors": [
                {
                    "sensor_type": "DynamicsSensor",
                    "configuration":{
                        "UseRPY": False # 使用四元数
                    }
                },
            ],
            "control_scheme": 2, # 这是 Custom Dynamics 的控制方案。
            "location": [0,0,-10],
            "rotation": [20,20,90]
        }
    ]
}

g = 9.81 # 重力
b = 3 # 线性阻尼
c = 2 # 角阻尼
# HoveringAUV.mass += 1 # 或者让它下沉

def f(x):
    # 从状态中提取所有信息
    a = x[:3]
    v = x[3:6]
    p = x[6:9]
    alpha = x[9:12]
    omega = x[12:15]
    quat = x[15:19]
    R = Rotation.from_quat(quat).as_matrix()

    # 对所有力求和
    force = np.zeros(3)
    force[2] += -HoveringAUV.mass * g # 重力
    force[2] += HoveringAUV.water_density * g * HoveringAUV.volume # 浮力
    force -= v*b # 阻尼

    # 对所有力矩求和
    torque = np.zeros(3)
    buoy_force = HoveringAUV.water_density*g*HoveringAUV.volume*np.array([0,0,1]) # 在全局坐标系中
    cob = R@HoveringAUV.cob # 将浮心移动至全局坐标系
    torque += np.cross(cob, buoy_force) # 浮力产生的力矩
    torque -= omega*c # 阻尼

    # 将力和力矩转换为加速度
    lin_accel = force / HoveringAUV.mass
    ang_accel = np.linalg.inv(HoveringAUV.I)@torque
    return np.append(lin_accel, ang_accel)

u = np.zeros(6)
# 构建环境
with holoocean.make(scenario_cfg=scenario) as env:
    for i in range(500):
        # 步进仿真
        state = env.step(u)
        # 获取要传递给 HoloOcean 的加速度数据
        u = f(state["DynamicsSensor"])
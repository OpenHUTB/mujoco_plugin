# 手动定义动力学

很多时候，能够轻松实现自定义动力学对研究可能有用。为此，我们为 [HovingAUV](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/hovering-auv-agent.html#hovering-auv-agent) 创建了控制器，这些控制器接收线性和角加速度，并将其集成以实现自定义动力学。除了碰撞，模拟器中没有对车辆施加其他加速度，从而允许在python中实现完全自定义的动力学。这种可能性是无限的，包括复杂的流体力学、水流等。

此外，动力学传感器 [DynamicsSensor](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.DynamicsSensor) 旨在提供计算动力学所需的所有必要当前状态信息，包括加速度、速度和当前姿态信息。

以下是一个实际应用示例，其中手动实现了重力、浮力和阻尼。

```python
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
```

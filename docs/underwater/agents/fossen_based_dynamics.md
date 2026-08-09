# 基于 Fossen 模型的动力学

水下航行器和水面航行器的动力学特性，可以通过 挪威科技大学 Thor Fossen 在其著作[《海洋航行器流体动力学与运动控制手册》（*Handbook of Marine Craft Hydrodynamics and Motion Control*）](https://github.com/cybergalactic/FossenHandbook)中推导出的运动方程进行建模。Fossen 已在其 [GitHub 仓库](https://github.com/cybergalactic/PythonVehicleSimulator)（包含自主水下航行器、无人水面航行器和船舶的模型）中提供了这些动力学模型的便捷实现。我们将 Fossen 的部分实现移植到了 HoloOcean 中，以便进行精确的航行器动力学仿真。

在 HoloOcean 中使用基于 Fossen 理论的动力学模型，是对“自定义动力学”（Custom Dynamics）控制方案的一种扩展。若要使用内置的 Fossen 动力学模型，只需按照几个步骤即可配置这些改进的水下航行器动力学特性。以下是在 HoloOcean 中设置 Fossen 动力学模型的步骤概要；后续章节将提供更详细的说明与示例：

**1.**在场景配置的代理（agent）字典中，将 `fossen_model` 键设置为相应的 Fossen 动力学类。可用的 Fossen 动力学类列在下方的“Fossen 载具类”一节中。

**2.**在代理字典中，将控制方案（`control_scheme`）键设置为该代理所使用的自定义动力学控制方案对应的值（参见[控制方案](./control_schemes.md)）。

**3.**在代理的传感器列表中设置一个动力学传感器（Dynamics Sensor）。该传感器用于读取载具状态并应用动力学模型。

**4.**您还可以选择在代理配置中设置动力学、执行器（actuator）和自动驾驶（autopilot）参数。这些参数定义了载具的动力学特性、控制面以及自动驾驶设置。此功能仅适用于定义了 `configure_from_scenario` 函数的 Fossen 动力学模型。

**5.**最后，在您的仿真脚本中创建一个福森接口（`FossenInterface`）管理器对象，并传入代理名称列表及场景配置。该类在 [fossen_interface.py](https://github.com/byu-holoocean/HoloOcean/blob/release/client/src/holoocean/fossen_dynamics/fossen_interface.py) 中实现。



# MJCF 导入

Unreal Robotics Lab 可以导入标准的 MuJoCo XML (MJCF) 文件，并将完整的模型层级结构重建为 Unreal 组件。您可以从 MuJoCo Menagerie 或您自己的项目中获取 [.xml](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLab/Private/MuJoCo/Core/MjPhysicsEngine.cpp#L255) 模型，然后将其直接拖入内容浏览器。

---

## 导入

1. 将 [.xml](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLab/Private/MuJoCo/Core/MjPhysicsEngine.cpp#L255) 文件拖入虚幻**内容浏览器(Content Browser)** 。
2. 首次导入时，编辑器会提示安装所需的 Python 包（[trimesh](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLabEditor/Private/MjPythonHelper.cpp#L168)、[numpy](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLabEditor/Private/MjPythonHelper.cpp#L168)、[scipy](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLabEditor/Private/MjPythonHelper.cpp#L168)）。默认情况下，这些包会安装到 UE 自带的 Python 环境中，无需额外配置 Python。您也可以通过对话框选择自定义解释器（conda、venv 等）。所选路径会保存到 [Config/LocalUnrealRoboticsLab.ini](https://github.com/OpenHUTB/UnrealRoboticsLab/tree/main/Config) 文件中（每个机器单独保存，不会提交到源代码控制系统）。
3. [UMujocoImportFactory](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLabEditor/Private/MujocoImportFactory.cpp#L38) 使用配置的 Python 运行清洗网格脚本 [Scripts/clean_meshes.py](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Scripts/clean_meshes.py):
   - 解析 XML 以查找所有引用的网格资产
   - 检测 GLB stem 冲突（例如，[link1.obj](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Scripts/clean_meshes.py#L27) 和 [link1.stl](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Scripts/clean_meshes.py#L27) 两者都产生 [link1.glb](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Scripts/clean_meshes.py#L27)），并重命名它们。
   - 将网格转换为 GLB 格式（保留 UV，去除嵌入纹理）
   - 生成带有更新网格参考的 [_ue.xml](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLabEditor/Private/MujocoImportFactory.cpp#L106)
   - 如果用户跳过 Python 设置，则会使用原始 XML（某些网格可能无法正确显示）。
4. 工厂通过四次解析过程创建 [铰链 AMjArticulation](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLab/Public/MuJoCo/Core/MjPhysicsEngine.h#L34) 蓝图：
   - **第一阶段：** 资产（带缩放的网格、带文件路径的纹理、带 RGBA/纹理引用的材质）
   - **第二阶段：** 默认值（类层次结构作为 [UMjDefault](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Source/URLab/Public/MuJoCo/Components/MjComponent.h#L33) 组件）
   - **第三阶段：** Worldbody (递归的刚体(body)/几何(geom)/关节(joint)/位点(site)层次结构)
   - **第四阶段：** 执行器、传感器、肌腱、equalities、关键帧、接触 对/排除
5. 将蓝图放置在关卡中，即可进行模拟。

### 准备 Mujoco MJCF 网格

脚本 [Scripts/clean_meshes.py](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Scripts/clean_meshes.py) 准备用于虚幻导入的 MuJoCo MJCF 网格，用于解析 MJCF XML 文件，将所有引用的网格模型（OBJ、STL）转换为 GLB 格式，解决命名冲突（例如，link1.obj 和 link1.stl 均转换为 link1.glb 的情况），并生成一份已更新的 XML 文件，以便直接拖拽导入 Unreal 引擎。

安装：
```shell
# cd hutb\Unreal\CarlaUE4\Plugins\UnrealRoboticsLab\Scripts
# conda create -n nn_3.11 python=3.11 --yes
# conda activate nn_3.11
pip install trimesh numpy
```
Python 3.7 安装过程
```shell
pip install trimesh numpy scipy
```

使用：
```shell
# cd hutb\Unreal\CarlaUE4\Plugins\UnrealRoboticsLab\Scripts
python clean_meshes.py <path_to_xml>
# 示例
python clean_meshes.py hutb\Unreal\CarlaUE4\Plugins\UnrealRoboticsLab\URLab_Bridge\RoboJuDo\assets\robots\g1\g1_29dof_rev_1_0.xml
# 会在 xml 所在统一目录下生成 g1_29dof_rev_1_0_ue.xml，用于拖转到虚幻编辑器的 Content Browser
```


---

## 创建的内容

| MJCF 元件 | 虚幻组件 |
|-------------|-----------------|
| `<body>` | `UMjBody` (保留递归层次结构) |
| `<joint>` | `UMjHingeJoint`, `UMjSlideJoint`, `UMjBallJoint`, `UMjFreeJoint` |
| `<geom>` | `UMjGeom` / 原始子类 |
| `<site>` | 位点 `UMjSite` |
| `<actuator>` | `UMjMotorActuator`, `UMjPositionActuator`,’ 等 |
| `<sensor>` | `UMjTouchSensor`, `UMjGyro` 等 (30 多种类型) |
| `<tendon>` | `UMjTendon` |
| `<equality>` | `UMjEquality` |
| `<keyframe>` | `UMjKeyframe` |
| `<default>` | `UMjDefault` |
| `<camera>` | `UMjCamera` |

---

## 编译器设置

导入器关于 MJCF `<compiler>` 元素：

| 属性 | 效果 |
|-----------|--------|
| `angle="degree"` / `"radian"` | 如何解读关节的限制和位置 |
| `autolimits="true"` | 当 `range` 设置后自动启动限制 |
| `eulerseq` | 用于调整物体姿态的欧拉旋转序列 |

---

## 默认值如何工作

MuJoCo XML 中的 `<default>` 块定义了子元素通过类名继承的共享属性。导入后，这些块会成为 `UMjDefault` 连接组件树中的组件。

这些组件**并非**仅供参考，而是实际存在的组件。插件在编译过程中会将它们用于将蓝图**转换回** MuJoCo 的内部表示形式。每个组件都会检查其分配的属性 `ClassName` 是否与默认链匹配，MuJoCo 会在规范编译时应用继承关系，就像处理原始 XML 一样。

这意味着：

- 编辑某个 `UMjDefault` 组件会影响所有引用该默认类的组件。
- 默认层次结构（嵌套默认值）得以保留并正常运行。
- 如果移除默认值，则依赖该默认值的组件将回退到它们自己的显式属性值。

---

## FromTo 解析

使用该 `fromto` 属性定义的几何体在导入时会解析为显式的 `pos`、`quat`和 `size`。解析过程会考虑类型：


| 几何类型 | 尺寸映射 |
|-----------|-------------|
| 胶囊体（Capsule）/ 圆柱体（Cylinder） | `size[1]` = 沿线段长度的一半 |
| 盒子（Box） / 椭圆球（Ellipsoid） | `size[2]` = 沿线段长度的一半 |

导入后，组件存储的是已解析的变换，`fromto` 而不是已解析的变换。

---

## 材质与纹理

导入器会创建以 XML `<material>` 名称为键的共享 Unreal 材质实例。所有引用相同材质名称的几何体共享同一个实例（例如，所有 `material="white"` 使用 ` <material_name>` 的几何体都使用 `MI_white`）。元素引用的纹理 `<texture>` 会应用到相应的材质实例上。

---

## 网格资产

导入程序会查找 XML 文件所在目录下的网格文件。网格文件会被复制到导入目标目录下的 `/meshes/` 子文件夹中，以避免纹理名称冲突，然后在编译期间注册到 MuJoCo 的 VFS 中。

**格式优先级：** GLB > OBJ。导入器首先尝试导入 GLB 文件（通过 Interchange），然后尝试导入原始 OBJ/STL 文件。如果所有路径都失败，则会创建不带可视网格的几何体，但该几何体仍作为碰撞图元存在。此时会记录一条警告信息，但编译仍然会成功。

**自动网格准备：** `clean_meshes.py` 脚本会在导入过程中自动运行（参见上文[导入](#importing)部分）。您也可以手动运行它：

```bash
python Scripts/clean_meshes.py path/to/robot.xml
```

这将生成一个包含更新后的网格引用的 [_ue.xml](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Scripts/clean_meshes.py#L256) 文件，您可以将其拖入 Unreal 中，而不是使用原始 XML 文件。


**手动安装软件包：** 如果您不想使用对话框，而是希望自行安装软件包，请使用您首选的 Python 解释器运行以下命令：

```bash
/path/to/your/python -m pip install trimesh numpy scipy
```
随后，请确保在 [Config/LocalUnrealRoboticsLab.ini](https://github.com/OpenHUTB/hutb/tree/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Config) 文件中设置了相同的 Python 路径（详见下文）。插件将在下次导入时自动检测相关包，并跳过安装提示。



**更改 Python 解释器：** 插件会将您的 Python 路径存储在插件目录下的 [Config/LocalUnrealRoboticsLab.ini](https://github.com/OpenHUTB/hutb/tree/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Config) 文件中。该文件已被 .gitignore 忽略（每台机器单独设置）。要切换解释器，您可以删除该文件（下次导入时对话框将重新出现），或者直接编辑该文件： 

```ini
[PythonSettings]
PythonPath=C:/Users/you/miniconda3/envs/myenv/python.exe
```

---

## 调试导入问题

启用 [UMjPhysicsEngine](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLab/Public/MuJoCo/Core/MjPhysicsEngine.h#L60) 的 [bSaveDebugXml](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLab/Public/MuJoCo/Core/MjPhysicsEngine.h#L139) 功能，即可在编译后将 [scene_compiled.xml](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLab/Private/MuJoCo/Core/MjPhysicsEngine.cpp#L255) 和 [scene_compiled.mjb](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLab/Private/MuJoCo/Core/MjPhysicsEngine.cpp#L241)（MuJoCo Binary） 保存到 [Saved/URLab/](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/352a9ea7bdce0eaa9e1bd365454f3b7ea421d44c/Source/URLab/Private/MuJoCo/Core/MjPhysicsEngine.cpp#L273) 目录。对比原始 MJCF 和编译后的 XML 文件，找出导入/导出不匹配之处（例如缺少元素、属性值错误、默认继承关系损坏）。编译后的 XML 文件也可以加载到原生 MuJoCo 中进行验证。更多信息请参阅 [URLab 编辑器](../dev/URLabEditor.md)、[开发者工具](developer_tools.md) 。


## 导入后

导入的关节是一个普通的虚幻引擎参与者。您可以重新排列组件、添加传感器或摄像机、覆盖属性，或将其保存为可重用的蓝图。XML 仅在导入期间读取——之后，虚幻引擎组件才是最终的数据源。

有关导入流程内部结构的完整详细信息，请参阅 [架构](../architecture.md#import-pipeline) 部分。


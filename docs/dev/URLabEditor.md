# URLab 编辑器

编辑器（[URLabEditor](https://github.com/OpenHUTB/hutb/tree/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor)）模块提供了将 MuJoCo 的 MJCF XML 定义与虚幻引擎的参与者（Actor）和组件（Component）系统相桥接所需的专用工具。该模块负责处理资源导入流程、网格预处理以及编辑器端的自定义设置，使用户能够在虚幻编辑器环境中管理复杂的机器人资源。


编辑工具的主要目标是自动将层次化的 XML 机器人描述转换为功能性的 [AMjArticulation](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLab/Public/MuJoCo/Core/MjPhysicsEngine.h#L34) 蓝图，该蓝图包含物理就绪的组件和优化的几何体。

## 系统概述：从MJCF到蓝图

下图展示了从原始 MJCF 文件到虚幻编辑器中生成机器人的高层流程。

```mermaid
flowchart TD
    subgraph subGraph2 ["Asset Space"]
        H["StaticMesh Assets"]
        I["AMjArticulation Blueprint"]
    end
    subgraph subGraph1 ["Editor Code Space (URLabEditor)"]
        C["UMujocoImportFactory"]
        D["MujocoXmlParser"]
        E["MujocoMeshImporter"]
        F["UMjPythonHelper"]
        G["UMujocoGenerationAction"]
    end
    subgraph subGraph0 ["Natural Language Space"]
        A["MJCF XML File"]
        B["Mesh Assets (STL/OBJ)"]
    end
    A --> C
    B --> E
    C --> D
    D --> G
    E --> F
    F --> H
    G --> I
```

### MJCF 导入管线

导入流程是一个多阶段的过程，当将 .xml 文件拖入虚幻内容浏览器时，该流程即开始。[UMujocoImportFactory](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoImportFactory.cpp#L51) 会拦截此操作，并协调多个专用类将 MuJoCo 场景图重建为虚幻引擎的参与者。

* 1.**XML 解析**：[MujocoXmlParser](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoXmlParser.cpp) 读取 MJCF 结构，并将 MuJoCo 元素（物体、关节、几何体）映射到其对应的UMjComponent子类。 尝试运行 clean_meshed.py 来准备网格。

    1.1.确保引擎的 Python 是否准备好（包括检查 Python 和[依赖的包](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MjPythonHelper.cpp#L228)）。位于 hutb\Build\engine\Engine\Binaries\ThirdParty\Python3\Win64\Python.exe 。

    1.2.运行网格准备：[python clean_mesh.py g1_29dof_rev_1_0.xml](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoImportFactory.cpp#L100)

    1.3.将导入用的原始 XML 文件路径写入新建蓝图的类默认对象（Class Default Object, CDO），以便该路径随蓝图资产持久保存并能在编辑器/运行时访问。

* 2.**网格处理**（使用已准备好的 XML [生成](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoImportFactory.cpp#L141) [蓝图](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp#L80) 组件）：由于 MuJoCo 经常使用可能未针对虚幻引擎优化的 STL（立体光刻、Stereolithography：描述三角面片组成的 3D 模型表面）或 OBJ 文件，因此 [MujocoMeshImporter](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoMeshImporter.cpp) （由 [UMjPythonHelper](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MjPythonHelper.cpp) 支持）负责将其转换为 GLB 格式，并进行三角网格清理。

* 3.**蓝图生成**：[编译](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp#L98)来保存修改，并确保组件是有效的。  [UMujocoGenerationAction](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp) 接收解析后的组件树，并通过编程方式构建一个从 [AMjArticulation](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLab/Public/MuJoCo/Core/MjPhysicsEngine.h#L34) 派生的蓝图类。

    导入的资产位于项目的：Content/MuJoCoImports/g1_29dof_rev_1_0_ue_ue_Assets 目录下。

    3.0. [预扫描](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp#L133)：收集默认网格比例，以便资源解析能够继承这些比例。

    3.1 传递：已处理的资产。[导入纹理](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp#L149) 中的 [导入单个纹理](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoMeshImporter.cpp#L343) 失败，[FFileHelper::LoadFileToArray](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoMeshImporter.cpp#L365) 失败。放在纹理资产变量 TextureAsserts（值 D:\hutb\Unreal\CarlaUE4\Content\Humanoid\robots\g1/**groundplane** 为空） 中。

    核心为**递归解析资产**：
        如果这是一个容器，请在直接子项中查找编译器标签，以便为所有同级项设置目录覆盖。
        递归处理顶级容器（不包括上面处理过的标签，如 include/asset）。

    3.2. 动态创建组织节点。首先解析编译器设置（角度、eulerseq），以便将其传播到 \<default>-block 导入中——默认类中的关节范围取决于编译器级别的`angle`设置。然后分别解析：默认、接触对和排除项、等式约束、关键帧、结构遍历（worldbody [递归导入节点（ImportNodeRecursive）](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp#L208) 报错）；解析\<option>并存储在articulation CDO中，以便AAMjManager在运行时应用它们。


有关这些类和数据映射逻辑的详细介绍，请参阅 **[MJCF导入管线](../guides/mujoco_import.md)** 。


---

### 编辑器自定义设置与Python助手

为了满足机器人仿真领域的独特需求，编辑器模块包含了多个用户界面（UI）和后端扩展。

- **自定义细节面板**：[UMjGeomDetailCustomization](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MjComponentDetailCustomizations.cpp) 几何组件提供了一个定制界面，允许用户可视化特定于 MuJoCo 的属性（如摩擦力 `friction` 或 `solimp`），这些属性不属于标准虚幻引擎静态网格组件（`UStaticMeshComponent`）属性的一部分。
- **Python 集成**：[UMjPythonHelper](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MjPythonHelper.cpp) 负责管理绑定的 Python 脚本（如 [clean_meshes.py](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Scripts/clean_meshes.py)）。它确保编辑器能够获取如 trimesh 和 numpy 等依赖库，以便进行自动网格清理和凸分解。
- **模块结构**: [URLabEditor](https://github.com/OpenHUTB/hutb/tree/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor) 模块与运行时 [URLab](https://github.com/OpenHUTB/hutb/tree/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLab) 模块严格分离，以确保仅供编辑器使用的依赖项（如 [UnrealEd](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/Converters/SimReady/Source/SimReadyUSD/Private/SimReadyUSDImporterHelper.cpp#L7) 或 [KismetCompiler](https://github.com/OpenHUTB/engine/tree/hutb/Engine/Source/Editor/KismetCompiler/Public/KismetCompiler.h#L13) ）不会包含在已发布的版本中。

---

### 关键编辑工具与脚本

该存储库包含一个 [Scripts/](https://github.com/OpenHUTB/hutb/tree/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Scripts) 目录，其中包含支持编辑器管线的独立工具。

| 脚本 | 目的 | 代码参考 |
| --- | --- | --- |
| [clean_meshes.py](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Scripts/clean_meshes.py) | 将网格转换为 GLB 格式，并修复 Unreal 中的方向（Z轴向上）。 | [Scripts/clean_meshes.py48-61](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Scripts/clean_meshes.py#L48-L61) |
| [generate_subclasses.py](https://github.com/OpenHUTB/hutb/blob/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Scripts/generate_subclasses.py) | 为新的 MuJoCo 组件类型构建 C++ 类框架。 | [Scripts/generate_subclasses.py37-83](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Scripts/generate_subclasses.py#L37-L83) |

**代码实体映射：网格清理流程**

```mermaid
flowchart LR
    subgraph subGraph2 ["Unreal Editor"]
        PH["UMjPythonHelper"]
        MI["MujocoMeshImporter"]
    end
    subgraph subGraph1 ["Python Tooling"]
        CM["clean_meshes.py"]
        F_CM["clean_mesh()"]
        F_CV["convert_mesh()"]
    end
    subgraph subGraph0 ["External Dependencies"]
        TM["trimesh"]
        NP["numpy"]
    end
    TM --> F_CM
    NP --> F_CM
    F_CM --> F_CV
    F_CV --> PH
    PH --> MI
```


### 报错解决方案

* 运行到 [GenerateForBlueprintXml()](https://github.com/OpenHUTB/hutb/blob/f49dd4dd8c0effaa4a07b81a4a53248682fe7e5c/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp#L96) 虚幻编辑器提示：导入"meshes/*.glb"失败。未知扩展名"glb"。

    解决：启用 glTF 插件（注意是小写 l 不是大写的 I）。备注：安装 [glTF](https://github.com/rdeioris/glTFRuntime/releases/download/20220823/glTFRuntime_20220823_426.zip) 插件解决不了。

* 调试模式报错：[FPlatformMisc::IsDebuggerPresent()](https://github.com/OpenHUTB/engine/blob/hutb/Engine/Source/Runtime/Slate/Private/Framework/Application/SlateApplication.cpp#L1875)在无人值守脚本模式下运行时，一个模态窗口试图接管控制。该窗口已被取消。

    解决：在 VS 中点击`开始执行（不调试）`。


* 在编辑器中拖入生成的蓝图并运行报错：
    ```text
    MuJoCo compile failed:

    Error: mesh 'g1_29dof_rev_1_4_pelvis_contour_link' not found in geom 1
    Element name 'g1_29dof_rev_1_4_Geom_Mesh1', id 1
    ```
    原因：[mujoco 模型编译的结果为空](https://github.com/OpenHUTB/hutb/blob/5d0243d461c4e492c856b73bbc870592d6b1b96b/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLab/Private/MuJoCo/Core/MjPhysicsEngine.cpp#L219)。

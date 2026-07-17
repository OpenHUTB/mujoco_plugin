# 几何与碰撞

如何定义碰撞形状（从基本体到分解网格）并控制哪些物体发生碰撞。

---

## 几何类型

| 类型 | 部件 | 定义 |
|------|-----------|-----------|
| 盒子(Box) | `UMjBox` | 半延伸（通过 XYZ 缩放） |
| 球体(Sphere) | `UMjSphere` | 半径（通过 X 轴缩放） |
| 圆柱体(Cylinder) | `UMjCylinder` | 半径（X 轴缩放）+半高（Z 轴缩放） |
| 胶囊(Capsule) | `UMjGeom` (type=Capsule) | 半径 + 半高 |
| 网格(Mesh) | `UMjGeom` (type=Mesh) | 静态网格资产 |
| 高度场(Heightfield) | `AMjHeightfieldActor` | 虚幻景观数据 |

使用标准的虚幻引擎变换 gizmo 来调整形状大小——该插件读取组件缩放并将其映射到 MuJoCo 尺寸参数。

---

## 基本元素

快速、精确的碰撞分析。将盒子`UMjBox`、球体`UMjSphere` 或圆柱体`UMjCylinder` 添加为 `UMjBody` 的子对象。在一个实体上堆叠多个对象，可实现复合形状。


## 网格几何体

对于凸网格，请将“类型”设置为“网格”（`Type = Mesh`），并指定一个“静态网格(Static Mesh)”。MuJoCo 会在内部计算凸包。


对于**凹**网格，请使用 CoACD 分解——单击几何体上的“分解网格(Decompose Mesh)”，或在“快速转换(Quick Convert)”组件上设置“需要复杂网格(`ComplexMeshRequired`)”。

---

## 快速转换

`UMjQuickConvertComponent` 可应用于任何静态网格体参与者（一键式物理实体）。

| 属性 | 效果 |
|----------|--------|
| `Static` | 固定到位（无活动关节） |
| `ComplexMeshRequired` | 凹网格的CoACD分解 |
| `CoACDThreshold` | 分解细节（0.01–1.0，数值越低表示凸块越多） |
| `bDrivenByUnreal` | 虚幻引擎驱动位置，MuJoCo 不进行模拟 |

## 高度场地形

高度场参与者 `AMjHeightfieldActor` 将虚幻引擎的地形几何体转换为 MuJoCo 高度场，用于地形接触。启用 `bTraceComplex` 可实现地形的精确网格级采样。使用 `TraceWhitelist` 可过滤要采样的参与者（例如，仅采样地形，不采样植被）。

---

## 几何属性

| 属性 | 描述 |
|----------|-------------|
| 摩擦`Friction` | 滑动系数、扭转系数、滚动系数 |
| 密度`Density` | 质量由密度乘以体积推断得出 |
| 范围`Margin` | 接触检测范围 |
| `Solref` / `Solimp` | 求解器刚度/阻尼/阻抗 |

---

## 过滤接触

**组**（0-5）：用于在 MuJoCo 原生查看器中组织几何体可见性的整数标签。在 URLab 中，组 2 通常用于仅显示可见性的网格（contype=0，conaffinity=0），组 3 用于仅显示碰撞的网格。接触生成由 `contype` 和 `conaffinity` 位掩码控制，而非组。

**接触对** (`UMjContactPair`): 明确允许两个物体之间接触。

**接触排除** (`UMjContactExclude`): 禁止两个物体之间的接触。

**位掩码** (`Contype` / `Conaffinity`): 适用于大型场景的可扩展过滤。只有当两个几何体的类型/亲和性掩码重叠时，它们才会发生碰撞。 

---

## 调试可视化

碰撞调试可视化会绘制属于 **第 3 组** 或 **contype != 0** 且 **conaffinity != 0** 的几何体。这确保了足部接触球体（可能不属于第 3 组，但参与了接触）在调试叠加层中可见。


按 **2** 可切换可视化网格渲染。隐藏​​可视化网格时，仅绘制碰撞几何体——这有助于在不干扰视觉效果的情况下检查接触形状。

---

## 惯性覆盖

MuJoCo 会根据几何体的密度和形状推断其质量。要进行显式控制，请将 `UMjInertial` 添加到具有特定质量、质心和惯性矩阵的物体中。


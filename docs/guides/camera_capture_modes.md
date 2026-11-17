# 相机捕获模式

每个 `UMjCamera` 都有一个 `CaptureMode` 属性，用于决定渲染目标包含的内容。每个摄像机只能使用一种模式；如果需要从同一视点获取多个数据流（RGB + 深度 + 掩膜），则可以生成多个摄像机。


| 模式 | 输出 | 渲染目标格式 | 场景捕获源 |
|---|---|---|---|
| `Real` (默认) | 照片级RGB色彩模式。与视口外观匹配，并保留后期处理后的体积。 | `RTF_RGBA8_SRGB` | `SCS_FinalToneCurveHDR` |
| `Depth` | 线性场景深度（厘米），每个像素一个浮点数。 | `RTF_R32f` | `SCS_SceneDepth` |
| `SemanticSegmentation` | 每个角色类都采用统一的色调。同一蓝图的两个实例共享一种颜色；不同的蓝图使用不同的颜色。 | `RTF_RGBA8` | `SCS_FinalToneCurveHDR` + `PRM_UseShowOnlyList` |
| `InstanceSegmentation` | 每个刚体都有其独特的色调。 | `RTF_RGBA8` | `SCS_FinalToneCurveHDR` + `PRM_UseShowOnlyList` |

---

## 配置相机

在“详细信息(Details)”面板中，为 `UMjCamera` 组件设置 `CaptureMode`。对于深度，同时设置 `DepthNearCm`（默认值 10 厘米）和 `DepthFarCm`（默认值 10000 厘米）——UI 预览和原始深度值将根据此范围进行归一化。

`CaptureMode` 在 `SetStreamingEnabled(true)` 时读取。要更改正在运行的相机的模式，请切换流的开关：


```cpp
Cam->SetStreamingEnabled(false);
Cam->CaptureMode = EMjCameraMode::Depth;
Cam->SetStreamingEnabled(true);
```

或者，从模拟小部件中，重新选择铰链（这将重新绑定所有输入条目）。

---

## 共存——同一帧中的多种模式

分段模式无需交换真实网格的材质即可工作，因此 RGB 摄像机和分段摄像机可以在同一帧中同时进行流传输，互不干扰。

在底层，`UMjDebugVisualizer` 为每个分段模式维护一个引用计数的**同级网格池**。第一个开始流传输的分段摄像机触发该池的创建；同一模式下的其他摄像机共享该池；当最后一个订阅者取消订阅时，该池将被销毁。

- 同级组件会复制每个铰链视觉网格和每个快速转换的静态网格，并赋予其未光照色调的动态材质实例（Material Instance Dynamic, MID）。
- 它们的 `bVisibleInSceneCaptureOnly` 属性设置为 `true`，并且还会禁用反射捕获、天空捕获、光线追踪贡献、距离场光照和动态间接光照——这样，辅助光照通道就不会将微弱的色调泄漏到主视口中。
- 分割相机使用 `PrimitiveRenderMode = PRM_UseShowOnlyList` 仅渲染其组件池。
- 非分割 URLab 摄像机（真实`Real`、深度`Depth`）会在每个帧周期刷新其 `HiddenComponents` 列表，以确保延迟启动的分割相机不会污染正在运行的 RGB 流。

成本：当两个分割组件池都处于活动状态时（原始组件池 + 实例同级组件池 + 语义同级组件池），每个物体最多需要 3 个组件。每个视图仍然绘制 N 个图元——每个视图的绘制数量不变。组件池是惰性的，因此仅渲染 RGB 的会话成本为零。

---

## 模拟组件预览

模拟组件的相机面板会显示所选铰链上的每个 `UMjCamera`，每个组件都会实时渲染其配置的模式。无需额外设置——信息流条目会检查 `CaptureMode` 并选择正确的显示路径：

- `Real` / `SemanticSegmentation` / `InstanceSegmentation` — 渲染目标直接绑定为 Slate 画笔资源。
- `Depth` — R32f RT 不能用作 Slate 画笔。入口 CPU 会在每个帧周期将 R 通道复制到 BGRA `UTexture2D` 中，将 `depth ∈ [DepthNearCm, DepthFarCm]` 映射到灰度 `[0, 255]`，并绑定该纹理。 

深度预览路径是同步的（`ReadLinearColorPixels` 会刷新渲染命令）。这对于调试 UI 来说没问题；如果需要在全帧速率下进行无头深度捕获，请直接在蓝图或 C++ 中使用渲染目标回读，而不是使用控件预览。


---

## ZMQ 广播

`bEnableZmqBroadcast` 继续支持 `Real`、`SemanticSegmentation` 和 `InstanceSegmentation`——现有的 BGRA 工作进程会传输这三种数据。

深度（`Depth`）模式会跳过 ZMQ 广播（尚未配置浮点传输路径），并记录一次性警告。如有需要，请跟踪深度流的后续操作。

---

## 已知 v1 版本限制

- **分割着色采用光照阴影效果，而非平面着色。** 分割相机使用 `SCS_FinalToneCurveHDR`，因为 `BasicShapeMaterial` 的 `Color` 参数并未直接连接到 BaseColor G 缓冲区。因此，场景光照会调节着色。这对于视觉调试来说足够好，但对于真实分割掩码而言并非像素级精确。最简洁的解决方案是插件自带的无光照父材质——已列入开发计划。 
- **PIE 过程中模式的更改需要切换流的开启/关闭。** 渲染目标格式与模式相关（`RTF_RGBA8` 与 `RTF_R32f`），并且不支持实时重新配置。
- **运行时生成铰链。** 兄弟池基于第一个分段订阅者构建。在分割相机已开始流传输*后*生成的铰链或快速转换属性，在兄弟池重建之前不会出现在其输出中（切换该分割相机的流传输状态即可强制重建）。
- **第三方 `USceneCaptureComponent2D`.** 用户在 ULab 管理之外创建的场景捕获不会自动隐藏兄弟组件——它们会将其视为普通图元（因为兄弟组件的 `bVisibleInSceneCaptureOnly = true`，根据定义，它们*对*场景捕获可见）。如果这造成问题，请手动将兄弟池添加到该组件的 `HiddenComponents` 中。

---

## 实现参考

- 模式枚举 + 每个摄像机的状态 — [MjCameraTypes.h](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Source/URLab/Public/MuJoCo/Components/Sensors/MjCameraTypes.h), [MjCamera.h](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Source/URLab/Public/MuJoCo/Components/Sensors/MjCamera.h)
- 每个模式的渲染目标 + 场景捕获设置 — [MjCamera.cpp::SetupRenderTarget](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Source/URLab/Private/MuJoCo/Components/Sensors/MjCamera.cpp)
- 池生命周期 — [MjDebugVisualizer.cpp::AcquireSegPool / BuildSegPool / DestroySegPool](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Source/URLab/Private/MuJoCo/Core/MjDebugVisualizer.cpp)
- 深度预览 — [MjCameraFeedEntry.cpp::UpdateDepthPreview](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Source/URLab/Private/UI/MjCameraFeedEntry.cpp)
- 自动化测试覆盖率 — `URLab.Camera.*` in [MjCameraTests.cpp](https://github.com/OpenHUTB/UnrealRoboticsLab/blob/main/Source/URLabEditor/Private/Tests/MjCameraTests.cpp)

# make package 问题与解决方案

## 问题一：Editor-only 模块链接到 Shipping 构建

**错误信息：**
```
ERROR: Non-editor build cannot depend on non-redistributable modules.
CarlaUE4-Linux-Shipping depends on 'DirectoryWatcher', 'SlateFileDialogs', 'DesktopPlatform'.
Dependant modules 'SlateFileDialogs', 'DesktopPlatform', 'URLab'
```

**根因：**
`URLab.Build.cs` 的 `PrivateDependencyModuleNames` 中无条件依赖了 `DesktopPlatform`。该模块是 Editor-only（non-redistributable），Shipping 构建不能链接。

`SlateFileDialogs` 和 `DirectoryWatcher` 是 `DesktopPlatform` 的传递依赖，随之一同被拉入。

**解决方案：**

1. `URLab.Build.cs` — 将 `DesktopPlatform` 移入 `if (Target.bBuildEditor)` 条件块：
```csharp
// 修改前
PrivateDependencyModuleNames.AddRange(new string[]
{
    ...
    "DesktopPlatform"   // ← 无条件依赖, Shipping 构建报错
});
+
// 修改后
if (Target.bBuildEditor)
{
    PrivateDependencyModuleNames.Add("DesktopPlatform");
}
```

2. `MjReplayManager.cpp` — `BrowseAndLoadCSV` 和 `BrowseAndSaveRecording` 两个函数中使用了 `IDesktopPlatform` / `FDesktopPlatformModule`，需要用 `#if WITH_EDITOR` 包裹：

```cpp
// 修改前
#include "DesktopPlatformModule.h"                              // 无条件 include

bool AMjReplayManager::BrowseAndLoadCSV(float Timestep)
{
    IDesktopPlatform* DesktopPlatform = FDesktopPlatformModule::Get();  // Shipping 中不可用
    ...
}

// 修改后
#if WITH_EDITOR
#include "DesktopPlatformModule.h"
#endif

bool AMjReplayManager::BrowseAndLoadCSV(float Timestep)
{
    FString DefaultDir = ...;
    TArray<FString> OutFiles;          // ← 声明移到 #if 外面

#if WITH_EDITOR
    {
        IDesktopPlatform* DesktopPlatform = FDesktopPlatformModule::Get();
        ... // 文件对话框
    }
#else
    return false;                      // Shipping 中无 UI 对话框, 直接返回
#endif

    // 后续文件处理代码（Editor 中可达）
    ...
}

// BrowseAndSaveRecording 同样处理
```

**涉及文件：**
- `Source/URLab/URLab.Build.cs`
- `Source/URLab/Private/Replay/MjReplayManager.cpp`

---

## 问题二：硬编码 Windows DLL 名称

**错误信息：**
```
LogURLab: Error: mujoco.dll not found (searched plugin dir + binary dir)
LogURLab: Error: libzmq-v143-mt-4_3_6.dll not found (searched plugin dir + binary dir)
```

**根因：**
`URLab.cpp` 和 `MjPhysicsEngine.cpp` 中硬编码了 Windows 的 DLL 文件名。Linux 上的动态库名称和路径均不同：

| | Windows | Linux |
|---|---|---|
| MuJoCo | `bin/mujoco.dll` | `lib/libmujoco.so` |
| ZMQ | `bin/libzmq-v143-mt-4_3_6.dll` | `lib/libzmq.so` |
| CoACD | `bin/lib_coacd.dll` | 无（头文件 only） |
| 搜索路径 | `bin/` | `lib/` |

**解决方案：**

1. `URLab.cpp` — `LoadDependencyDLL` lambda 中搜索路径加平台判断：
```cpp
#if PLATFORM_WINDOWS
    FString DLLPath = FPaths::Combine(InstallDir, SubDir, TEXT("bin"), LibraryName);
#else
    FString DLLPath = FPaths::Combine(InstallDir, SubDir, TEXT("lib"), LibraryName);
#endif
```

2. `URLab.cpp` — 库名加平台判断：
```cpp
// MuJoCo
#if PLATFORM_WINDOWS
    LoadDependencyDLL(TEXT("mujoco.dll"), TEXT("MuJoCo"));
#else
    LoadDependencyDLL(TEXT("libmujoco.so"), TEXT("MuJoCo"));
#endif

// ZMQ
#if PLATFORM_WINDOWS
    LoadDependencyDLL(TEXT("libzmq-v143-mt-4_3_6.dll"), TEXT("libzmq"));
#else
    LoadDependencyDLL(TEXT("libzmq.so"), TEXT("libzmq"));
#endif

// CoACD — Windows only, header-only on Linux
#if PLATFORM_WINDOWS
    LoadDependencyDLL(TEXT("lib_coacd.dll"), TEXT("CoACD"));
#endif
```

3. `MjPhysicsEngine.cpp` — 同样加平台判断：
```cpp
#if PLATFORM_WINDOWS
    void* Handle = FPlatformProcess::GetDllHandle(TEXT("mujoco.dll"));
#else
    void* Handle = FPlatformProcess::GetDllHandle(TEXT("libmujoco.so"));
#endif
```

**涉及文件：**
- `Source/URLab/Private/URLab.cpp`
- `Source/URLab/Private/MuJoCo/Core/MjPhysicsEngine.cpp`

---

## 问题三：软链接导致 Staging 复制失败

**错误信息：**
```
Size mismatch libmujoco.so = 18 to libmujoco.so = 5323176
Failed to copy libmujoco.so
ERROR: Failed to copy libmujoco.so
```

**根因：**
MuJoCo 和 ZMQ 预编译包中的 `.so` 文件是软链接：

```
libmujoco.so -> libmujoco.so.3.7.0   (18 字节)
libzmq.so    -> libzmq.so.5.2.2      (15 字节)
```

UE4 的 Staging（部署）阶段复制文件时不跟随软链接。第一次复制 `libmujoco.so`（18 字节），第二次检查目标位置时发现同名文件实际是已解析的 5MB 真实文件，大小对不上，报错重试直到失败。

**解决方案：**
将软链接替换为实体文件：

```bash
# MuJoCo
MUJOCO_LIB="third_party/install/MuJoCo/lib"
rm "$MUJOCO_LIB/libmujoco.so"
cp "$MUJOCO_LIB/libmujoco.so.3.7.0" "$MUJOCO_LIB/libmujoco.so"

# ZMQ
ZMQ_LIB="third_party/install/libzmq/lib"
rm "$ZMQ_LIB/libzmq.so"
cp "$ZMQ_LIB/libzmq.so.5.2.2" "$ZMQ_LIB/libzmq.so"
```

CI 工作流中也加入对应步骤（检测软链接后自动替换）：

```yaml
# MuJoCo
MUJOCO_LIB=Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/third_party/install/MuJoCo/lib
if [ -L "$MUJOCO_LIB/libmujoco.so" ]; then
  REAL=$(readlink -f "$MUJOCO_LIB/libmujoco.so")
  rm "$MUJOCO_LIB/libmujoco.so" && cp "$REAL" "$MUJOCO_LIB/libmujoco.so"
fi

# ZMQ — 同理
```

**涉及文件：**
- `third_party/install/MuJoCo/lib/libmujoco.so`（本地）
- `third_party/install/libzmq/lib/libzmq.so`（本地）
- `.github/workflows/build_linux.yml`（CI 同步）

---

---

## 问题四：Cook 阶段 SetupAttachment ensure 崩溃

**错误信息：**
```
LogOutputDevice: Error: Ensure condition failed: AttachParent == nullptr || !AttachParent->AttachChildren.Contains(this)
[File:SceneComponent.cpp] [Line: 1756]
LogOutputDevice: Error: SetupAttachment cannot be used once a component has already had AttachTo used to connect it to a parent.
LogOutputDevice: Error: [Callstack] UMjCylinder::OnRegister() [MjCylinder.cpp:65]
-> SaveCookedPackage -> CookCommandlet
```

**最终结果：**
```
Failure - 26 error(s), 4159 warning(s)
UE4Editor ExitCode=1
AutomationTool exiting with ExitCode=25 (Error_UnknownCookFailure)
```

**根因：**
UE4.26 中 `SetupAttachment` 和 `AttachTo` 不能混用。当组件通过 `AttachTo` 连接过父组件后，其内部 `AttachParent` 仍保留非空引用，但父组件的 `AttachChildren` 数组可能已经不同步（尤其在 Cook 序列化/反序列化过程中）。此时再次调用 `SetupAttachment` 触发 `ensure` 失败。

四个 MuJoCo Primitive 组件的 `EnsureVisualizerMesh()` 和 `OnRegister()` 中均有未受保护的 `SetupAttachment` 调用：

| 文件 | Visualizer 子组件 |
|---|---|
| `MjCylinder.cpp` | 1 个 (VisualizerMesh) |
| `MjBox.cpp` | 1 个 (VisualizerMesh) |
| `MjSphere.cpp` | 1 个 (VisualizerMesh) |
| `MjCapsule.cpp` | 3 个 (VisualizerShaft, VisualizerCapTop, VisualizerCapBottom) |

**解决方案：**

在每次 `SetupAttachment` 调用前，先检查 `GetAttachParent()` 是否为非空。如果非空，先用 `DetachFromComponent` 清除旧的附加状态：

```cpp
// 修改前
VisualizerMesh->SetupAttachment(this);
VisualizerMesh->RegisterComponent();

// 修改后
if (VisualizerMesh->GetAttachParent() != nullptr)
{
    VisualizerMesh->DetachFromComponent(FDetachmentTransformRules::KeepRelativeTransform);
}
VisualizerMesh->SetupAttachment(this);
VisualizerMesh->RegisterComponent();
```

每个文件分别在 `EnsureVisualizerMesh()` 和 `OnRegister()` 两处添加此保护。

`MjCapsule.cpp` 中通过 lambda `MakeSubMesh` 和 `RegisterIfNeeded` 调用，同样添加保护。

**涉及文件：**
- `Source/URLab/Private/MuJoCo/Components/Geometry/Primitives/MjCylinder.cpp`
- `Source/URLab/Private/MuJoCo/Components/Geometry/Primitives/MjBox.cpp`
- `Source/URLab/Private/MuJoCo/Components/Geometry/Primitives/MjSphere.cpp`
- `Source/URLab/Private/MuJoCo/Components/Geometry/Primitives/MjCapsule.cpp`

---

## 修改文件清单

| # | 文件 | 改动 | 对应问题 |
|---|---|---|---|
| 1 | `URLab.Build.cs` | `DesktopPlatform` 移入 `bBuildEditor` 条件 | 一 |
| 2 | `MjReplayManager.cpp` | include + 两个函数加 `#if WITH_EDITOR` | 一 |
| 3 | `URLab.cpp` | `LoadDependencyDLL` 路径 + 库名加平台判断 | 二 |
| 4 | `MjPhysicsEngine.cpp` | `GetDllHandle` 库名加平台判断 | 二 |
| 5 | `MuJoCo/lib/libmujoco.so` | 软链接 → 实体文件 | 三 |
| 6 | `libzmq/lib/libzmq.so` | 软链接 → 实体文件 | 三 |
| 7 | `build_linux.yml` | CI 中加入软链接替换步骤 | 三 |
| 8 | `MjCylinder.cpp` | `EnsureVisualizerMesh()` + `OnRegister()` 中 SetupAttachment 前加 Detach 保护 | 四 |
| 9 | `MjBox.cpp` | 同上 | 四 |
| 10 | `MjSphere.cpp` | 同上 | 四 |
| 11 | `MjCapsule.cpp` | 同上（含 MakeSubMesh + RegisterIfNeeded 两处 lambda） | 四 |

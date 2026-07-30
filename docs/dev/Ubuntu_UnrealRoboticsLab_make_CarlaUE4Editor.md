# CarlaUE4 Linux 编译问题与解决方案

## 一、MuJoCo 版本不匹配

### 问题 1.1：大量 MuJoCo API 未声明

**错误信息：**
- `use of undeclared identifier 'mjGAIN_DCMOTOR'`
- `use of undeclared identifier 'mjBIAS_DCMOTOR'`
- `use of undeclared identifier 'mjDYN_DCMOTOR'`
- `use of undeclared identifier 'mjNPOLY'`
- `no member named 'sleep_tolerance' in 'mjOption_'`
- `no member named 'body_awake' in 'mjData_'`
- `no member named 'tree_sleep_policy' in 'mjModel_'`

**根因：**
CI 流水线安装的 MuJoCo 3.3.5 太旧。上述 API 在 MuJoCo 3.4.0 ~ 3.7.0 之间才逐步引入：
- `mjNPOLY`、`mjGAIN_DCMOTOR`、`mjBIAS_DCMOTOR`、`mjDYN_DCMOTOR` → 3.7.0
- `sleep_tolerance`、`body_awake`、`tree_sleep_policy` → 3.4.0

**解决方案：**
从 MuJoCo GitHub Releases 下载 **3.7.0** Linux 预编译包，替换 `third_party/install/MuJoCo/`。

```bash
# 下载
curl -L -o mujoco-3.7.0-linux-x86_64.tar.gz \
  "https://github.com/google-deepmind/mujoco/releases/download/3.7.0/mujoco-3.7.0-linux-x86_64.tar.gz"

# 安装
tar -xzf mujoco-3.7.0-linux-x86_64.tar.gz \
  -C Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/third_party/install/MuJoCo \
  --strip-components=1

# 同时保存到 CI 依赖目录
cp mujoco-3.7.0-linux-x86_64.tar.gz Build/dependencies/Plugins/
```

**涉及文件：**
- `Build/dependencies/Plugins/mujoco-3.7.0-linux-x86_64.tar.gz`（新增）
- `.github/workflows/build_linux.yml`（更新版本号）

---

## 二、C++ 标准版本

### 问题 2.1：`std::byte` 不存在

**错误信息：**
```
error: no member named 'byte' in namespace 'std'
error: unknown type name 'mjByteVec'; did you mean 'mjIntVec'?
```

**根因：**
`std::byte` 是 C++17 特性。MuJoCo 3.x 的 `mjspec.h` 使用 `std::byte` 定义 `mjByteVec`，但 UE4.26 默认使用 C++14 标准编译。

在 `URLab.Build.cs` 中设置 `CppStandard = CppStandardVersion.Cpp17` 理论上可行，但 UBT 缓存和模块级设置的传播路径不够稳定。

**解决方案：**
在 MuJoCo 的 `mjspec.h` 中添加 C++14 兼容层（polyfill）：

```cpp
// 在 #include <vector> 之后、extern "C" { 之前插入：

// C++14 compatibility: std::byte was introduced in C++17.
// UE 4.26 defaults to C++14. Provide a polyfill so MuJoCo compiles.
#if __cplusplus < 201703L
namespace std {
  enum class byte : unsigned char {};
}
#endif
```

同时在 `URLab.Build.cs` 中保留 `CppStandard = CppStandardVersion.Cpp17` 作为兜底。

**涉及文件：**
- `third_party/install/MuJoCo/include/mujoco/mjspec.h`（polyfill）
- `Source/URLab/URLab.Build.cs`（CppStandard 设置）

---

## 三、平台宏污染

### 问题 3.1：Linux 编译时 `__declspec` 报错

**错误信息：**
```
error: '__declspec' attributes are not enabled;
use '-fdeclspec' or '-fms-extensions' to enable support for __declspec attributes
```

**根因：**
`URLab.Build.cs` 中 Linux 分支有 `PublicDefinitions.Add("_WIN32=0")`。C 预处理器的 `#if defined _WIN32` 只检查宏是否**存在**，不看值。`#define _WIN32 0` 让 `defined _WIN32` 返回 `true`，导致 MuJoCo 的 `mjexport.h` 在 Linux 上走入了 Windows 的 `__declspec(dllimport)` 分支。

```c
// mjexport.h 的判断逻辑
#if defined _WIN32 || defined __CYGWIN__
  #define MUJOCO_HELPER_DLL_IMPORT __declspec(dllimport)  // ← Linux 上被命中
#else
  #define MUJOCO_HELPER_DLL_IMPORT __attribute__ ((visibility ("default")))
#endif
```

**解决方案：**
从 `URLab.Build.cs` 的 Linux 分支中删除 `_WIN32=0` 和 `USE_DECLSPEC=1`。

```csharp
// 修改前
if (Target.Platform == UnrealTargetPlatform.Linux)
{
    PublicDefinitions.Add("_WIN32=0");        // ← 删除
    PublicDefinitions.Add("USE_DECLSPEC=1");   // ← 删除
    PublicDefinitions.Add("__linux__=1");
    PublicDefinitions.Add("__unix__=1");
}

// 修改后
if (Target.Platform == UnrealTargetPlatform.Linux)
{
    CppStandard = CppStandardVersion.Cpp17;
    PublicDefinitions.Add("__linux__=1");
    PublicDefinitions.Add("__unix__=1");
}
```

**涉及文件：**
- `Source/URLab/URLab.Build.cs`

---

### 问题 3.2：`URLab.h` 无条件定义 `_WIN32`

**根因：**
`URLab.h` 中有如下代码：

```cpp
#ifndef _WIN32
    #define _WIN32 PLATFORM_WINDOWS  // Linux 上 PLATFORM_WINDOWS = 0
#endif
```

这导致即使 Build.cs 不再定义 `_WIN32`，URLab.h 仍然在 Linux 上定义它，同样会触发 MuJoCo 的 `__declspec` 路径。

**解决方案：**
改为仅在 Windows 平台定义：

```cpp
// 修改前
#ifndef _WIN32
    #define _WIN32 PLATFORM_WINDOWS
#endif

// 修改后
// Only define _WIN32 on actual Windows builds, not on Linux
// (PLATFORM_WINDOWS is 0 on Linux, but #define _WIN32 0 still makes
//  `defined _WIN32` true, causing MuJoCo's mjexport.h to use __declspec)
#if PLATFORM_WINDOWS
    #ifndef _WIN32
        #define _WIN32 1
    #endif
#endif
```

**涉及文件：**
- `Source/URLab/Public/URLab.h`

---

### 问题 3.3：CoACD 第三方库 `#if _WIN32` 触发 `-Wundef`

**错误信息：**
```
error: '_WIN32' is not defined, evaluates to 0 [-Werror,-Wundef]
```

**根因：**
经过上述修复后，Linux 上 `_WIN32` 不再被定义。但 CoACD 的 `coacd.h` 中有 `#if _WIN32`（未定义的宏在 `#if` 中求值为 0），这在 `-Wundef` + `-Werror` 下报错。

**解决方案：**
在 `URLab.Build.cs` 中禁用未定义标识符警告：

```csharp
bEnableUndefinedIdentifierWarnings = false;
```

**涉及文件：**
- `Source/URLab/URLab.Build.cs`

---

## 四、FbxMeshImportData 枚举冲突

### 问题 4.1：前向声明与 UE4.26 定义冲突

**错误信息：**
```
error: enumeration previously declared with fixed underlying type
note: previous declaration is here
```

**详细：**
```
FbxMeshImportData.h:22:7: error: enumeration previously declared with fixed underlying type
        enum Type
             ^
MujocoGenerationAction.h:34:45: note: previous declaration is here
namespace EFBXNormalGenerationMethod { enum Type : int; }
                                            ^
```

**根因：**
`MujocoGenerationAction.h` 中有一个前向声明：

```cpp
namespace EFBXNormalGenerationMethod { enum Type : int; }
```

但 UE4.26 的 `FbxMeshImportData.h` 实际定义是：

```cpp
namespace EFBXNormalGenerationMethod {
    enum Type {           // ← 没有 : int
        BuiltIn,
        MikkTSpace,
    };
}
```

C++ 标准不允许前向声明带固定底层类型而定义不带（或反过来）。

**解决尝试：**

| 尝试 | 方案 | 结果 |
|---|---|---|
| 1 | 去掉 `: int` → `enum Type;` | C++14 不允许无固定底层类型的枚举前向声明 |
| 2 | 保留 `: int` → 给定义也加 `: int` | 不能改引擎文件 |

**最终解决方案：**
删除前向声明，直接 `#include` 完整定义的头文件：

```cpp
// 修改前
// Forward declarations
namespace EFBXNormalGenerationMethod { enum Type : int; }

// 修改后
// Forward declarations
#include "Factories/FbxMeshImportData.h"
```

**涉及文件：**
- `Source/URLabEditor/Public/MujocoGenerationAction.h`

---

## 五、其他编译错误

### 问题 5.1：`/*` 嵌套在块注释中

**错误信息：**
```
error: '/*' within block comment [-Werror,-Wcomment]
```

**根因：**
`MjCamera.h:140` 的 Doxygen 块注释中包含 `tcp://*:5558`，其中 `//*` 被解析为嵌套的 `/*`，触发了 `-Wcomment` 警告（`-Werror` 使其成为错误）。

```cpp
/** @brief The ZMQ Endpoint for this specific camera (e.g., tcp://*:5558). */
//                                                   ^ 这里的 //* 被看作 /*
```

**解决方案：**
将 `/** */` 块注释改为 `///` 行注释：

```cpp
/// @brief The ZMQ Endpoint for this specific camera (e.g., tcp://*:5558).
```

**涉及文件：**
- `Source/URLab/Public/MuJoCo/Components/Sensors/MjCamera.h`

---

### 问题 5.2：`EFBXNormalGenerationMethod::MikkTSpace` 找不到

**错误信息：**
```
error: no member named 'MikkTSpace' in namespace 'EFBXNormalGenerationMethod'
error: no member named 'BuiltIn' in namespace 'EFBXNormalGenerationMethod'
```

**根因：**
枚举冲突（见问题 4.1）导致编译器无法正确解析 `EFBXNormalGenerationMethod` 命名空间中的成员。

**解决方案：**
用 `static_cast` 替代命名空间枚举成员访问：

```cpp
// 修改前
UStaticMesh* ImportedMesh = AttemptMeshImport(ActualSourcePath, DestinationPath,
    EFBXNormalGenerationMethod::MikkTSpace);
ImportedMesh = AttemptMeshImport(ActualSourcePath, DestinationPath,
    EFBXNormalGenerationMethod::BuiltIn);

// 修改后
// UE4.26 workaround: avoid EFBXNormalGenerationMethod::MikkTSpace/BuiltIn
// due to UHT forward-declaration conflict
UStaticMesh* ImportedMesh = AttemptMeshImport(ActualSourcePath, DestinationPath,
    static_cast<EFBXNormalGenerationMethod::Type>(1)); // MikkTSpace
ImportedMesh = AttemptMeshImport(ActualSourcePath, DestinationPath,
    static_cast<EFBXNormalGenerationMethod::Type>(0)); // BuiltIn
```

**涉及文件：**
- `Source/URLabEditor/Private/MujocoMeshImporter.cpp`

---

### 问题 5.3：`FFileHelper` 未声明

**错误信息：**
```
error: use of undeclared identifier 'FFileHelper'
```

**根因：**
`MujocoMeshImporter.cpp` 使用了 `FFileHelper::LoadFileToArray` 但没有 include 其头文件。

**解决方案：**
添加 `#include "Misc/FileHelper.h"`。

```cpp
#include "MujocoGenerationAction.h"
#include "Misc/FileHelper.h"       // ← 新增
#include "URLabEditorLogging.h"
```

**涉及文件：**
- `Source/URLabEditor/Private/MujocoMeshImporter.cpp`

---

### 问题 5.4：变量未初始化

**错误信息：**
```
error: variable 'NumUVChannels' is uninitialized when used here [-Werror,-Wuninitialized]
```

**根因：**
`NumVertices`、`NumTriangles`、`NumUVChannels` 三个变量声明时未初始化，赋值代码被注释掉。

**解决方案：**
声明时给初始值 0：

```cpp
int32 NumVertices = 0;
int32 NumTriangles = 0;
int32 NumUVChannels = 0;
```

**涉及文件：**
- `Source/URLabEditor/Private/MujocoMeshImporter.cpp`

---

## 六、第三方库

### 问题 6.1：CoACD 头文件找不到

**错误信息：**
```
fatal error: 'Coacd/coacd.h' file not found
```

**根因：**
CoACD.zip 解压后的目录结构为 `CoACD/CoACD/include/CoACD/coacd.h`（嵌套了一层），而 `URLab.Build.cs` 的 `AddThirdPartyLibrary` 函数添加的 include 路径是 `CoACD/include/`，导致 `coacd.h` 不在搜索路径中。

**解决方案：**

1. 将嵌套的 include 目录移出来：
```bash
mv CoACD/CoACD/include CoACD/include
```

2. 目录名 `CoACD`（大写）和代码中的 `#include "Coacd/coacd.h"`（小写 `d`）不匹配。Linux 文件系统区分大小写，需要统一：
```bash
mv CoACD/include/CoACD CoACD/include/Coacd
```

3. CI 工作流同步修复：
```yaml
# .github/workflows/build_linux.yml
unzip -qo Build/dependencies/Plugins/CoACD.zip \
  -d Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/third_party/install/CoACD

# 新增：修复目录嵌套
if [ -d .../CoACD/CoACD/include ] && [ ! -d .../CoACD/include ]; then
  mv .../CoACD/CoACD/include .../CoACD/include
  mv .../CoACD/include/CoACD .../CoACD/include/Coacd
fi
```

**涉及文件：**
- `third_party/install/CoACD/include/`（目录结构调整）
- `.github/workflows/build_linux.yml`（CI 同步）

---

### 问题 6.2：ZMQ 头文件找不到

**错误信息：**
```
fatal error: 'zmq.h' file not found
```

**根因：**
CI 提供的 `libzmq-linux.tar.gz` 预编译包只包含 `.so` 动态库，`include/` 目录为空，没有 `zmq.h`。

**解决方案：**
系统已安装 `libzmq3-dev`（`/usr/include/zmq.h`），创建软链接：

```bash
ln -sf /usr/include/zmq.h \
  third_party/install/libzmq/include/zmq.h
```

**涉及文件：**
- `third_party/install/libzmq/include/zmq.h`（软链接）

---

## 修改文件清单

| # | 文件 | 改动类型 | 解决问题 |
|---|---|---|---|
| 1 | `third_party/install/MuJoCo/` | 替换为 3.7.0 | 1.1 API 缺失 |
| 2 | `mjspec.h` | 添加 C++14 polyfill | 2.1 `std::byte` |
| 3 | `URLab.Build.cs` | 删 `_WIN32=0`、加 Cpp17、禁用 `-Wundef` | 3.1 `__declspec`、2.1、3.3 |
| 4 | `URLab.h` | `_WIN32` 仅 Windows 定义 | 3.2 宏污染 |
| 5 | `MujocoGenerationAction.h` | 前向声明 → include 头文件 | 4.1 枚举冲突 |
| 6 | `MujocoMeshImporter.cpp` | 枚举 cast + include + 初始化 | 5.2、5.3、5.4 |
| 7 | `MjCamera.h` | `/**` → `///` | 5.1 嵌套注释 |
| 8 | `CoACD/include/` | 目录结构调整 | 6.1 CoACD |
| 9 | `libzmq/include/` | 软链接 zmq.h | 6.2 ZMQ |
| 10 | `build_linux.yml` | MuJoCo 版本 + CoACD 修复 | CI 同步 |

---

## 编译前必须执行的步骤

每次修改 Build.cs、头文件或第三方库后，UBT 缓存可能导致旧配置被使用。编译前务必清理缓存：

```bash
cd /path/to/hutb

# 清理 UBT 缓存
rm -rf /home/ubuntu/UnrealEngine_4.26/Engine/Intermediate/Build/Linux/B4D820EA

# 清理项目中间文件
rm -rf Unreal/CarlaUE4/Intermediate

# 编译
source ./setEnv64.sh
make CarlaUE4Editor ARGS="--chrono"
```

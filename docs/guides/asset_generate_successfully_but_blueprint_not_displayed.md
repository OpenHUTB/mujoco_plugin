# 资产生成成功但蓝图没显示（UE4.26）

> 本文记录 MuJoCo 插件在 **UE4.26 + CarlaUE4（hutb 工程）** 中遇到的一个“假失败”：
> 网格实际上已经导入成功并保存成了 `.uasset`，但插件报告 **0 个对象**，最后判定 `Failed to import mesh ... - all import methods failed`，蓝图里没有任何网格。
>
> 路径约定：项目路径相对 `hutb` 仓库根目录；引擎路径相对 `UnrealEngine_4.26` 引擎根目录。

---

## 1. 现象

拖入 XML、`clean_meshes.py` 生成 `.glb` 之后，日志里明明能看到 GLTF 工厂在构建网格、保存资产：

```text
LogFactory: FactoryCreateFile: StaticMesh with GLTFImportFactory (.../pelvis.glb)
LogStaticMesh: 正在构建静态网格体0_pelvis_STL……
LogStaticMesh: Built static mesh [0.07s] /Game/MuJoCoImports/g1_ue_Assets/Meshes/pelvis/0_pelvis_STL.0_pelvis_STL
LogSavePackage: Moving '.../0_pelvis_STL....tmp' to '.../0_pelvis_STL.uasset'
```

但紧接着插件打印的是：

```text
[ImportSingleMesh] Import returned 0 objects:
```

然后路径猜测全部失败，最终：

```text
Failed to import mesh 'pelvis' - all import methods failed
```

蓝图因此没有 `Viz_*` 组件，视口空白。

---

## 2. 错误日志（失败运行）

关键片段（从第 47874 行开始）：

```text
LogURLabEditor: Importing mesh from: .../unitree_g1/assets/pelvis.STL to /Game/MuJoCoImports/g1_ue_Assets/Meshes
LogURLabEditor: Found higher priority mesh file: .../unitree_g1/assets/pelvis.glb
LogFactory: FactoryCreateFile: StaticMesh with GLTFImportFactory (.../pelvis.glb)
LogStaticMesh: 正在构建静态网格体0_pelvis_STL……
LogStaticMesh: Built static mesh [0.07s] /Game/MuJoCoImports/g1_ue_Assets/Meshes/pelvis/0_pelvis_STL.0_pelvis_STL
LoadErrors: Warning: Mesh has primitives with no materials assigned: 0_pelvis.STL
LogSavePackage: Moving '.../0_pelvis_STL....tmp' to '.../Content/MuJoCoImports/g1_ue_Assets/Meshes/pelvis/0_pelvis_STL.uasset'
LogURLabEditor: [ImportSingleMesh] Import returned 0 objects:
LogURLabEditor: [ImportSingleMesh] Not found at: /Game/MuJoCoImports/g1_ue_Assets/Meshes/pelvis/StaticMeshes/pelvis.pelvis
LogURLabEditor: [ImportSingleMesh] Not found at: /Game/MuJoCoImports/g1_ue_Assets/Meshes/pelvis/StaticMeshes/pelvis
LogURLabEditor: [ImportSingleMesh] Not found at: /Game/MuJoCoImports/g1_ue_Assets/Meshes/pelvis.pelvis
LogURLabEditor: [ImportSingleMesh] Searching asset registry under: /Game/MuJoCoImports/g1_ue_Assets/Meshes/pelvis
LogURLabEditor: Warning: Failed to import mesh 'pelvis' with MikkTSpace, attempting fallback
```

这次运行（同一日志文件）的统计：

```text
[ImportSingleMesh] Import returned 0 objects:   118 次
Successfully imported mesh                       0 次
```

---

## 3. 根因：UE4.26 只填 `ImportedObjectPaths`，不填 `Result`

### 3.1 `UAssetImportTask` 有两个结果字段

`Engine/Source/Editor/UnrealEd/Public/AssetImportTask.h:62-68`

```cpp
/** Paths to objects created or updated after import */
UPROPERTY(BlueprintReadWrite, Category = "Asset Import Task")
TArray<FString> ImportedObjectPaths;

/** Imported objects */
UPROPERTY(BlueprintReadWrite, Category = "Asset Import Task")
TArray<UObject*> Result;
```

### 3.2 UE4.26 的 `ImportAssetTasks` 只写 `ImportedObjectPaths`

`Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:1173-1180`

```cpp
for (UObject* Object : ImportedObjects)
{
    ImportTask->ImportedObjectPaths.Add(Object->GetPathName());   // ← 只写路径
    if (ImportTask->bSave)
    {
        PackagesToSave.AddUnique(Object->GetOutermost());
    }
}
```

整个 UE4.26 的 `ImportAssetTasks` 里没有任何 `ImportTask->Result.Add(...)`。`Result` 的填充是 UE5（Interchange 导入流程）才有的行为。

### 3.3 插件当时只读了 `Result`

修复前，插件在导入返回后只做了：

```cpp
TArray<UObject*> ImportedAssets;
for (UObject* Obj : ImportTask->Result)   // UE4.26 里这个数组恒为空
{
    if (Obj) ImportedAssets.Add(Obj);
}
```

所以无论工厂导入得多成功，`ImportedAssets` 永远是空的：

```text
[ImportSingleMesh] Import returned 0 objects:
```

### 3.4 为什么后面的兜底也找不到

`ImportSingleMesh` 在直接结果为空后，会按固定路径猜测：

```text
<目标>/<网格名>/StaticMeshes/<网格名>.<网格名>
<目标>/<网格名>/StaticMeshes/<网格名>
<目标>/<网格名>.<网格名>
```

而 GLTF 工厂实际生成的资产是：

```text
/Game/MuJoCoImports/g1_ue_Assets/Meshes/pelvis/0_pelvis_STL.0_pelvis_STL
```

两者对不上，所以三条猜测全部 `Not found`。

最后的资产注册表兜底也没命中（`Found mesh via registry` 为 0），因为资产是刚刚创建的，注册表缓存尚未更新。

### 3.5 网格其实已经导入成功了

日志里的这两行就是证据：

- `LogStaticMesh: Built static mesh ...` —— StaticMesh 已经构建；
- `LogSavePackage: Moving ... 0_pelvis_STL.uasset` —— 资产已经落盘。

所以问题不在“导入失败”，而在“**导入成功了，但插件没读到结果**”。

---

## 4. 修复

位置：`Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoMeshImporter.cpp:217-233`

```cpp
// 获取结果。
// 注意：UE4.26 的 UAssetToolsImpl::ImportAssetTasks() 只填充 ImportedObjectPaths，
// 不填充 Result（UE5 才会填充 Result），因此两个都要读取。
TArray<UObject*> ImportedAssets;
for (UObject* Obj : ImportTask->Result)        
{
    if (Obj) ImportedAssets.Add(Obj);
}

for (const FString& ObjectPath : ImportTask->ImportedObjectPaths)   // UE4.26
{
    if (UObject* ImportedObject = LoadObject<UObject>(nullptr, *ObjectPath))
    {
        ImportedAssets.AddUnique(ImportedObject);
    }
}
```

说明：

- `ImportedObjectPaths` 里存的是 `Object->GetPathName()`，用 `LoadObject` 就能取回对象；对象通常已经在内存里，基本没有磁盘开销；

---

## 5. 修复后的日志

成功样例：

```text
LogURLabEditor: [ImportSingleMesh] Import returned 1 objects:
LogURLabEditor:   [0] 0_pelvis_STL (StaticMesh) at /Game/MuJoCoImports/g1_ue_Assets/Meshes/pelvis/0_pelvis_STL.0_pelvis_STL
LogSavePackage: Moving '.../0_pelvis_STL....tmp' to '.../0_pelvis_STL.uasset'
LogURLabEditor: Imported mesh 'pelvis' - Bounds: X=9.750 Y=12.890 Z=14.995
LogURLabEditor: Successfully imported mesh 'pelvis' with MikkTSpace
```

统计：

```text
[ImportSingleMesh] Import returned 1 objects:   87 次
[ImportSingleMesh] Import returned 0 objects:    0 次
Successfully imported mesh                      87 次
Failed to import mesh                            0 次
```

---

## 6. 和“导入被取消”的区别

同样是 `Import returned 0 objects`，但原因完全不同，修复方式也不同：

| 现象                         | 日志特征                                                                                                    | 根因                                                     | 修复                                           |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------- |
| 工厂内部把导入取消           | `A modal window tried to take control...` + `The import task was canceled.`                             | GLTF 工厂在自动化模式下调用了模态窗口，窗口被 Slate 取消 | 引擎补丁 `if (!IsAutomatedImport())`         |
| 工厂导入成功但插件读不到结果 | `LogStaticMesh: Built static mesh ...` + `LogSavePackage: Moving ...`，但 `Import returned 0 objects` | 插件只读 `Result`，UE4.26 只填 `ImportedObjectPaths` | 读取 `ImportedObjectPaths` 并 `LoadObject` |

判断方法：

```bash
grep -c "The import task was canceled" Saved/Logs/CarlaUE4.log
grep -c "Built static mesh"            Saved/Logs/CarlaUE4.log
grep -c "Import returned 0 objects"    Saved/Logs/CarlaUE4.log
```

- 第一项 > 0：是“弹窗取消”问题；
- 第一项为 0、第二项 > 0、第三项 > 0：是“结果没读取”问题。

---

## 7. 如何自行定位这类问题

1. 确认工厂是否真的执行了：

   ```bash
   grep -n "FactoryCreateFile: StaticMesh with" Saved/Logs/CarlaUE4.log
   ```
2. 确认网格是否真的构建、保存了：

   ```bash
   grep -n "Built static mesh" Saved/Logs/CarlaUE4.log
   grep -n "Moving .*\.uasset" Saved/Logs/CarlaUE4.log
   ```
3. 确认插件读到几个对象：

   ```bash
   grep -n "Import returned" Saved/Logs/CarlaUE4.log
   ```
4. 如果“构建了但读到 0 个”，去检查 `ImportTask->Result` 和 `ImportTask->ImportedObjectPaths` 的读取代码。

---

## 8. 总结

**UE4.26 的 `UAssetToolsImpl::ImportAssetTasks` 只把导入结果写进 `ImportTask->ImportedObjectPaths`，不写 `Result`。** 插件如果只读 `Result`，就会在“网格已经导入成功”的情况下拿到 0 个对象，随后路径猜测和资产注册表兜底都找不到，最终误判为导入失败。读取 `ImportedObjectPaths` 并 `LoadObject` 即可解决。

---

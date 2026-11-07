# 如何从崩溃日志判定：是 `CollectGarbage` 回收了对象？

> 本文是 [MuJoCo XML 导入崩溃：Datasmith GC 回收导入对象（UE4.26）](../mujoco_import_gc_crash.md) 的补充说明，回答：
>
> 为什么日志里只有一行 `Unhandled Exception: SIGSEGV: invalid attempt to read memory at address 0x00000000e30a0490`，就能判断是 `CollectGarbage()` 把导入时创建的对象回收了？

---

## 1. 地址本身能说明什么

```text
Unhandled Exception: SIGSEGV: invalid attempt to read memory at address 0x00000000e30a0490
```

- 这是 **read**（不是 write）——代码在读取某个对象的内存；
- 地址**不是 0 附近**：纯空指针解引用通常读 `0x0`、`0x8`、`0x10` 这类小地址；
- `0x00000000e30a0490` 是「看起来像指针、实际不可映射」的垃圾值，典型于**对象已释放、内存被分配器改写后，代码又通过它读 vtable 或成员**；
- 同一地址在多次崩溃中**完全一致**（11-05 的三次崩溃都是 `0xe30a0490`），说明是**确定性**的释放后内存内容，而不是随机野指针。

**但这只能证明「use-after-free 类野指针」，不能证明是谁释放的。** 是谁释放的，要看下面的证据。

---

## 2. 证据详解

### 2.1 崩溃栈：对象死在 `ImportObject` 期间

崩溃时的调用栈（节选）：

```text
UAssetToolsImpl::ImportAssetsInternal        ← 崩溃点（ResolveSupportedClass）
UAssetToolsImpl::ImportAssetTasks
UMujocoGenerationAction::AttemptMeshImport
UMujocoGenerationAction::ImportSingleMesh
UMujocoGenerationAction::ImportNodeRecursive
...
UMujocoImportFactory::FactoryCreateFile
UFactory::ImportObject                        ← 工厂调用在这里面
UAssetToolsImpl::ImportAssetsInternal         ← 外层（拖入的 .xml）
FImportFilesByPath::Run
UImportSubsystem::HandleNextTick
```

关键推理：

- 在同一个 `ImportAssetsInternal` 里，`Factory` 在调用 `ImportObject` **之前**刚被正常使用过（`Factory->ImportObject(...)` 本身能调进去）；
- 调用返回后，**下一次**使用同一个 `Factory`（`Factory->ResolveSupportedClass()`）就崩溃了；
- 指针值没有变化（不是传错指针），唯一解释是：**对象在 `ImportObject` 执行期间被销毁了**。

### 2.2 日志时序：窗口内只发生了 Datasmith 的 GC

崩溃前最后几行日志：

```text
LogUObjectHash: Compacting FUObjectHashTables data took   2.88ms
LogDatasmithImport: Imported z1_Link00 in [0 min 2.070 s]
LoadErrors: Warning: Mesh has primitives with no materials assigned: 0_z1_Link00.stl
=== Critical error ===
Unhandled Exception: SIGSEGV: invalid attempt to read memory at address 0x00000000e30a0490
```

查看源码可知， 这一行是在 `CollectGarbage()` **之后**才打印的：

```cpp
// DatasmithImportFactory.cpp:340  ReportImportStats
CollectGarbage(GARBAGE_COLLECTION_KEEPFLAGS);                    // :349  ← 显式 GC
...
UE_LOG(LogDatasmithImport, Log, TEXT("%s %s in [%d min %.3f s]%s"), ImportContext.bIsAReimport ? TEXT("Reimported") : TEXT("Imported"), ImportContext.Scene->GetName(), ElapsedMin, ElapsedSeconds, *MemoryStats);
```

因此「日志紧挨着崩溃」=「GC 刚跑完，控制权回到 AssetTools，随即崩溃」。

也可以在**源码里全局搜这个格式串**

```shell
grep -rn 'in \[%d min' 
  /home/ubuntu/UnrealEngine_4.26/Engine/Plugins/Enterprise/DatasmithImporter/Source --include=*.cpp
```

输出

```shell
/home/ubuntu/UnrealEngine_4.26/Engine/Plugins/Enterprise/DatasmithImporter/Source/DatasmithImporter/Private/DatasmithImportFactory.cpp:366:		UE_LOG(LogDatasmithImport, Log, TEXT("%s %s in [%d min %.3f s]%s"), ImportContext.bIsAReimport ? TEXT("Reimported") : TEXT("Imported"), ImportContext.Scene->GetName(), ElapsedMin, ElapsedSeconds, *MemoryStats);
```

[← 返回主文档](../mujoco_import_gc_crash.md)

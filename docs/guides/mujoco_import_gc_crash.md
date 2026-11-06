# MuJoCo XML 导入崩溃： GC 回收导入对象（UE4.26）

本文记录在 **UE4.26 + CarlaUE4（hutb 工程）** 中，把 MuJoCo `.xml` 从文件管理器拖入内容浏览器后，编辑器在网格导入完成后发生 **SIGSEGV** 崩溃的问题：现象、完整日志、根因分析与修复方案。

---

## 1. 现象

- 拖入 `.xml` 后，前几个网格顺利导入，日志出现 `Imported <mesh> in [0 min X s]`，紧接着编辑器崩溃退出。
- 崩溃对话框显示 `Caught signal 11 Segmentation fault`，日志里是：
  - `Unhandled Exception: SIGSEGV: invalid attempt to read memory at address 0x00000000e30a0490`
- 崩溃点不在 Datasmith 里，而是在**导入成功之后**的 AssetTools 收尾代码中。

---

## 2. 崩溃日志

```text
[2026.11.05-04.15.47:735][299]LogLayoutUV: FindBestPacking (Total Time: 0 ms, Avg Efficiency: -nan)
[2026.11.05-04.15.47:823][299]LogUObjectHash: Compacting FUObjectHashTables data took   2.88ms
[2026.11.05-04.15.47:826][299]LogDatasmithImport: Imported z1_Link00 in [0 min 2.070 s]
[2026.11.05-04.15.47:826][299]LoadErrors: Warning: Mesh has primitives with no materials assigned: 0_z1_Link00.stl
[2026.11.05-04.15.47:875][299]LogCore: === Critical error: ===
Unhandled Exception: SIGSEGV: invalid attempt to read memory at address 0x00000000e30a0490

[2026.11.05-04.15.47:875][299]LogCore: 0x00001539f794e517 libUE4Editor-AssetTools.so!UAssetToolsImpl::ImportAssetsInternal(TArray<FString, TSizedDefaultAllocator<32> > const&, FString const&, TArray<TTuple<FString, FString>, TSizedDefaultAllocator<32> >*, FAssetImportParams const&) const [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:2126]
0x00001539f79511f9 libUE4Editor-AssetTools.so!UAssetToolsImpl::ImportAssetTasks(TArray<UAssetImportTask*, TSizedDefaultAllocator<32> > const&) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:1170]
0x0000153554c0d8fd libUE4Editor-URLabEditor.so!UMujocoGenerationAction::AttemptMeshImport(FString const&, FString const&, EFBXNormalGenerationMethod::Type) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoMeshImporter.cpp:213]
0x0000153554c0cd32 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::ImportSingleMesh(FString const&, FString const&) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoMeshImporter.cpp:91]
0x0000153554c04aa5 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::ImportNodeRecursive(FXmlNode const*, USCS_Node*, UBlueprint*, FString const&, FString const&, TMap<FString, FString, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FString, false> > const&, TMap<FString, FVector, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FVector, false> > const&, TMap<FString, FString, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FString, false> > const&, TMap<FString, FMuJoCoMaterialData, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FMuJoCoMaterialData, false> > const&, TMap<FString, UTexture2D*, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, UTexture2D*, false> > const&, FMjCompilerSettings const&, bool, USCS_Node*) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoXmlParser.cpp:471]
0x0000153554c0600f libUE4Editor-URLabEditor.so!UMujocoGenerationAction::ImportNodeRecursive(FXmlNode const*, USCS_Node*, UBlueprint*, FString const&, FString const&, TMap<FString, FString, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FString, false> > const&, TMap<FString, FVector, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FVector, false> > const&, TMap<FString, FString, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FString, false> > const&, TMap<FString, FMuJoCoMaterialData, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FMuJoCoMaterialData, false> > const&, TMap<FString, UTexture2D*, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, UTexture2D*, false> > const&, FMjCompilerSettings const&, bool, USCS_Node*) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoXmlParser.cpp:979]
0x0000153554bf47c0 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::GenerateForBlueprintXml(UBlueprint*, FString const&, FXmlFile const*) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp:231]
0x0000153554bf3a80 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::GenerateForBlueprintXml(UBlueprint*, FString const&) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp:125]
0x0000153554bf3897 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::GenerateForBlueprint(UBlueprint*, FString const&) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp:107]
0x0000153554c0bd06 libUE4Editor-URLabEditor.so!UMujocoImportFactory::FactoryCreateFile(UClass*, UObject*, FName, EObjectFlags, FString const&, char16_t const*, FFeedbackContext*, bool&) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoImportFactory.cpp:200]
0x0000153a09daf9fe libUE4Editor-UnrealEd.so!UFactory::ImportObject(UClass*, UObject*, FName, EObjectFlags, FString const&, char16_t const*, bool&) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/Factories/Factory.cpp:201]
0x00001539f794e30c libUE4Editor-AssetTools.so!UAssetToolsImpl::ImportAssetsInternal(TArray<FString, TSizedDefaultAllocator<32> > const&, FString const&, TArray<TTuple<FString, FString>, TSizedDefaultAllocator<32> >*, FAssetImportParams const&) const [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:2091]
0x00001539f7956cfd libUE4Editor-AssetTools.so!non-virtual thunk to UAssetToolsImpl::ImportAssets(TArray<FString, TSizedDefaultAllocator<32> > const&, FString const&, UFactory*, bool, TArray<TTuple<FString, FString>, TSizedDefaultAllocator<32> >*) const [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:0]
0x0000153a0a70ee2d libUE4Editor-UnrealEd.so!FImportFilesByPath::Run() [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/Subsystems/ImportSubsystem.cpp:95]
0x0000153a0a6bfc0e libUE4Editor-UnrealEd.so!UImportSubsystem::HandleNextTick() [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/Subsystems/ImportSubsystem.cpp:143]
0x0000153a0f8987c0 libUE4Editor-Engine.so!FTimerUnifiedDelegate::Execute() [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Engine/Public/TimerManager.h:51]
0x0000153a0f7e230c libUE4Editor-Engine.so!FTimerManager::Tick(float) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Engine/Private/TimerManager.cpp:878]
0x0000153a09c17664 libUE4Editor-UnrealEd.so!UEditorEngine::Tick(float, bool) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/EditorEngine.cpp:1362]
0x0000153a0a74ed12 libUE4Editor-UnrealEd.so!UUnrealEdEngine::Tick(float, bool) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/UnrealEdEngine.cpp:423]
0x000000000026c4c1 UE4Editor!FEngineLoop::Tick() [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Launch/Private/LaunchEngineLoop.cpp:4830]
0x000000000027ad83 UE4Editor!GuardedMain(char16_t const*) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Launch/Private/Launch.cpp:171]
0x0000153a08800286 libUE4Editor-UnixCommonStartup.so!CommonUnixMain(int, char**, int (*)(char16_t const*), void (*)()) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Unix/UnixCommonStartup/Private/UnixCommonStartup.cpp:264]
0x0000153a08624083 libc.so.6!__libc_start_main(+0xf2)
0x0000000000263d89 UE4Editor!_start()
```

## 3. 根因分析

### 3.1 调用链

```
UMujocoGenerationAction::AttemptMeshImport                     // 插件
  └─ AssetTools.ImportAssetTasks(ImportTasks)                  // AssetTools.cpp:1144
       └─ ImportAssetsInternal                                 // AssetTools.cpp:1666
            ├─ Factory = Params.SpecifiedFactory               // :1851-1853 自动化导入直接使用指定工厂
            ├─ Factory->SetAutomatedAssetImportData(...)       // :2087
            ├─ Factory->SetAssetImportTask(ImportTask)         // :2088 临时以 UPROPERTY 持有任务
            └─ Factory->ImportObject(...)                      // :2091 → Factory.cpp:162
                 └─ FactoryCreateFile (虚函数分发)              // DatasmithImportFactory.cpp:457
                      ├─ TranslatableSource.Translate(Scene)   // 解析 GLB
                      ├─ Import(ImportContext)                 // 生成 StaticMesh 等资产
                      └─ ReportImportStats(...)                // DatasmithImportFactory.cpp:340
                           └─ CollectGarbage(...)              // ★ 显式 GC（:349）
            ← 返回后：SetAssetImportTask(nullptr)
            ← 然后：ImportAssetType = Factory->ResolveSupportedClass()   // ★ 崩溃点
```

要点：GC **不是** AssetTools 触发的，而是 Datasmith 在每次导入收尾时（`ReportImportStats`）显式调用 `CollectGarbage()` 回收翻译过程的临时数据。日志里 `Imported <mesh> in [0 min X s]` 正是该函数在 GC **之后**打印的，所以这行日志紧挨着崩溃。

**延伸阅读**：[为什么日志中出现的这个 `Unhandled Exception: SIGSEGV: invalid attempt to read memory at address 0x00000000e30a0490`，就能知道是 `CollectGarbage` 把创建的对象给回收了？](mujoco_import_gc_crash/why_sigsegv_means_gc.md)

## 4. 解决方案

### 4.1 核心修复：导入期间保护 `ImportTask` 与 `Factory`

文件：`Source/URLabEditor/Private/MujocoMeshImporter.cpp`（`UMujocoGenerationAction::AttemptMeshImport`）

```cpp
// 运行导入。
// 注意：Datasmith 工厂在 FactoryCreateFile() 结束时调用 CollectGarbage()
// （DatasmithImportFactory.cpp 的 ReportImportStats）；UE4.26 中
// GARBAGE_COLLECTION_KEEPFLAGS 在编辑器里等于 RF_Standalone。
// 这里 NewObject 出来的 ImportTask / Factory 都不是 RF_Standalone 且未被 Root，
// GC 会把工厂回收，AssetTools 之后在 ImportAssetsInternal() 末尾执行
// Factory->ResolveSupportedClass() 时就会访问已释放对象并段错误。
// 所以导入期间必须把它们保持在根集里，TStrongObjectPtr 析构时会自动移出根集。
TStrongObjectPtr<UAssetImportTask> ImportTaskGuard(ImportTask);
TStrongObjectPtr<UFactory> ImportFactoryGuard(ImportTask->Factory);

TArray<UAssetImportTask*> ImportTasks;
ImportTasks.Add(ImportTask);
AssetTools.ImportAssetTasks(ImportTasks);

// 之后的 ImportTask->Result / ImportTask->ImportedObjectPaths 读取同样受保护
```

## 总结

就是在`ImportTask`和`Factory`执行到`CollectGarbage`的时候被当垃圾回收了。然后回来的时候还是要用`Factory`或`ImportTask`，从而导致的报错。

# 生成的蓝图不正常

> 适用场景：CarlaUE4 / hutb 工程，把 MuJoCo `.xml` 拖入内容浏览器后，由插件自动导入 `clean_meshes.py` 生成的 `.glb` 网格。
>
> 本文解释一个很容易误判的现象：**不弹窗、不报错、蓝图正常生成，但蓝图里没有任何网格**。
>
> 路径约定：项目路径相对 `hutb` 仓库根目录；引擎路径相对 `UnrealEngine_4.26` 引擎根目录。

---

## 1. 现象

- 拖入 XML 后，Content Browser 里**确实生成了蓝图**；
- 双击打开蓝图，组件树里只有 `MjBody` / `MjGeom` 这类逻辑组件，**没有 `Viz_*` 静态网格组件**；
- 视口里什么都不显示；
- 编辑器中**没有弹出任何窗口，也没有红色错误通知**；
- 日志里反复出现同一组三行：

```text
LogSlate: Warning: A modal window tried to take control while running in unattended script mode. 
LogOutputDevice: Error: === FDebug::DumpStackTrace(): ===
LogOutputDevice: Error: 
LogOutputDevice: Error: [Callstack] 0x000014e0d6eedeee libUE4Editor-GLTFImporter.so!GLTFImporterImpl::ShowOptionsWindow(FString const&, FString const&, UGLTFImportOptions&) [/home/ubuntu/UnrealEngine_4.26/Engine/Plugins/Editor/GLTFImporter/Source/GLTFImporter/Private/GLTFImportFactory.cpp:52]
LogOutputDevice: Error: [Callstack] 0x000014e0d6eef034 libUE4Editor-GLTFImporter.so!UGLTFImportFactory::FactoryCreateFile(UClass*, UObject*, FName, EObjectFlags, FString const&, char16_t const*, FFeedbackContext*, bool&) [/home/ubuntu/UnrealEngine_4.26/Engine/Plugins/Editor/GLTFImporter/Source/GLTFImporter/Private/GLTFImportFactory.cpp:104]
LogOutputDevice: Error: [Callstack] 0x000014e3c70f18ce libUE4Editor-UnrealEd.so!UFactory::ImportObject(UClass*, UObject*, FName, EObjectFlags, FString const&, char16_t const*, bool&) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/Factories/Factory.cpp:202]
LogOutputDevice: Error: [Callstack] 0x000014e3b54b330c libUE4Editor-AssetTools.so!UAssetToolsImpl::ImportAssetsInternal(TArray<FString, TSizedDefaultAllocator<32> > const&, FString const&, TArray<TTuple<FString, FString>, TSizedDefaultAllocator<32> >*, FAssetImportParams const&) const [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:2091]
LogOutputDevice: Error: [Callstack] 0x000014e3b54b61f9 libUE4Editor-AssetTools.so!UAssetToolsImpl::ImportAssetTasks(TArray<UAssetImportTask*, TSizedDefaultAllocator<32> > const&) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:1170]
LogOutputDevice: Error: [Callstack] 0x000014df1cb3d1bf libUE4Editor-URLabEditor.so!UMujocoGenerationAction::AttemptMeshImport(FString const&, FString const&, EFBXNormalGenerationMethod::Type) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoMeshImporter.cpp:216]
LogOutputDevice: Error: [Callstack] 0x000014df1cb3c6a1 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::ImportSingleMesh(FString const&, FString const&) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoMeshImporter.cpp:108]
LogOutputDevice: Error: [Callstack] 0x000014df1cb342f5 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::ImportNodeRecursive(FXmlNode const*, USCS_Node*, UBlueprint*, FString const&, FString const&, TMap<FString, FString, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FString, false> > const&, TMap<FString, FVector, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FVector, false> > const&, TMap<FString, FString, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FString, false> > const&, TMap<FString, FMuJoCoMaterialData, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FMuJoCoMaterialData, false> > const&, TMap<FString, UTexture2D*, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, UTexture2D*, false> > const&, FMjCompilerSettings const&, bool, USCS_Node*) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoXmlParser.cpp:471]
LogOutputDevice: Error: [Callstack] 0x000014df1cb3585f libUE4Editor-URLabEditor.so!UMujocoGenerationAction::ImportNodeRecursive(FXmlNode const*, USCS_Node*, UBlueprint*, FString const&, FString const&, TMap<FString, FString, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FString, false> > const&, TMap<FString, FVector, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FVector, false> > const&, TMap<FString, FString, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FString, false> > const&, TMap<FString, FMuJoCoMaterialData, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, FMuJoCoMaterialData, false> > const&, TMap<FString, UTexture2D*, FDefaultSetAllocator, TDefaultMapHashableKeyFuncs<FString, UTexture2D*, false> > const&, FMjCompilerSettings const&, bool, USCS_Node*) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoXmlParser.cpp:979]
LogOutputDevice: Error: [Callstack] 0x000014df1cb24010 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::GenerateForBlueprintXml(UBlueprint*, FString const&, FXmlFile const*) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp:231]
LogOutputDevice: Error: [Callstack] 0x000014df1cb232d0 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::GenerateForBlueprintXml(UBlueprint*, FString const&) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp:125]
LogOutputDevice: Error: [Callstack] 0x000014df1cb230e7 libUE4Editor-URLabEditor.so!UMujocoGenerationAction::GenerateForBlueprint(UBlueprint*, FString const&) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoGenerationAction.cpp:107]
LogOutputDevice: Error: [Callstack] 0x000014df1cb3b556 libUE4Editor-URLabEditor.so!UMujocoImportFactory::FactoryCreateFile(UClass*, UObject*, FName, EObjectFlags, FString const&, char16_t const*, FFeedbackContext*, bool&) [/home/ubuntu/hdd4/hutb/Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoImportFactory.cpp:200]
LogOutputDevice: Error: [Callstack] 0x000014e3c70f18ce libUE4Editor-UnrealEd.so!UFactory::ImportObject(UClass*, UObject*, FName, EObjectFlags, FString const&, char16_t const*, bool&) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/Factories/Factory.cpp:202]
LogOutputDevice: Error: [Callstack] 0x000014e3b54b330c libUE4Editor-AssetTools.so!UAssetToolsImpl::ImportAssetsInternal(TArray<FString, TSizedDefaultAllocator<32> > const&, FString const&, TArray<TTuple<FString, FString>, TSizedDefaultAllocator<32> >*, FAssetImportParams const&) const [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:2091]
LogOutputDevice: Error: [Callstack] 0x000014e3b54bbcfd libUE4Editor-AssetTools.so!non-virtual thunk to UAssetToolsImpl::ImportAssets(TArray<FString, TSizedDefaultAllocator<32> > const&, FString const&, UFactory*, bool, TArray<TTuple<FString, FString>, TSizedDefaultAllocator<32> >*) const [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Developer/AssetTools/Private/AssetTools.cpp:0]
LogOutputDevice: Error: [Callstack] 0x000014e3c80bacad libUE4Editor-UnrealEd.so!FImportFilesByPath::Run() [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/Subsystems/ImportSubsystem.cpp:95]
LogOutputDevice: Error: [Callstack] 0x000014e3c806ba8e libUE4Editor-UnrealEd.so!UImportSubsystem::HandleNextTick() [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/Subsystems/ImportSubsystem.cpp:143]
LogOutputDevice: Error: [Callstack] 0x000014e3cd1ec7c0 libUE4Editor-Engine.so!FTimerUnifiedDelegate::Execute() [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Engine/Public/TimerManager.h:51]
LogOutputDevice: Error: [Callstack] 0x000014e3cd13630c libUE4Editor-Engine.so!FTimerManager::Tick(float) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Engine/Private/TimerManager.cpp:878]
LogOutputDevice: Error: [Callstack] 0x000014e3c75c8564 libUE4Editor-UnrealEd.so!UEditorEngine::Tick(float, bool) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/EditorEngine.cpp:1362]
LogOutputDevice: Error: [Callstack] 0x000014e3c80fab92 libUE4Editor-UnrealEd.so!UUnrealEdEngine::Tick(float, bool) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Editor/UnrealEd/Private/UnrealEdEngine.cpp:423]
LogOutputDevice: Error: [Callstack] 0x000000000023b9c1 UE4Editor!FEngineLoop::Tick() [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Launch/Private/LaunchEngineLoop.cpp:4830]
LogOutputDevice: Error: [Callstack] 0x000000000024a283 UE4Editor!GuardedMain(char16_t const*) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Launch/Private/Launch.cpp:171]
LogOutputDevice: Error: [Callstack] 0x000014e3c61ac286 libUE4Editor-UnixCommonStartup.so!CommonUnixMain(int, char**, int (*)(char16_t const*), void (*)()) [/home/ubuntu/UnrealEngine_4.26/Engine/Source/Runtime/Unix/UnixCommonStartup/Private/UnixCommonStartup.cpp:264]
LogOutputDevice: Error: [Callstack] 0x000014e3c5fd0083 libc.so.6!__libc_start_main(+0xf2)
LogOutputDevice: Error: [Callstack] 0x0000000000233289 UE4Editor!_start()
LogOutputDevice: Error: 
The window was canceled.
LogAssetTools: The import task was canceled.
LogURLabEditor: [ImportSingleMesh] Import returned 0 objects:
```

---

## 2. 根因：把“弹窗”当成了“导入许可”

UE4.26 的 `UGLTFImportFactory::FactoryCreateFile` 里，`ShowOptionsWindow` 的返回值被当成了“用户是否同意导入”：

```cpp
// GLTFImportFactory.cpp
if (!GLTFImporterImpl::ShowOptionsWindow(Filepath, PackagePath, *ImporterOptions))
{
    bOutOperationCanceled = true;
    return nullptr;      // ← 窗口没显示出来，也走这里
}
```

而 `ShowOptionsWindow` 返回 `false` 有两种完全不同的原因：

1. 用户点了 Cancel；
2. **窗口根本没有显示出来**（无人值守模式下被 Slate 取消）。

工厂不区分这两种情况，统一按“用户取消导入”处理。

同时，选项窗口的默认状态是“不同意导入”：

```cpp
// GLTFOptionsWindow.cpp:21
bShouldImport = false;

// GLTFOptionsWindow.cpp:123（用户点击 Import 按钮时才会执行）
bShouldImport = true;
```

所以只要窗口没显示、没人点按钮，`ShouldImport()` 就一定是 `false`。

---

## 3. 完整调用链

```text
① 插件把导入任务标记为自动化
   MujocoMeshImporter.cpp:133      ImportTask->bAutomated = true;

② AssetTools 进入无人值守模式
   AssetTools.cpp:1667             Params.bAutomated = ImportTask->bAutomated;
   AssetTools.cpp:1668             GIsRunningUnattendedScript = true;

③ 选工厂：没有指定工厂时走自动发现
   自动发现 → UGLTFImportFactory

   AssetTools.cpp:2090   Factory->ImportObject(...)
                       │
                       │  ① 虚函数调用（vtable 槽位 = ImportObject）
                       │     UGLTFImportFactory 没有重写 ImportObject
                       ▼      → 落到基类 UFactory::ImportObject
                  Factory.cpp:162  UFactory::ImportObject(...)
                       │
                       ├─ :199  UE_LOG("FactoryCreateFile: %s with %s", ..., *GetClass()->GetName())
                       │         ← 日志里打印的 "GLTFImportFactory" 就是这里
                       │
                       │  ② 虚函数调用（vtable 槽位 = FactoryCreateFile）
                       ▼     UGLTFImportFactory 重写了 FactoryCreateFile
                  GLTFImportFactory.cpp:91  UGLTFImportFactory::FactoryCreateFile(...)
                       │
                       ▼
                  GLTFImporterImpl::ShowOptionsWindow(...)

④ 工厂无条件调用选项窗口
   GLTFImportFactory.cpp:99        GLTFImporterImpl::ShowOptionsWindow(...)
        │
        ▼
⑤ Slate 拒绝创建模态窗口
   SlateApplication.cpp:1872       if (GIsRunningUnattendedScript && !bSlowTaskWindow)
                                   {
                                       UE_LOG(LogSlate, Warning, "...window was canceled.");
                                       FDebug::DumpStackTraceToLog(...);
                                       return;          ← 窗口从未创建
                                   }

⑥ 窗口没显示，用户没点 Import
   GLTFOptionsWindow.cpp:21        bShouldImport = false;
   → ShouldImport() == false

⑦ 工厂把“窗口没显示”当成“用户取消”
   GLTFImportFactory.cpp:103      if (!ShowOptionsWindow(...))
                                  {
                                      bOutOperationCanceled = true;
                                      return nullptr;
                                  }

⑧ AssetTools 记录取消
   AssetTools.cpp:2137             UE_LOG(LogAssetTools, Log, TEXT("The import task was canceled."));

⑨ 插件拿不到网格
   MujocoMeshImporter.cpp:217-235  ImportTask->Result / ImportedObjectPaths 都为空
   [ImportSingleMesh] Import returned 0 objects:

⑩ 不创建网格组件
   MujocoXmlParser.cpp:471-476     UStaticMesh* NewMesh = ImportSingleMesh(...);
                                   if (NewMesh) { ... 创建 Viz_* ... }   ← 不成立
```


## 4. 为什么“有蓝图但里面空白”

蓝图是在组件生成之前就创建好的：

`Unreal/CarlaUE4/Plugins/UnrealRoboticsLab/Source/URLabEditor/Private/MujocoImportFactory.cpp:87`

```cpp
UBlueprint* NewBP = FKismetEditorUtilities::CreateBlueprint(
    ParentClass, InParent, InName, BPTYPE_Normal, ...);
```

无论后面网格导入成不成功，`NewBP` 都会被返回并注册到 Content Browser，所以蓝图一定存在。

但 `Viz_*` 网格组件只有在 `ImportSingleMesh` 返回非空时才会创建。所有网格都被取消后：

- 蓝图：存在；
- `MjBody` / `MjGeom` 等逻辑组件：存在；
- `Viz_*` 静态网格组件：**不存在**；
- 视口：空白。

---

## 5. 总结

由于不管是不是自动导入都会进入让用户选择的是否导入的界面，但是一开始就把自动导入设置成true，从而不会弹窗让用户选择。导致以为用户选择的是取消，后面想要制作网格被直接跳过。再回到网格的判断中，直接没有网格。由于一开始有创建一个蓝图，所以最终只有蓝图没有网格。


## 6. 解决方案

在GLTFImportFactory.cpp:99加入 if (!IsAutomatedImport()) 如果是自动导入，直接跳过选择弹窗，直接执行制作静态网格步骤。
```C++
if (!IsAutomatedImport())
	{
		const FString Filepath    = FPaths::ConvertRelativePathToFull(Filename);
		const FString PackagePath = InParent->GetPathName();

		if (!GLTFImporterImpl::ShowOptionsWindow(Filepath, PackagePath, *ImporterOptions))
		{
			bOutOperationCanceled = true;
			return nullptr;
		}
	}
```


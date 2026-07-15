// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "mujoco/mujoco.h"

#include "CoreMinimal.h"

#include "GameFramework/Actor.h"
#include "ProceduralMeshComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Runtime/Engine/Classes/Components/StaticMeshComponent.h"
#include "Components/ArrowComponent.h"
// #include "Components/InstancedStaticMeshComponent.h"
#include "MuJoCoSimulation.generated.h"

/**
 * @struct BodyInfo
 * @brief 包含从 MuJoCo 模型和数据中提取的有关刚体的信息。
 *
 * @property std::string name - 刚体名称。
 * @property int parent_id - 父刚体的 ID
 * @property mjtNum[3] pos - 身体位置的三维向量。
 * @property mjtNum[4] quat - MuJoCo 格式中刚体的四元数朝向。
 * @property FQuat quat2 - 刚体朝向以引擎的四元数表示。
 */
struct BodyInfo
{
	std::string name;
	int parent_id;
	mjtNum pos[3];
	mjtNum quat[4];
	FQuat quat2;
};

/**
 * @struct GeomInfo
 * @brief 包含从 MuJoCo 模型和数据中提取的几何信息。
 *
 * 该结构存储几何体对象的各种属性，例如名称、刚体 ID、类型、大小、位置、朝向和颜色。
 * 它提供了一种在 MuJoCo 仿真环境中管理和调整几何体的方法。
 *
 * @var std::string name
 * 几何体的名称标识符。
 *
 * @var int body_id
 * 该几何体所附着的刚体的 ID。
 *
 * @var int type
 * 几何体的类型（例如，长方体、球体等）。
 *
 * @var mjtNum size[3]
 * 沿每个轴的几何体维度。
 *
 * @var mjtNum pos[3]
 * The position of the geometry in 3D space.
 *
 * @var mjtNum posAdjust[3]
 * 附加位置调整值，初始值为零。
 *
 * @var mjtNum quat[4]
 * 以 MuJoCo 格式表示几何体朝向的四元数。
 *
 * @var FQuat quat2
 * 引擎格式的四元数，表示朝向。
 *
 * @var FLinearColor color
 * 引擎格式中几何体的颜色。
 */
struct GeomInfo
{
	std::string name;
	int body_id;
	int type;
	mjtNum size[3];
	mjtNum pos[3];
	mjtNum posAdjust[3];
	mjtNum quat[4];
	FQuat quat2;
	FLinearColor color;
	GeomInfo()
	{
		posAdjust[0] = 0;
		posAdjust[1] = 0;
		posAdjust[2] = 0;
	}
};

/**
 * @struct ModelInfo
 * @brief 表示有关 MuJoCo 模型的信息。
 *
 * 该结构包含我们在引擎中可能需要的 MuJoCo 身体和几何信息集合。
 *
 * @member bodies 包含刚体信息(BodyInfo)结构的向量，表示模型中的物理实体（具有质量、惯性等物理属性）。
 * @member geoms 表示模型中几何形状的几何体信息(GeomInfo)结构向量。定义了外观和碰撞检测边界。
 */
struct ModelInfo
{
	std::vector<BodyInfo> bodies;
	std::vector<GeomInfo> geoms;
};

/**
 * @struct FMjOceanCurrentLayer
 * @brief 单一深度层洋流参数
 *
 * @property float DepthM - 深度 (m, 负值表示水下深度)
 * @property float SpeedMS - 流速大小 (m/s)
 * @property float HorizAngleRad - 水平角度 (rad)，0 = +X 方向
 * @property float VertAngleRad - 垂直角度 (rad)，0 = 水平，+ = 向下
 */
USTRUCT(BlueprintType)
struct FMjOceanCurrentLayer
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean")
    float DepthM = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean")
    float SpeedMS = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean")
    float HorizAngleRad = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean")
    float VertAngleRad = 0.0f;
};

/**
 * @struct FMjOceanCurrentConfig
 * @brief 洋流配置参数
 *
 * 三层级联模型：Gauss-Markov + Stratified + Turbulent
 * 与 Python ocean_current.py 的 config.json 结构对应
 */
USTRUCT(BlueprintType)
struct FMjOceanCurrentConfig
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|Enable")
    bool bEnabled = false;

    // Gauss-Markov 参数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|GaussMarkov")
    float GM_MeanSpeed = 0.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|GaussMarkov")
    float GM_MeanHorizAngle = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|GaussMarkov")
    float GM_MeanVertAngle = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|GaussMarkov")
    float GM_Mu = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|GaussMarkov")
    float GM_NoiseAmp = 0.1f;

    // 分层洋流参数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|Stratified")
    TArray<FMjOceanCurrentLayer> StratifiedLayers;

    // 湍流参数
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|Turbulent")
    float TurbulentIntensity = 0.15f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ocean|Turbulent")
    float TurbulentIntegralScale = 1.0f;
};

/**
 * @brief 与引擎中的 MuJoCo 物理模拟交互的 Actor 类。
 *
 * 该类提供在虚幻引擎中加载、模拟和可视化 MuJoCo 物理模型的功能。
 * 它负责 MuJoCo 物理表示与引擎视觉组件之间的转换，从而实现实时物理模拟和可视化。
 *
 * 该模拟可通过蓝图函数进行控制，实现物理模拟的启动、暂停、重置和单步执行。
 * 它还能将 MuJoCo 的物体和几何体映射到引擎组件。
 *
 * 新增洋流功能：
 * - 三层级联洋流模型（Gauss-Markov + Stratified + Turbulent）
 * - 洋流拖曳力自动注入 xfrc_applied
 * - 洋流速度可实时可视化
 *
 * @note 需要将 MuJoCo 物理库正确集成到项目中。
 */
/**
 * @class AMuJoCoSimulation
 * @brief 用于在引擎中集成 MuJoCo 物理模拟的 Actor
 *
 * 该类提供加载、可视化和模拟 MuJoCo 物理模型的功能。
 * 它负责 MuJoCo 的物理表示与虚幻引擎的视觉组件之间的转换，从而实现实时物理模拟和可视化。
 */

// Protected 变量
/** @brief MuJoCo 仿真数据 */
// mjData* mData;

/** @brief MuJoCo 模型 */
// mjModel* mModel;

/** @brief 当前模型信息 */
// ModelInfo _info;

/** @brief 初始化模型信息 */
// ModelInfo _infoStart;

/** @brief 指示模拟当前是否正在运行的标志 */
// bool bSimulationRunning=false;

// Public 属性
/** @brief 将 MuJoCo 刚体 ID 映射到场景组件 */
// UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
// TMap<int,USceneComponent*> BodyMap;

/** @brief 将 MuJoCo 几何体 ID 映射到静态网格组件 */
// UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
// TMap<int,UStaticMeshComponent*> GeomMap1;

/** @brief 模拟过程中创建的所有程序化网格的集合 */
// UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
// TArray<UProceduralMeshComponent*> ProceduralMeshes;

/** @brief MuJoCo XML 模型文件的路径 */
// UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
// FString XmlSourcePath;

/** @brief 用于几何体可视化的可用静态网格集合 */
// UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
// TMap<int, UStaticMesh*> MeshAssets;

/** @brief 当未提供特定网格时使用的默认网格 */
// UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
// UStaticMesh* defaultMesh;
UCLASS()
class MUJOCOUE_API AMuJoCoSimulation : public AActor
{
	GENERATED_BODY()

public:
	// 为参与者属性设置默认值
	AMuJoCoSimulation();

protected:
	mjData *mData;
	mjModel *mModel;
	ModelInfo _info;  // 当前引擎中的身体和几何的模型信息
	ModelInfo _infoStart;
	bool bSimulationRunning = false;

	// ── 洋流模块（Phase 6）────────────────────────────

	/** @brief 洋流配置 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo|Ocean")
	FMjOceanCurrentConfig OceanCurrentConfig;

	/** @brief 当前洋流速度向量 [vx, vy, vz] (m/s) */
	FVector OceanCurrentVelocity;

	/** @brief Gauss-Markov 当前状态（内部） */
	float OceanGM_Speed;
	float OceanGM_HorizAngle;
	float OceanGM_VertAngle;

	/** @brief 湍流上次位置（用于空间相关性） */
	FVector OceanTurbLastPos;
	bool OceanTurbHasLastPos;

	/** @brief LCG 随机数状态（用于可复现性） */
	uint32 OceanRNGState;

	/** @brief 洋流阻力系数 (kg/s) */
	float OceanDragCoeff;

	/** @brief 洋流受影响的 body ID */
	int OceanCurrentBodyId;

	/** @brief 洋流可视化开关 */
	bool bOceanVisualizationEnabled;
	bool bStratifiedProfileShown;
	bool bOceanHeatmapShown;

	/** @brief 洋流箭头可视化组件 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo|Ocean")
	UArrowComponent* OceanArrowComponent;

	/** @brief 洋流速度日志频率（秒） */
	float OceanLogInterval;
	float OceanLastLogTime;

public:
	// ── 洋流公共接口 ─────────────────────────────────

	/** @brief 在 mj_step 之前调用，将洋流力注入 xfrc_applied */
	void ApplyOceanCurrent();

	/** @brief 重置所有洋流状态（仿真重置时调用） */
	void ResetOceanCurrent();

	/** @brief 获取当前位置的洋流速度（用于可视化） */
	FVector GetOceanCurrentVelocityAt(float x, float y, float z, float dt);

	/** @brief 设置洋流影响的 body 名称 */
	UFUNCTION(BlueprintCallable, Category = "MuJoCo|Ocean")
	void SetOceanCurrentBodyName(const FString& BodyName);

	/** @brief 切换洋流可视化（显示/隐藏箭头） */
	UFUNCTION(BlueprintCallable, Category = "MuJoCo|Ocean")
	void ToggleOceanVisualization();

	/** @brief 显示洋流分层剖面 */
	UFUNCTION(BlueprintCallable, Category = "MuJoCo|Ocean")
	void ShowStratifiedProfile();

	/** @brief 切换洋流热力图叠加 */
	UFUNCTION(BlueprintCallable, Category = "MuJoCo|Ocean")
	void ToggleOceanHeatmap();

	/** @brief 打印当前洋流状态到日志 */
	UFUNCTION(BlueprintCallable, Category = "MuJoCo|Ocean")
	void LogOceanStatus();

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
	TMap<int, USceneComponent *> BodyMap;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
	TMap<int, UStaticMeshComponent *> GeomMap1;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
	TMap<int, UProceduralMeshComponent *> GeomMap2;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
	TArray<UProceduralMeshComponent *> ProceduralMeshes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
	FString XmlSourcePath;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
	TMap<int, UStaticMesh *> MeshAssets;

	// 默认的纹理
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo")
	UStaticMesh *defaultMesh;

	// 仅用于可视化调试的缩放系数，不影响物理仿真数据，默认1.0即原始MuJoCo尺寸
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo|Debug")
	float VisualScaleMultiplier = 1.0f;

	// 动态几何体使用的材质，留空则使用引擎默认材质
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MuJoCo|Debug")
	UMaterialInterface* ProceduralMeshMaterial = nullptr;

protected:
	// 当游戏开始或该参与者生成时调用
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	/**
	* 模拟 MuJoCo 物理过程，时间步长为指定值。
	* 将 MuJoCo 物理模拟推进指定的时间增量。
	 *
	 * @param DeltaTime 模拟推进的时间步长（以秒为单位）
	 */
	void SimulateMuJoCo(float DeltaTime);

	/**
	 * @brief 从 MuJoCo 仿真中提取当前状态信息
	 *
	 * 该函数使用来自活动的 MuJoCo 仿真的当前物体和几何数据
	 * （包括位置、朝向和其他相关属性）填充提供的 ModelInfo 结构。
	 *
	 * @param modelInfo 指向 ModelInfo 结构，该结构将填充当前仿真状态
	 */
	void ExtractCurrentState(ModelInfo &modelInfo);

	/**
	 * @brief 更新视觉表示以匹配当前仿真状态
	 *
	 * 此函数从 MuJoCo 仿真中获取包含刚体和几何体数据的当前模型信息，
	 * 并更新相应的引擎组件以反映当前状态。
	 * 它会更新场景中物体和几何体的位置、旋转和其他视觉属性。
	 *
	 * @param Info 指向包含当前仿真状态的 ModelInfo 结构
	 */
	void UpdateSimulationView(const ModelInfo &Info);

	/**
	 * @brief 为模型中的所有几何体生成网格组件
	 *
	 * 该函数为提供的 ModelInfo 中的每个几何体创建并初始化相应的网格组件（静态或程序化）。
	 * 它能够处理来自 MuJoCo 的不同几何体类型（球体、胶囊体、立方体等），
	 * 并在虚幻引擎中创建相应的视觉表示。
	 *
	 * @param modelInfo 指向包含几何体信息的 ModelInfo 结构
	 */
	void GenerateMeshes(ModelInfo &modelInfo);

	/**
	 * @brief 将自定义的 MuJoCo 网格几何体转换为引擎中的程序化网格
	 *
	 * 此函数从 MuJoCo 模型中提取非基本形状（例如球体、立方体等）的几何体的网格数据，
	 * 并在引擎中创建相应的程序化网格组件。
	 * 它从 MuJoCo 模型中读取顶点位置、法线、面索引和其他网格属性，
	 * 并创建可在引擎场景中渲染的等效网格表示。
	 *
	 * @param mjModel 指向包含待提取网格数据的 MuJoCo 模型的指针
	 * @param  UObject* Outer 程序网格组件的所有者指针
	 */
	void ConvertMuJoCoModelToProceduralMeshes(const mjModel *mjModel, UObject *Outer);

	/**
	 * 设置静态网格组件的颜色。
	 *
	 * @param StaticMeshComponent 要更新的静态网格组件
	 * @param Color 要应用于网格的新线性颜色
	 */
	void SetMeshColor(UStaticMeshComponent *StaticMeshComponent, FLinearColor Color);

	/**
	 * used for 调试以打印一些属性
	 **/

	void LogInfo();

	// ── 动态几何体生成（基础类型）────────────────────
	/** @brief 动态生成平面网格 */
	void CreateProceduralPlane(UProceduralMeshComponent* MeshComp, float HalfXCm, float HalfYCm);

	/** @brief 动态生成球体网格 */
	void CreateProceduralSphere(UProceduralMeshComponent* MeshComp, float RadiusCm, int32 Segments = 16);

	/** @brief 动态生成圆柱体网格（轴向为 Z 轴） */
	void CreateProceduralCylinder(UProceduralMeshComponent* MeshComp, float RadiusCm, float HalfHeightCm, int32 Segments = 16);

	/** @brief 动态生成长方体网格 */
	void CreateProceduralBox(UProceduralMeshComponent* MeshComp, float HalfXCm, float HalfYCm, float HalfZCm);

	/** @brief 动态生成胶囊体网格（轴向为 Z 轴） */
	void CreateProceduralCapsule(UProceduralMeshComponent* MeshComp, float RadiusCm, float HalfCylHeightCm, int32 Segments = 16);

public:
	// 每一帧都调用
	virtual void Tick(float DeltaTime) override;

	UFUNCTION(BlueprintCallable, Category = "MuJoCo")
	bool LoadModel(FString Xml);

	UFUNCTION(BlueprintCallable, Category = "MuJoCo")
	void StartSimulation();

	UFUNCTION(BlueprintCallable, Category = "MuJoCo")
	void PauseSimulation();

	UFUNCTION(BlueprintCallable, Category = "MuJoCo")
	void ResetSimulation();

	UFUNCTION(BlueprintCallable, Category = "MuJoCo")
	void StepSimulation();

	UFUNCTION(BlueprintCallable, Category = "MuJoCo")
	void SetControl(int Id, float Value);
};

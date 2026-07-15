// Fill out your copyright notice in the Description page of Project Settings.

#include "MuJoCoSimulation.h"

#include "mujoco/mujoco.h"
#include <vector>
#include <string>
#include <cstring>
#include <cmath>

#include "KismetProceduralMeshLibrary.h"
#include "ProceduralMeshConversion.h"

FVector CalculateWorldPosition(const FVector &BaseLocation, const FQuat &BaseRotation, const FVector &RelativeLocation)
{
	return BaseLocation + BaseRotation.RotateVector(RelativeLocation);
}

FQuat CalculateWorldRotation(const FQuat &BaseRotation, const FQuat &RelativeRotation)
{
	return RelativeRotation * BaseRotation;
}

// 抽取模型信息
ModelInfo ExtractModelInfo(const mjModel *m)
{
	ModelInfo modelInfo;  // 返回的模型信息对象

	// 抽取 MuJoCo 模型中的刚体(body)信息
	for (int i = 0; i < m->nbody; ++i)
	{
		BodyInfo bodyInfo;
		// 读取名称
		bodyInfo.name = std::string(m->names + m->name_bodyadr[i]);  // 名称字符串池的指针 + 第i个刚体名称在字符串池中的偏移量
		// 复制位置数据
		// m->body_pose: [x0,y0,z0, x1,y1,z2, ...]
		// 第i个body：从索引 3*i 到 3*(i+1)
		std::copy(m->body_pos + 3 * i, m->body_pos + 3 * (i + 1), bodyInfo.pos);  
		// 复制四元数数据
		std::copy(m->body_quat + 4 * i, m->body_quat + 4 * (i + 1), bodyInfo.quat);
		bodyInfo.parent_id = m->body_parentid[i];  // 记录父级关系
		// 调整四元数构造的顺序：MuJoCo格式为 [w,x,y,z] -> 引擎格式：FQuat(x,y,z,w)
		bodyInfo.quat2 = FQuat(bodyInfo.quat[1], bodyInfo.quat[2], bodyInfo.quat[3], bodyInfo.quat[0]);
		modelInfo.bodies.push_back(bodyInfo);
	}

	// 抽取 MuJoCo 模型中的几何体(geom)信息
	for (int i = 0; i < m->ngeom; ++i)
	{
		GeomInfo geomInfo;
		geomInfo.name = std::string(m->names + m->name_geomadr[i]);
		geomInfo.body_id = m->geom_bodyid[i];  // 所属刚体body的 ID
		geomInfo.type = m->geom_type[i];  // 几何体类型枚举
		std::copy(m->geom_size + 3 * i, m->geom_size + 3 * (i + 1), geomInfo.size);
		std::copy(m->geom_pos + 3 * i, m->geom_pos + 3 * (i + 1), geomInfo.pos);
		std::copy(m->geom_quat + 4 * i, m->geom_quat + 4 * (i + 1), geomInfo.quat);
		geomInfo.quat2 = FQuat(geomInfo.quat[1], geomInfo.quat[2], geomInfo.quat[3], geomInfo.quat[0]);
		// 检查此几何体是否具有材质或纹理信息
		if (m->geom_matid[i] >= 0)  // 有材质的情况
		{
			int matid = m->geom_matid[i];
			geomInfo.color = FLinearColor(
				m->mat_rgba[matid * 4 + 0],  // R 颜色分量
				m->mat_rgba[matid * 4 + 1],  // G
				m->mat_rgba[matid * 4 + 2],  // B
				m->mat_rgba[matid * 4 + 3]); // A
	
			if (m->mat_texid[matid] >= 0)  // 存在纹理则进行处理
			{
				int texid = m->mat_texid[matid];
				// 纹理是存在的，但我们将使用几何体颜色作为基础色。
				geomInfo.color = FLinearColor(
					m->geom_rgba[i * 4 + 0],
					m->geom_rgba[i * 4 + 1],
					m->geom_rgba[i * 4 + 2],
					m->geom_rgba[i * 4 + 3]);
				//	geomInfo.texId = texid;
			}
		}
		// 否则，使用几何体特定的 RGBA 颜色
		else
		{
			geomInfo.color = FLinearColor(
				m->geom_rgba[i * 4 + 0],
				m->geom_rgba[i * 4 + 1],
				m->geom_rgba[i * 4 + 2],
				m->geom_rgba[i * 4 + 3]);
		}
		
		// 调整尺寸以用作比例尺（不同几何体类型需要不同的尺寸转换策略，以适应引擎的表示方式）
		// 假设所有网格均为原始网格。
		// 转换坐标系和单位（右手系->左手系；米->厘米）
		// 1 米 大小 -> 在 UE 中为 100 厘米。
		switch (geomInfo.type)
		{
		case mjGEOM_CYLINDER:  // 圆柱体
			geomInfo.size[0] *= 2;  // 半径 -> 直径
			geomInfo.size[2] = geomInfo.size[1] * 2;  // 高度调整
			geomInfo.size[1] = geomInfo.size[0];
			break;
		case mjGEOM_CAPSULE:  // 胶囊体
			geomInfo.size[2] = geomInfo.size[1] + geomInfo.size[0];  // 高度调整
			geomInfo.size[0] *= 2;
			geomInfo.size[1] = geomInfo.size[0];
			break;
		case mjGEOM_SPHERE:  // 球体
			geomInfo.size[0] *= 2;
			geomInfo.size[1] = geomInfo.size[0];
			geomInfo.size[2] = geomInfo.size[0];
			break;
		case mjGEOM_BOX:  // 长方体
			geomInfo.size[0] *= 2;
			geomInfo.size[1] *= 2;
			geomInfo.size[2] *= 2;
			break;
		case mjGEOM_ELLIPSOID:  // 椭圆体
			geomInfo.size[0] *= 2;
			geomInfo.size[1] *= 2;
			geomInfo.size[2] *= 2;
			break;
			break;
		}
		modelInfo.geoms.push_back(geomInfo);
	}

	return modelInfo;
}

// 生成网格组件
// 优先级顺序：手动配置的静态网格 > 基础几何体（球体、立方体等） > MuJoCo 网格几何体
void AMuJoCoSimulation::GenerateMeshes(ModelInfo &modelInfo)
{
	BodyMap.Empty();
	GeomMap1.Empty();
	GeomMap2.Empty();

	// ── 生成刚体(body)组件 ────────────────────────────
	int BodyId = 0;
	for (const BodyInfo &bodyInfo : modelInfo.bodies)
	{
		USceneComponent *sceneComponent = NewObject<USceneComponent>(this, FName(*(FString(bodyInfo.name.c_str()) + *FString::Printf(TEXT("_Body%d"), BodyId))));
		BodyMap.Add(BodyId++, sceneComponent);
		sceneComponent->RegisterComponent();
		sceneComponent->SetRelativeLocation(FVector(bodyInfo.pos[0] * 100, bodyInfo.pos[1] * 100, bodyInfo.pos[2] * 100));
		sceneComponent->SetRelativeRotation(bodyInfo.quat2);
		if (bodyInfo.parent_id == 0)
			sceneComponent->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);
		else
		{
			USceneComponent *parentComponent = BodyMap[bodyInfo.parent_id];
			sceneComponent->AttachToComponent(parentComponent, FAttachmentTransformRules::KeepRelativeTransform);
		}
	}

	// ── 生成几何体(geom)网格组件 ──────────────────────
	int GeomId = 0;
	for (GeomInfo &geomInfo : modelInfo.geoms)
	{
		// 判断是否为基础几何体类型（可以动态生成）
		bool bIsBasicGeom = (geomInfo.type == mjGEOM_PLANE   ||
		                     geomInfo.type == mjGEOM_SPHERE   ||
		                     geomInfo.type == mjGEOM_CYLINDER ||
		                     geomInfo.type == mjGEOM_BOX      ||
		                     geomInfo.type == mjGEOM_CAPSULE  ||
		                     geomInfo.type == mjGEOM_ELLIPSOID);

		// 检查 MeshAssets 是否有手动配置的静态网格（手动配置优先级最高）
		auto *manualMesh = MeshAssets.Find(geomInfo.type) ? MeshAssets[geomInfo.type] : nullptr;

		if (manualMesh)
		{
			// ── 手动配置的静态网格（优先级最高）──────────
			UStaticMeshComponent *staticMeshComponent = NewObject<UStaticMeshComponent>(this);
			staticMeshComponent->RegisterComponent();
			staticMeshComponent->SetRelativeLocation(FVector(geomInfo.pos[0] * 100, geomInfo.pos[1] * 100, geomInfo.pos[2] * 100));
			staticMeshComponent->SetRelativeRotation(geomInfo.quat2);
			staticMeshComponent->AttachToComponent(this->BodyMap[geomInfo.body_id], FAttachmentTransformRules::KeepRelativeTransform);
			staticMeshComponent->SetStaticMesh(manualMesh);
			SetMeshColor(staticMeshComponent, geomInfo.color);
			staticMeshComponent->SetSimulatePhysics(false);
			staticMeshComponent->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			staticMeshComponent->SetWorldScale3D(FVector(geomInfo.size[0], geomInfo.size[1], geomInfo.size[2]) * VisualScaleMultiplier);
			this->GeomMap1.Add(GeomId, staticMeshComponent);
		}
		else if (bIsBasicGeom)
		{
			// ── 基础几何体：ProceduralMesh 动态生成 ──────
			// 注意：size 数据已在 ExtractModelInfo 中做过换算
			// cylinder: size[0]=diameter, size[2]=height
			// sphere:   size[0]=diameter
			// box:      size[0/1/2]=full dimensions
			// plane:    size[0]=half_x, size[1]=half_y（未换算）
			// capsule:  size[0]=diameter, size[2]=half_total_height
			UProceduralMeshComponent *procMesh = NewObject<UProceduralMeshComponent>(this);
			procMesh->RegisterComponent();
			procMesh->SetRelativeLocation(FVector(geomInfo.pos[0] * 100, geomInfo.pos[1] * 100, geomInfo.pos[2] * 100));
			procMesh->SetRelativeRotation(geomInfo.quat2);
			procMesh->AttachToComponent(this->BodyMap[geomInfo.body_id], FAttachmentTransformRules::KeepRelativeTransform);
			procMesh->SetSimulatePhysics(false);
			procMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

			// 将 VisualScaleMultiplier 乘入生成参数，不影响物理数据
			float S = VisualScaleMultiplier;

			switch (geomInfo.type)
			{
			case mjGEOM_PLANE:
				// size[0/1] = half extents（米），直接转 cm
				CreateProceduralPlane(procMesh,
					geomInfo.size[0] * 100.0f * S,
					geomInfo.size[1] * 100.0f * S);
				break;

			case mjGEOM_SPHERE:
			case mjGEOM_ELLIPSOID:
				// size[0] = diameter（米），radius = size[0]/2 * 100 cm
				CreateProceduralSphere(procMesh, geomInfo.size[0] * 50.0f * S);
				break;

			case mjGEOM_CYLINDER:
				// size[0] = diameter（米），size[2] = height（米）
				CreateProceduralCylinder(procMesh,
					geomInfo.size[0] * 50.0f * S,   // radius cm
					geomInfo.size[2] * 50.0f * S);  // half_height cm
				break;

			case mjGEOM_BOX:
				// size[0/1/2] = full dimensions（米）
				CreateProceduralBox(procMesh,
					geomInfo.size[0] * 50.0f * S,
					geomInfo.size[1] * 50.0f * S,
					geomInfo.size[2] * 50.0f * S);
				break;

			case mjGEOM_CAPSULE:
				// size[0] = diameter（米），size[2] = half_total_height（米）
				// half_cyl_height = half_total_height - radius
				CreateProceduralCapsule(procMesh,
					geomInfo.size[0] * 50.0f * S,                              // radius cm
					(geomInfo.size[2] - geomInfo.size[0] * 0.5f) * 100.0f * S); // half_cyl_height cm
				break;

			default:
				break;
			}
			// 赋值材质
			if (ProceduralMeshMaterial)
				procMesh->SetMaterial(0, ProceduralMeshMaterial);
			// 设置颜色
			this->GeomMap2.Add(GeomId, procMesh);
		}
		else
		{
			// ── mjGEOM_MESH 或其他：走原有 StaticMesh 路径 ─
			UStaticMeshComponent *staticMeshComponent = NewObject<UStaticMeshComponent>(this);
			staticMeshComponent->RegisterComponent();
			staticMeshComponent->SetRelativeLocation(FVector(geomInfo.pos[0] * 100, geomInfo.pos[1] * 100, geomInfo.pos[2] * 100));
			staticMeshComponent->SetRelativeRotation(geomInfo.quat2);
			staticMeshComponent->AttachToComponent(this->BodyMap[geomInfo.body_id], FAttachmentTransformRules::KeepRelativeTransform);

			if (geomInfo.type == mjGEOM_MESH && mModel->geom_dataid[GeomId] != -1)
			{
				int meshId = mModel->geom_dataid[GeomId];
				if (meshId >= 0 && meshId < ProceduralMeshes.Num())
				{
					UProceduralMeshComponent *procMeshRef = ProceduralMeshes[meshId];
					const FMeshDescription description = BuildMeshDescription(procMeshRef);
					TArray<const FMeshDescription *> descs;
					descs.Add(&description);
					UStaticMesh *NewStaticMesh = NewObject<UStaticMesh>(staticMeshComponent);
					NewStaticMesh->AddMaterial(procMeshRef->GetMaterial(0));
					NewStaticMesh->BuildFromMeshDescriptions(descs);
					staticMeshComponent->SetStaticMesh(NewStaticMesh);
				}
			}

			if (!staticMeshComponent->GetStaticMesh() && defaultMesh)
				staticMeshComponent->SetStaticMesh(defaultMesh);

			SetMeshColor(staticMeshComponent, geomInfo.color);
			staticMeshComponent->SetSimulatePhysics(false);
			staticMeshComponent->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			staticMeshComponent->SetWorldScale3D(FVector(geomInfo.size[0], geomInfo.size[1], geomInfo.size[2]) * VisualScaleMultiplier);
			this->GeomMap1.Add(GeomId, staticMeshComponent);
		}

		GeomId++;
	}
}

void AMuJoCoSimulation::ExtractCurrentState(ModelInfo &info)
{
	for (int i = 0; i < mModel->nbody; ++i)
	{
		// 从全局坐标（xpos 和 xquat）获取位置数据
		BodyInfo bodyInfo;
		std::copy(mData->xpos + 3 * i, mData->xpos + 3 * (i + 1), info.bodies[i].pos);     // 将mujoco中的位置数据 拷贝到 引擎(info) 中
		std::copy(mData->xquat + 4 * i, mData->xquat + 4 * (i + 1), info.bodies[i].quat);  // 获取身体的四元素数据
		info.bodies[i].quat2 = FQuat(info.bodies[i].quat[1], info.bodies[i].quat[2], info.bodies[i].quat[3], info.bodies[i].quat[0]);  // 调整四元素数据顺序
	}

	// 更新几何体状态
	for (int i = 0; i < mModel->ngeom; ++i)
	{   GeomInfo& geomInfo=info.geoms[i];
		std::copy(mData->geom_xpos + 3 * i, mData->geom_xpos + 3 * (i + 1), info.geoms[i].pos);
		// 将旋转矩阵转换为四元数
		const mjtNum *mat = mData->geom_xmat + 9 * i;
		mjtNum quat[4];
		mju_mat2Quat(quat, mat);  // 将 3D 旋转矩阵转换为四元数

		geomInfo.quat2 = FQuat(quat[1], quat[2], quat[3], quat[0]);
	}
}

AMuJoCoSimulation::AMuJoCoSimulation()
{
	// 设置此 Actor 每帧调用 Tick() 函数。
	// 如果不需要此功能，可以将其关闭以提高性能。
	PrimaryActorTick.bCanEverTick = true;

	// CreateDefaultSubobject 必须在 RF_ClassDefaultObject 检查之前调用
	// 否则 PIE 实例的 GetComponents 无法枚举到这些组件

	// 创建洋流箭头可视化组件
	OceanArrowComponent = CreateDefaultSubobject<UArrowComponent>(TEXT("OceanCurrentArrow"));
	if (OceanArrowComponent)
	{
		OceanArrowComponent->SetupAttachment(RootComponent);
		OceanArrowComponent->bHiddenInGame = true;  // 默认隐藏
		OceanArrowComponent->ArrowColor = FColor(0, 255, 255);  // 青色表示洋流
	}

	// 使用一个圆柱体作为模型的替代，否则拖进去看不到
	UStaticMeshComponent* Cylinder = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VisualRepresentation"));
	Cylinder->SetupAttachment(RootComponent);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(TEXT("/Game/StarterContent/Shapes/Shape_Cylinder.Shape_Cylinder"));
	if (CylinderAsset.Succeeded())
	{
		Cylinder->SetStaticMesh(CylinderAsset.Object);
		Cylinder->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
		Cylinder->SetWorldScale3D(FVector(1.f));
	}

	// 使用对象查找器在类的构造函数中自动加载网格
	static ConstructorHelpers::FObjectFinder<UStaticMesh> StaticMesh(TEXT("StaticMesh'/Game/Carla/Static/SM_Plane.SM_Plane'"));
	defaultMesh = StaticMesh.Object;

	// CDO 检查：CDO 只需要注册组件，不需要初始化运行时状态
	if (HasAnyFlags(RF_ClassDefaultObject))
	{
		return;
	}

	// 以下是非 CDO 实例的运行时初始化
	mData = nullptr;
	mModel = nullptr;
	bSimulationRunning = false;
	XmlSourcePath = TEXT("mujoco/pendulum.xml");

	// 洋流模块初始化
	OceanGM_Speed = OceanCurrentConfig.GM_MeanSpeed;
	OceanGM_HorizAngle = OceanCurrentConfig.GM_MeanHorizAngle;
	OceanGM_VertAngle = OceanCurrentConfig.GM_MeanVertAngle;
	OceanTurbLastPos = FVector(0, 0, -1);
	OceanTurbHasLastPos = false;
	OceanRNGState = 42;  // LCG 随机种子
	OceanDragCoeff = 10.0f;
	OceanCurrentBodyId = -1;  // -1 = 未设置，将在 ApplyOceanCurrent 中自动查找
	OceanCurrentVelocity = FVector(0, 0, 0);

	// 洋流可视化初始化
	bOceanVisualizationEnabled = false;
	bStratifiedProfileShown = false;
	bOceanHeatmapShown = false;
	OceanLogInterval = 5.0f;  // 每 5 秒输出一次洋流状态
	OceanLastLogTime = 0.0f;
}

// 开始仿真
void AMuJoCoSimulation::BeginPlay()
{
    Super::BeginPlay();
    mData = nullptr;
    mModel = nullptr;
    LoadModel(XmlSourcePath);
    if (mModel)
    {
        _info = ExtractModelInfo(mModel);
        ConvertMuJoCoModelToProceduralMeshes(mModel, this);
        GenerateMeshes(_info);

        // 隐藏构造函数里的占位圆柱体，避免遮挡真实几何体
        TArray<UStaticMeshComponent*> StaticComps;
        GetComponents<UStaticMeshComponent>(StaticComps);
        for (auto* Comp : StaticComps)
        {
            if (Comp->GetFName() == FName(TEXT("VisualRepresentation")))
            {
                Comp->SetVisibility(false, true);
                break;
            }
        }
    }
    StartSimulation();
    UE_LOG(LogTemp, Warning, TEXT("Mujoco begin play."));
}

void AMuJoCoSimulation::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (mData)
		mj_deleteData(mData);

	if (mModel)
		mj_deleteModel(mModel);
	mData = nullptr;
	mModel = nullptr;
	Super::EndPlay(EndPlayReason);
}

// 更新视觉表示以匹配当前仿真状态
void AMuJoCoSimulation::UpdateSimulationView(const ModelInfo &Info)
{
	FVector BaseLocation = BodyMap[0]->GetComponentLocation();
	FQuat BaseRotation = BodyMap[0]->GetComponentRotation().Quaternion();

	// ── 更新刚体位置 ──────────────────────────────────
	int BodyId = 0;
	for (const BodyInfo &bodyInfo : Info.bodies)
	{
		USceneComponent *sceneComponent = BodyMap[BodyId];
		if (!sceneComponent) { BodyId++; continue; }
		FVector WorldLoc = CalculateWorldPosition(BaseLocation, BaseRotation,
			FVector(bodyInfo.pos[0] * 100, bodyInfo.pos[1] * 100, bodyInfo.pos[2] * 100));
		sceneComponent->SetWorldLocation(WorldLoc);
		sceneComponent->SetWorldRotation(bodyInfo.quat2);
		BodyId++;
	}

	// ── 更新几何体位置（GeomMap1: StaticMesh，GeomMap2: ProceduralMesh）──
	int GeomId = 0;
	for (const GeomInfo &geomInfo : Info.geoms)
	{
		// geom_xpos 已经是 MuJoCo 全局世界坐标，直接转换单位即可
		FVector WorldLoc(
			geomInfo.pos[0] * 100,
			geomInfo.pos[1] * 100,
			geomInfo.pos[2] * 100);

		// StaticMesh 路径
		if (UStaticMeshComponent **comp = GeomMap1.Find(GeomId))
		{
			if (*comp)
			{
				(*comp)->SetWorldLocation(WorldLoc);
				(*comp)->SetWorldRotation(geomInfo.quat2);
			}
		}

		// ProceduralMesh 路径
		if (UProceduralMeshComponent **comp = GeomMap2.Find(GeomId))
		{
			if (*comp)
			{
				(*comp)->SetWorldLocation(WorldLoc);
				(*comp)->SetWorldRotation(geomInfo.quat2);
			}
		}

		GeomId++;
	}
}

// ── 洋流模块实现 ──────────────────────────────────
FVector AMuJoCoSimulation::GetOceanCurrentVelocityAt(float x, float y, float z, float dt)
{
	// ── Layer 1: Gauss-Markov 过程 ──────────────────
	// V? + μ·V = ω,  ω ~ N(0, σ2)
	// 离散化：V_{t+dt} = V_t + μ·(V_mean - V_t)·dt + σ·√dt·N(0,1)

	// LCG 随机数生成器 (Linear Congruential Generator)
	auto LCG = [this]() -> float {
		OceanRNGState = OceanRNGState * 1664525u + 1013904223u;
		return ((int32)OceanRNGState >> 1) / (float)0x7FFFFFFF * 2.0f - 1.0f;  // [-1, 1]
	};

	float noiseS = OceanCurrentConfig.GM_NoiseAmp * sqrtf(dt) * LCG();
	OceanGM_Speed += OceanCurrentConfig.GM_Mu * (OceanCurrentConfig.GM_MeanSpeed - OceanGM_Speed) * dt + noiseS;
	OceanGM_Speed = FMath::Max(0.0f, OceanGM_Speed);  // 速度非负

	float noiseH = OceanCurrentConfig.GM_NoiseAmp * sqrtf(dt) * LCG();
	OceanGM_HorizAngle += (OceanCurrentConfig.GM_Mu * (OceanCurrentConfig.GM_MeanHorizAngle - OceanGM_HorizAngle) + noiseH) * dt;

	float noiseV = OceanCurrentConfig.GM_NoiseAmp * sqrtf(dt) * LCG();
	OceanGM_VertAngle += (OceanCurrentConfig.GM_Mu * (OceanCurrentConfig.GM_MeanVertAngle - OceanGM_VertAngle) + noiseV) * dt;

	// NED 坐标系 → MuJoCo Z 向上
	float cosV = cosf(OceanGM_VertAngle);
	FVector vGM(
		OceanGM_Speed * cosV * cosf(OceanGM_HorizAngle),
		OceanGM_Speed * cosV * sinf(OceanGM_HorizAngle),
		-OceanGM_Speed * sinf(OceanGM_VertAngle)
	);

	// ── Layer 2: 分层洋流 (Stratified) ──────────────
	FVector vStrat(0, 0, 0);
	if (OceanCurrentConfig.StratifiedLayers.Num() >= 2)
	{
		// 深度 = -z (z 向上)
		float depth = -z;
		const auto& layers = OceanCurrentConfig.StratifiedLayers;

		// 边界处理：浅于最浅层
		if (depth <= layers[0].DepthM)
		{
			float cosV2 = cosf(layers[0].VertAngleRad);
			vStrat = FVector(
				layers[0].SpeedMS * cosV2 * cosf(layers[0].HorizAngleRad),
				layers[0].SpeedMS * cosV2 * sinf(layers[0].HorizAngleRad),
				-layers[0].SpeedMS * sinf(layers[0].VertAngleRad)
			);
		}
		else if (depth >= layers.Last().DepthM)  // 深于最深层
		{
			float cosV2 = cosf(layers.Last().VertAngleRad);
			vStrat = FVector(
				layers.Last().SpeedMS * cosV2 * cosf(layers.Last().HorizAngleRad),
				layers.Last().SpeedMS * cosV2 * sinf(layers.Last().HorizAngleRad),
				-layers.Last().SpeedMS * sinf(layers.Last().VertAngleRad)
			);
		}
		else
		{
			// 在两层之间线性插值
			for (int i = 0; i < layers.Num() - 1; ++i)
			{
				if (layers[i].DepthM <= depth && depth <= layers[i + 1].DepthM)
				{
					float t = (depth - layers[i].DepthM) /
							  (layers[i + 1].DepthM - layers[i].DepthM);

					float cosV1 = cosf(layers[i].VertAngleRad);
					FVector v1(
						layers[i].SpeedMS * cosV1 * cosf(layers[i].HorizAngleRad),
						layers[i].SpeedMS * cosV1 * sinf(layers[i].HorizAngleRad),
						-layers[i].SpeedMS * sinf(layers[i].VertAngleRad)
					);

					float cosV2 = cosf(layers[i + 1].VertAngleRad);
					FVector v2(
						layers[i + 1].SpeedMS * cosV2 * cosf(layers[i + 1].HorizAngleRad),
						layers[i + 1].SpeedMS * cosV2 * sinf(layers[i + 1].HorizAngleRad),
						-layers[i + 1].SpeedMS * sinf(layers[i + 1].VertAngleRad)
					);

					vStrat = v1 * (1.0f - t) + v2 * t;
					break;
				}
			}
		}
	}

	// ── Layer 3: 湍流扰动 (Turbulent) ───────────────
	FVector vTurb(0, 0, 0);
	FVector pos(x, y, z);

	if (OceanTurbHasLastPos)
	{
		float dist = (pos - OceanTurbLastPos).Size();
		float correlation = FMath::Exp(-dist / FMath::Max(OceanCurrentConfig.TurbulentIntegralScale, 0.01f));
		float noiseStrength = OceanCurrentConfig.TurbulentIntensity * sqrtf(1.0f - correlation * correlation);

		vTurb = FVector(
			noiseStrength * LCG() * 0.5f,
			noiseStrength * LCG() * 0.5f,
			noiseStrength * LCG() * 0.5f
		);
	}
	else
	{
		vTurb = FVector(
			OceanCurrentConfig.TurbulentIntensity * LCG() * 0.5f,
			OceanCurrentConfig.TurbulentIntensity * LCG() * 0.5f,
			OceanCurrentConfig.TurbulentIntensity * LCG() * 0.5f
		);
		OceanTurbHasLastPos = true;
	}

	OceanTurbLastPos = pos;

	// 总洋流速度 = 三层叠加
	return vGM + vStrat + vTurb;
}

void AMuJoCoSimulation::ApplyOceanCurrent()
{
	if (!OceanCurrentConfig.bEnabled || !mData || !mModel)
		return;

	// ── 查找 ROV body ───────────────────────────────
	int bodyId = OceanCurrentBodyId;
	if (bodyId < 0)
	{
		// 自动查找包含 "rov" 的 body
		for (int i = 0; i < mModel->nbody; ++i)
		{
			const char* name = mModel->names + mModel->name_bodyadr[i];
			if (strstr(name, "rov") != nullptr)
			{
				bodyId = i;
				OceanCurrentBodyId = i;
				break;
			}
		}
		if (bodyId < 0)
		{
			// 如果没找到，使用第一个自由 body
			for (int i = 0; i < mModel->nbody; ++i)
			{
				if (mModel->body_jntadr[i] >= 0)
				{
					bodyId = i;
					OceanCurrentBodyId = i;
					break;
				}
			}
			if (bodyId >= 0)
			{
				UE_LOG(LogTemp, Warning, TEXT("[Ocean] Auto fallback to body ID=%d"), bodyId);
			}
		}
	}

	if (bodyId < 0 || bodyId >= mModel->nbody)
		return;

	// ── 获取机器人位置 ──────────────────────────────
	float robotX = mData->xpos[3 * bodyId + 0];
	float robotY = mData->xpos[3 * bodyId + 1];
	float robotZ = mData->xpos[3 * bodyId + 2];

	// ── 计算洋流速度 ────────────────────────────────
	float dt = mModel->opt.timestep;
	OceanCurrentVelocity = GetOceanCurrentVelocityAt(robotX, robotY, robotZ, dt);

	// ── 施加洋流拖曳力到 xfrc_applied ───────────────
	// F_drag = -drag_coeff * V_current
	// MuJoCo xfrc_applied: [Fx, Fy, Fz, Tx, Ty, Tz]
	mData->xfrc_applied[bodyId * 6 + 0] = -OceanDragCoeff * OceanCurrentVelocity.X;
	mData->xfrc_applied[bodyId * 6 + 1] = -OceanDragCoeff * OceanCurrentVelocity.Y;
	mData->xfrc_applied[bodyId * 6 + 2] = -OceanDragCoeff * OceanCurrentVelocity.Z;
}

void AMuJoCoSimulation::ResetOceanCurrent()
{
	// 重置 Gauss-Markov 状态为均值
	OceanGM_Speed = OceanCurrentConfig.GM_MeanSpeed;
	OceanGM_HorizAngle = OceanCurrentConfig.GM_MeanHorizAngle;
	OceanGM_VertAngle = OceanCurrentConfig.GM_MeanVertAngle;

	// 重置湍流状态
	OceanTurbLastPos = FVector(0, 0, -1);
	OceanTurbHasLastPos = false;

	// 重置随机数种子（确保可复现性）
	OceanRNGState = 42;

	OceanCurrentVelocity = FVector(0, 0, 0);
	OceanCurrentBodyId = -1;  // 下次运行重新查找
}

void AMuJoCoSimulation::SetOceanCurrentBodyName(const FString& BodyName)
{
	if (!mModel || BodyName.IsEmpty())
		return;

	int id = mj_name2id(mModel, mjOBJ_BODY, TCHAR_TO_ANSI(*BodyName));
	if (id >= 0)
	{
		OceanCurrentBodyId = id;
		UE_LOG(LogTemp, Warning, TEXT("[Ocean] Set current body to: %s (ID=%d)"), *BodyName, id);
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("[Ocean] Body not found: %s, will auto-detect"), *BodyName);
		OceanCurrentBodyId = -1;
	}
}

// ── 洋流可视化模块 ────────────────────────────────
void AMuJoCoSimulation::ToggleOceanVisualization()
{
    bOceanVisualizationEnabled = !bOceanVisualizationEnabled;

    // 用组件名查找，确保在 PIE 实例里也能找到正确组件
    TArray<UArrowComponent*> ArrowComps;
    GetComponents<UArrowComponent>(ArrowComps);
    for (auto* Comp : ArrowComps)
	{
		if (Comp->GetFName().ToString().Contains(TEXT("OceanCurrentArrow")))
		{
			Comp->SetHiddenInGame(!bOceanVisualizationEnabled);
			Comp->SetVisibility(bOceanVisualizationEnabled);
			Comp->ArrowSize = 5.0f;
			Comp->ArrowLength = 200.0f;
			break;
		}
	}

    UE_LOG(LogTemp, Warning, TEXT("[Ocean] Visualization %s"),
        bOceanVisualizationEnabled ? TEXT("ON") : TEXT("OFF"));
}

void AMuJoCoSimulation::ShowStratifiedProfile()
{
	bStratifiedProfileShown = !bStratifiedProfileShown;
	if (bStratifiedProfileShown)
	{
		UE_LOG(LogTemp, Warning, TEXT("[Ocean] Showing stratified profile: %d layers"), OceanCurrentConfig.StratifiedLayers.Num());
		for (int i = 0; i < OceanCurrentConfig.StratifiedLayers.Num(); ++i)
		{
			const auto& layer = OceanCurrentConfig.StratifiedLayers[i];
			UE_LOG(LogTemp, Warning, TEXT("  Layer %d: depth=%.1fm speed=%.2f m/s angle=%.2f rad"),
					i, layer.DepthM, layer.SpeedMS, layer.HorizAngleRad);
		}
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("[Ocean] Hiding stratified profile"));
	}
}

void AMuJoCoSimulation::ToggleOceanHeatmap()
{
	bOceanHeatmapShown = !bOceanHeatmapShown;
	UE_LOG(LogTemp, Warning, TEXT("[Ocean] Heatmap %s"), bOceanHeatmapShown ? TEXT("ON") : TEXT("OFF"));
}

void AMuJoCoSimulation::LogOceanStatus()
{
	if (!mData || !mModel)
	{
		UE_LOG(LogTemp, Warning, TEXT("[Ocean] No model loaded"));
		return;
	}

	// ── 获取机器人位置 ────────────────────────────────
	FVector robotPos;
	if (OceanCurrentBodyId >= 0 && OceanCurrentBodyId < mModel->nbody)
	{
		robotPos = FVector(mData->xpos[3 * OceanCurrentBodyId + 0],
						   mData->xpos[3 * OceanCurrentBodyId + 1],
						   mData->xpos[3 * OceanCurrentBodyId + 2]);
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("[Ocean] Body ID invalid"));
		return;
	}

	float speed = OceanCurrentVelocity.Size();
	UE_LOG(LogTemp, Warning, TEXT("[Ocean Status] Position: (%.3f, %.3f, %.3f)"),
			robotPos.X, robotPos.Y, robotPos.Z);
	UE_LOG(LogTemp, Warning, TEXT("[Ocean Status] Current: (%.4f, %.4f, %.4f) | speed=%.4f m/s"),
			OceanCurrentVelocity.X, OceanCurrentVelocity.Y, OceanCurrentVelocity.Z, speed);
	UE_LOG(LogTemp, Warning, TEXT("[Ocean Status] GM Speed=%.4f HorizAngle=%.4f VertAngle=%.4f"),
			OceanGM_Speed, OceanGM_HorizAngle, OceanGM_VertAngle);
}

void AMuJoCoSimulation::SimulateMuJoCo(float DeltaTime)
{
	if (mData == nullptr || mModel == nullptr)
	{
		UE_LOG(LogTemp, Error, TEXT("Model or data is null"));
		return;
	}
	double startTime = mData->time;
	while (mData->time - startTime < DeltaTime)  // 当前步的仿真时间
	{
		// 洋流模块：在 mj_step 之前注入洋流拖曳力 (Phase 6)
		if (OceanCurrentConfig.bEnabled)
		{
			ApplyOceanCurrent();
		}
		mj_step(mModel, mData);  // 推进仿真，使用控制回调来获取外部力和控制（运行时更新mModel和mData中的数据）
	}

	ModelInfo info;
	if (!_info.bodies.size())
		return;
	ExtractCurrentState(_info);

	UpdateSimulationView(_info);
}


// 从 XML 文件加载 MuJoCo 模型
bool AMuJoCoSimulation::LoadModel(FString Xml)
{
	// 相对于 Content 的路径 + 编辑器中配置的 XML Source Path
	FString FullPath = FPaths::Combine(FPaths::ConvertRelativePathToFull(FPaths::ProjectContentDir()), Xml);
	if (!FPaths::FileExists(FullPath))
	{
		UE_LOG(LogTemp, Error, TEXT("File does not exist: %s"), *FullPath);
		return false;
	}
	mModel = mj_loadXML(TCHAR_TO_ANSI(*FullPath), NULL, NULL, 0);
	if (!mModel)
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to load model from %s"), *Xml);
		return false;
	}
	mData = mj_makeData(mModel);
	if (!mData)
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to make data for model"));
		return false;
	}
	return true;
}

// 每一帧都被调用
void AMuJoCoSimulation::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	if (bSimulationRunning)
		SimulateMuJoCo(DeltaTime);

	// 洋流可视化快捷键 
	// 注意：实际游戏中需要通过 Input 系统绑定按键
	// 这里提供日志接口，可通过蓝图或控制台命令调用
	if (OceanCurrentConfig.bEnabled && mData && mModel)
	{
		// 洋流速度日志（定期输出）
		OceanLastLogTime += DeltaTime;
		if (OceanLastLogTime >= OceanLogInterval && bOceanVisualizationEnabled)
		{
			LogOceanStatus();
			OceanLastLogTime = 0;
		}
		if (bOceanVisualizationEnabled && OceanArrowComponent && OceanCurrentVelocity.SizeSquared() > 0)
		{
			OceanArrowComponent->SetWorldRotation(OceanCurrentVelocity.Rotation());
		}
	}
}


void AMuJoCoSimulation::SetControl(int Id, float Value)
{
	if (!mData || !mModel || mModel->nu <= Id)
		return;
	mData->ctrl[Id] = Value;
}


void AMuJoCoSimulation::StartSimulation()
{
	bSimulationRunning = true;
}


void AMuJoCoSimulation::PauseSimulation()
{
	bSimulationRunning = false;
}


void AMuJoCoSimulation::ResetSimulation()
{
	bSimulationRunning = false;
	if (mData)
		mj_deleteData(mData);
	mData = mj_makeData(mModel);

	// 洋流模块：重置洋流状态
	ResetOceanCurrent();

	ExtractCurrentState(_info);
	UpdateSimulationView(_info);
}

void AMuJoCoSimulation::StepSimulation()
{
	LogInfo();
	mj_step(mModel, mData);
	ExtractCurrentState(_info);
	UpdateSimulationView(_info);
	LogInfo();
}

void AMuJoCoSimulation::LogInfo()
{
	// 记录刚体(body)信息
	int BodyId = 0;
	for (const auto &bodyInfo : _info.bodies)
	{
		if (USceneComponent *bodyComponent = BodyMap[BodyId])
		{
			FVector worldLoc = bodyComponent->GetComponentLocation();
			FRotator worldRot = bodyComponent->GetComponentRotation();
			UE_LOG(LogTemp, Warning, TEXT("Body[%d] %hs - WorldLocation: (%f, %f, %f), WorldRotation: (%f, %f, %f)"),
				   BodyId,
				   bodyInfo.name.c_str(),
				   worldLoc.X, worldLoc.Y, worldLoc.Z,
				   worldRot.Pitch, worldRot.Yaw, worldRot.Roll);
		}
		BodyId++;
	}

    // ── 记录几何体信息 ────────────────────────────────
	int GeomId = 0;
	for (const auto &geomInfo : _info.geoms)
	{
		// GeomMap1 存静态网格，GeomMap2 存动态网格，需要分别检查
		if (UStaticMeshComponent **compPtr = GeomMap1.Find(GeomId))
		{
			if (UStaticMeshComponent *geomComponent = *compPtr)
			{
				FVector worldLoc = geomComponent->GetComponentLocation();
				FRotator worldRot = geomComponent->GetComponentRotation();
				UE_LOG(LogTemp, Warning, TEXT("Geom[%d] %hs - WorldLocation: (%f, %f, %f), WorldRotation: (%f, %f, %f)"),
					   GeomId, geomInfo.name.c_str(),
					   worldLoc.X, worldLoc.Y, worldLoc.Z,
					   worldRot.Pitch, worldRot.Yaw, worldRot.Roll);
			}
		}
		else if (UProceduralMeshComponent **compPtr2 = GeomMap2.Find(GeomId))
		{
			if (UProceduralMeshComponent *geomComponent = *compPtr2)
			{
				FVector worldLoc = geomComponent->GetComponentLocation();
				FRotator worldRot = geomComponent->GetComponentRotation();
				UE_LOG(LogTemp, Warning, TEXT("Geom[%d] %hs - WorldLocation: (%f, %f, %f), WorldRotation: (%f, %f, %f)"),
					   GeomId, geomInfo.name.c_str(),
					   worldLoc.X, worldLoc.Y, worldLoc.Z,
					   worldRot.Pitch, worldRot.Yaw, worldRot.Roll);
			}
		}
		GeomId++;
	}
}

// 将MuJoCo模型中的网格数据转换为Engine的程序化网格组件，
// 专门处理复杂的自定义网格几何体（mjGEOM_MESH类型）
void AMuJoCoSimulation::ConvertMuJoCoModelToProceduralMeshes(const mjModel *mjModel, UObject *Outer)
{
	// 输入模型不能为空、输出对象Out必须有效（用于组件创建）、模型中至少包含一个网格
	if (!mjModel || !Outer || mjModel->nmesh == 0)
	{
		UE_LOG(LogTemp, Warning, TEXT("Invalid input parameters or no meshes in model"));
		return;
	}

	// 遍历 MuJoCo 模型中的所有网格
	for (int mesh_id = 0; mesh_id < mjModel->nmesh; mesh_id++)
	{
		// 从 MuJoCo 中抽取网格数据
		const int vert_start = mjModel->mesh_vertadr[mesh_id];  // 顶点起始索引
		const int nvert = mjModel->mesh_vertnum[mesh_id];  // 顶点数量
		const float *mj_vertices = &mjModel->mesh_vert[vert_start * 3];  // 顶点数组指针(每个顶点占用3个float)

		// 面片数据提取
		const int face_start = mjModel->mesh_faceadr[mesh_id];  // 面片起始索引
		const int nface = mjModel->mesh_facenum[mesh_id];  // 面片数量
		const int *mj_faces = &mjModel->mesh_face[face_start * 3];  // 面片数组指针

		// 跳过空网格
		if (nvert == 0 || nface == 0)
			continue;

		// 将顶点转换为引擎坐标
		TArray<FVector> UnrealVertices;
		for (int i = 0; i < nvert; i++)
		{
			const float *v = &mj_vertices[i * 3];
			UnrealVertices.Add(FVector(
				v[0] * 100.0f,	// X: 米 -> 厘米，保持朝向
				-v[1] * 100.0f, // Y: 翻转坐标轴，右手系->左手系
				v[2] * 100.0f	// Z: 米 -> 厘米
				));
		}

		// 将面片转换为引擎的缠绕顺序（顺时针而不是 MuJoCo 的逆时针）
		TArray<int32> UnrealTriangles;
		for (int i = 0; i < nface; i++)
		{
			UnrealTriangles.Add(mj_faces[i * 3 + 0]);  // 顶点 0 保持不变
			UnrealTriangles.Add(mj_faces[i * 3 + 2]); // 顶点 2 和顶点 1 交换
			UnrealTriangles.Add(mj_faces[i * 3 + 1]);
		}

		// 创建并注册 程序化网格组件
		UProceduralMeshComponent *ProcMesh = NewObject<UProceduralMeshComponent>(Outer);
		ProcMesh->RegisterComponent();

		// Generate normals/tangents (using placeholder UVs if none exist)
		TArray<FVector> Normals;
		TArray<FVector2D> UVs;
		TArray<FProcMeshTangent> Tangents;

		// Generate default UVs if needed (flat projection)
		UVs.SetNum(UnrealVertices.Num());
		for (FVector2D &uv : UVs)
		{
			uv = FVector2D(0.5f, 0.5f); // Simple default
		}

		// 自动法线切线计算
		// 计算原理: 基于顶点位置和UV坐标，自动生成平滑的法线和切线向量
		UKismetProceduralMeshLibrary::CalculateTangentsForMesh(
			UnrealVertices,   // 顶点位置
			UnrealTriangles,  // 三角形索引
			UVs,              // UV 坐标
			Normals,          // 输出：法线
			Tangents);        // 输出：切线

		// 创建网格分段
		ProcMesh->CreateMeshSection(
			0,                 // 网格分段的 ID
			UnrealVertices,    // 顶点数组
			UnrealTriangles,   // 三角形索引
			Normals,           // 法线数组
			UVs,               // UV 坐标数组
			TArray<FColor>(),  // 顶点颜色（空）
			Tangents,          // 切线数组
			true               // 启用碰撞
		);

		ProcMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

		// Add to output array

		ProceduralMeshes.Add(ProcMesh);
		ProcMesh->SetVisibility(false);  // 初始不可见
	}

	return;
}

void AMuJoCoSimulation::SetMeshColor(UStaticMeshComponent *StaticMeshComponent, FLinearColor Color)
{
	if (!StaticMeshComponent)
		return;
	// TODO: 向网格添加材质仍然存在问题
	//	static UMaterialInterface* Material= FindObject<UMaterialInterface>(ANY_PACKAGE,TEXT("M_BaseColor"));         ///Game/MuJoCo/M_BaseColor.
	//	if (!Material)
	//	{
	//	               return;
	//	}

	//	StaticMeshComponent->SetMaterial(0, Material);

	// 创建动态材质实例
	UMaterialInterface *BaseMaterial = StaticMeshComponent->GetMaterial(0);
	if (!BaseMaterial)
		return;

	UMaterialInstanceDynamic *DynamicMaterial = UMaterialInstanceDynamic::Create(BaseMaterial, StaticMeshComponent);
	if (!DynamicMaterial)
		return;

	DynamicMaterial->SetVectorParameterValue(FName("BaseColor"), Color);

	StaticMeshComponent->SetMaterial(0, DynamicMaterial);
}

// 动态几何体生成实现
void AMuJoCoSimulation::CreateProceduralPlane(UProceduralMeshComponent* MeshComp, float HalfXCm, float HalfYCm)
{
	TArray<FVector> Vertices = {
		FVector(-HalfXCm, -HalfYCm, 0),
		FVector( HalfXCm, -HalfYCm, 0),
		FVector( HalfXCm,  HalfYCm, 0),
		FVector(-HalfXCm,  HalfYCm, 0)
	};
	TArray<int32> Triangles = {0, 1, 2, 0, 2, 3};
	TArray<FVector> Normals = {
		FVector(0,0,1), FVector(0,0,1), FVector(0,0,1), FVector(0,0,1)
	};
	TArray<FVector2D> UVs = {
		FVector2D(0,0), FVector2D(1,0), FVector2D(1,1), FVector2D(0,1)
	};
	TArray<FProcMeshTangent> Tangents;
	UKismetProceduralMeshLibrary::CalculateTangentsForMesh(Vertices, Triangles, UVs, Normals, Tangents);
	MeshComp->CreateMeshSection(0, Vertices, Triangles, Normals, UVs, TArray<FColor>(), Tangents, false);
}

void AMuJoCoSimulation::CreateProceduralSphere(UProceduralMeshComponent* MeshComp, float RadiusCm, int32 Segments)
{
	TArray<FVector> Vertices;
	TArray<int32> Triangles;
	TArray<FVector> Normals;
	TArray<FVector2D> UVs;
	TArray<FProcMeshTangent> Tangents;

	int32 Rings = FMath::Max(Segments / 2, 4);

	for (int32 i = 0; i <= Rings; i++)
	{
		float phi = PI * i / Rings;
		float sinPhi = FMath::Sin(phi);
		float cosPhi = FMath::Cos(phi);

		for (int32 j = 0; j <= Segments; j++)
		{
			float theta = 2.0f * PI * j / Segments;
			FVector Normal(sinPhi * FMath::Cos(theta), sinPhi * FMath::Sin(theta), cosPhi);
			Vertices.Add(Normal * RadiusCm);
			Normals.Add(Normal.GetSafeNormal());
			UVs.Add(FVector2D((float)j / Segments, (float)i / Rings));
		}
	}

	for (int32 i = 0; i < Rings; i++)
	{
		for (int32 j = 0; j < Segments; j++)
		{
			int32 a = i * (Segments + 1) + j;
			int32 b = a + 1;
			int32 c = (i + 1) * (Segments + 1) + j;
			int32 d = c + 1;
			Triangles.Add(a); Triangles.Add(c); Triangles.Add(b);
			Triangles.Add(b); Triangles.Add(c); Triangles.Add(d);
		}
	}

	UKismetProceduralMeshLibrary::CalculateTangentsForMesh(Vertices, Triangles, UVs, Normals, Tangents);
	MeshComp->CreateMeshSection(0, Vertices, Triangles, Normals, UVs, TArray<FColor>(), Tangents, false);
}

void AMuJoCoSimulation::CreateProceduralCylinder(UProceduralMeshComponent* MeshComp, float RadiusCm, float HalfHeightCm, int32 Segments)
{
	TArray<FVector> Vertices;
	TArray<int32> Triangles;
	TArray<FVector> Normals;
	TArray<FVector2D> UVs;
	TArray<FProcMeshTangent> Tangents;

	// ── 侧面 ──────────────────────────────────────────
	for (int32 i = 0; i <= Segments; i++)
	{
		float theta = 2.0f * PI * i / Segments;
		float cosT = FMath::Cos(theta);
		float sinT = FMath::Sin(theta);

		// 底圈
		Vertices.Add(FVector(RadiusCm * cosT, RadiusCm * sinT, -HalfHeightCm));
		Normals.Add(FVector(cosT, sinT, 0));
		UVs.Add(FVector2D((float)i / Segments, 0));

		// 顶圈
		Vertices.Add(FVector(RadiusCm * cosT, RadiusCm * sinT, HalfHeightCm));
		Normals.Add(FVector(cosT, sinT, 0));
		UVs.Add(FVector2D((float)i / Segments, 1));
	}

	for (int32 i = 0; i < Segments; i++)
	{
		int32 base = i * 2;
		Triangles.Add(base);     Triangles.Add(base + 2); Triangles.Add(base + 1);
		Triangles.Add(base + 1); Triangles.Add(base + 2); Triangles.Add(base + 3);
	}

	// ── 底面 cap ──────────────────────────────────────
	int32 bottomCenter = Vertices.Num();
	Vertices.Add(FVector(0, 0, -HalfHeightCm));
	Normals.Add(FVector(0, 0, -1));
	UVs.Add(FVector2D(0.5f, 0.5f));

	for (int32 i = 0; i <= Segments; i++)
	{
		float theta = 2.0f * PI * i / Segments;
		Vertices.Add(FVector(RadiusCm * FMath::Cos(theta), RadiusCm * FMath::Sin(theta), -HalfHeightCm));
		Normals.Add(FVector(0, 0, -1));
		UVs.Add(FVector2D(0.5f + 0.5f * FMath::Cos(theta), 0.5f + 0.5f * FMath::Sin(theta)));
	}

	for (int32 i = 0; i < Segments; i++)
	{
		Triangles.Add(bottomCenter);
		Triangles.Add(bottomCenter + i + 2);
		Triangles.Add(bottomCenter + i + 1);
	}

	// ── 顶面 cap ──────────────────────────────────────
	int32 topCenter = Vertices.Num();
	Vertices.Add(FVector(0, 0, HalfHeightCm));
	Normals.Add(FVector(0, 0, 1));
	UVs.Add(FVector2D(0.5f, 0.5f));

	for (int32 i = 0; i <= Segments; i++)
	{
		float theta = 2.0f * PI * i / Segments;
		Vertices.Add(FVector(RadiusCm * FMath::Cos(theta), RadiusCm * FMath::Sin(theta), HalfHeightCm));
		Normals.Add(FVector(0, 0, 1));
		UVs.Add(FVector2D(0.5f + 0.5f * FMath::Cos(theta), 0.5f + 0.5f * FMath::Sin(theta)));
	}

	for (int32 i = 0; i < Segments; i++)
	{
		Triangles.Add(topCenter);
		Triangles.Add(topCenter + i + 1);
		Triangles.Add(topCenter + i + 2);
	}

	UKismetProceduralMeshLibrary::CalculateTangentsForMesh(Vertices, Triangles, UVs, Normals, Tangents);
	MeshComp->CreateMeshSection(0, Vertices, Triangles, Normals, UVs, TArray<FColor>(), Tangents, false);
}

void AMuJoCoSimulation::CreateProceduralBox(UProceduralMeshComponent* MeshComp, float HalfXCm, float HalfYCm, float HalfZCm)
{
	TArray<FVector> Vertices;
	TArray<int32> Triangles;
	TArray<FVector> Normals;
	TArray<FVector2D> UVs;
	TArray<FProcMeshTangent> Tangents;

	// 每个面 4 个顶点，共 6 个面
	struct Face { FVector n; FVector v[4]; };
	TArray<Face> Faces = {
		// +X
		{FVector(1,0,0), {FVector(HalfXCm,-HalfYCm,-HalfZCm), FVector(HalfXCm,HalfYCm,-HalfZCm), FVector(HalfXCm,HalfYCm,HalfZCm), FVector(HalfXCm,-HalfYCm,HalfZCm)}},
		// -X
		{FVector(-1,0,0), {FVector(-HalfXCm,HalfYCm,-HalfZCm), FVector(-HalfXCm,-HalfYCm,-HalfZCm), FVector(-HalfXCm,-HalfYCm,HalfZCm), FVector(-HalfXCm,HalfYCm,HalfZCm)}},
		// +Y
		{FVector(0,1,0), {FVector(HalfXCm,HalfYCm,-HalfZCm), FVector(-HalfXCm,HalfYCm,-HalfZCm), FVector(-HalfXCm,HalfYCm,HalfZCm), FVector(HalfXCm,HalfYCm,HalfZCm)}},
		// -Y
		{FVector(0,-1,0), {FVector(-HalfXCm,-HalfYCm,-HalfZCm), FVector(HalfXCm,-HalfYCm,-HalfZCm), FVector(HalfXCm,-HalfYCm,HalfZCm), FVector(-HalfXCm,-HalfYCm,HalfZCm)}},
		// +Z
		{FVector(0,0,1), {FVector(-HalfXCm,-HalfYCm,HalfZCm), FVector(HalfXCm,-HalfYCm,HalfZCm), FVector(HalfXCm,HalfYCm,HalfZCm), FVector(-HalfXCm,HalfYCm,HalfZCm)}},
		// -Z
		{FVector(0,0,-1), {FVector(-HalfXCm,HalfYCm,-HalfZCm), FVector(HalfXCm,HalfYCm,-HalfZCm), FVector(HalfXCm,-HalfYCm,-HalfZCm), FVector(-HalfXCm,-HalfYCm,-HalfZCm)}}
	};

	static const TArray<FVector2D> FaceUVs = {FVector2D(0,0),FVector2D(1,0),FVector2D(1,1),FVector2D(0,1)};

	for (int32 f = 0; f < Faces.Num(); f++)
	{
		int32 base = f * 4;
		for (int32 v = 0; v < 4; v++)
		{
			Vertices.Add(Faces[f].v[v]);
			Normals.Add(Faces[f].n);
			UVs.Add(FaceUVs[v]);
		}
		Triangles.Add(base);     Triangles.Add(base+1); Triangles.Add(base+2);
		Triangles.Add(base);     Triangles.Add(base+2); Triangles.Add(base+3);
	}

	UKismetProceduralMeshLibrary::CalculateTangentsForMesh(Vertices, Triangles, UVs, Normals, Tangents);
	MeshComp->CreateMeshSection(0, Vertices, Triangles, Normals, UVs, TArray<FColor>(), Tangents, false);
}

void AMuJoCoSimulation::CreateProceduralCapsule(UProceduralMeshComponent* MeshComp, float RadiusCm, float HalfCylHeightCm, int32 Segments)
{
	TArray<FVector> Vertices;
	TArray<int32> Triangles;
	TArray<FVector> Normals;
	TArray<FVector2D> UVs;
	TArray<FProcMeshTangent> Tangents;

	int32 CapRings = FMath::Max(Segments / 4, 2);

	// 生成顶点行的 lambda：r=圆圈半径，z=高度，法线=(cosT*nx, sinT*ny, nz)
	auto AddRing = [&](float r, float z, float nx, float nz, float vCoord)
	{
		for (int32 j = 0; j <= Segments; j++)
		{
			float theta = 2.0f * PI * j / Segments;
			float cosT = FMath::Cos(theta);
			float sinT = FMath::Sin(theta);
			Vertices.Add(FVector(r * cosT, r * sinT, z));
			Normals.Add(FVector(nx * cosT, nx * sinT, nz).GetSafeNormal());
			UVs.Add(FVector2D((float)j / Segments, vCoord));
		}
	};

	// ── 顶半球（phi: 0 → PI/2）──────────────────────
	for (int32 i = 0; i <= CapRings; i++)
	{
		float phi = (PI * 0.5f) * i / CapRings;
		float sinPhi = FMath::Sin(phi);
		float cosPhi = FMath::Cos(phi);
		AddRing(RadiusCm * sinPhi, HalfCylHeightCm + RadiusCm * cosPhi, sinPhi, cosPhi, 0.25f * i / CapRings);
	}

	// ── 底圆柱边（z=-H，与顶圆柱边 z=+H 之间形成柱面）──
	AddRing(RadiusCm, -HalfCylHeightCm, 1.0f, 0.0f, 0.5f);

	// ── 底半球（phi: PI/2 → PI）──────────────────────
	for (int32 i = 1; i <= CapRings; i++)
	{
		float phi = (PI * 0.5f) + (PI * 0.5f) * i / CapRings;
		float sinPhi = FMath::Sin(phi);
		float cosPhi = FMath::Cos(phi);
		AddRing(RadiusCm * sinPhi, -HalfCylHeightCm + RadiusCm * cosPhi, sinPhi, cosPhi, 0.5f + 0.5f * i / CapRings);
	}

	// 总行数：(CapRings+1) + 1 + CapRings = 2*CapRings+2
	int32 numRows = 2 * CapRings + 2;
	for (int32 i = 0; i < numRows - 1; i++)
	{
		for (int32 j = 0; j < Segments; j++)
		{
			int32 a = i * (Segments + 1) + j;
			int32 b = a + 1;
			int32 c = (i + 1) * (Segments + 1) + j;
			int32 d = c + 1;
			Triangles.Add(a); Triangles.Add(c); Triangles.Add(b);
			Triangles.Add(b); Triangles.Add(c); Triangles.Add(d);
		}
	}

	UKismetProceduralMeshLibrary::CalculateTangentsForMesh(Vertices, Triangles, UVs, Normals, Tangents);
	MeshComp->CreateMeshSection(0, Vertices, Triangles, Normals, UVs, TArray<FColor>(), Tangents, false);
}
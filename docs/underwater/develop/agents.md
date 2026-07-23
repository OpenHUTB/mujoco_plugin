# 开发代理（Agents）

遗憾的是，由于代理程序需要同时存在于 Python、C++ 和 UE 代码中，因此这个过程相当复杂。虽然并不难，但比较繁琐，我会在这里一步步指导你完成。

## 通用代理 <span id="general_agents"></span>

### Python 部分

首先，打开 [client/src/holoocean/agents.py](https://github.com/OpenHUTB/Underwater/blob/master/client/src/holoocean/agents.py) 文件。要创建代理程序，通常直接复制 [TurtleAgent](https://github.com/OpenHUTB/Underwater/blob/master/client/src/holoocean/agents.py#L624) 并根据自己的喜好进行编辑。你需要编辑以下内容：

* 类名

* 代理类型（agent_type）

* 所有与控制相关的内容。这包括所有常量和 [control_schemes()](https://github.com/OpenHUTB/Underwater/blob/d26be1f6b14112f69981388130332abaa3b348a3/client/src/holoocean/agents.py#L645) 函数。请确保在返回值中将代理的输入数量赋给 [ContinuousActionSpace](https://github.com/OpenHUTB/Underwater/blob/d26be1f6b14112f69981388130332abaa3b348a3/client/src/holoocean/agents.py#L648)。

Python 部分就差不多了，最终结果应该类似这样。
```python
class CustomAgent(HoloOceanAgent):
    """A simple custom bot.

    Inherits from :class:`HoloOceanAgent`."""
    # Underwater 中 CustomAgent.h 的常量
    __MAX = 160.0
    __MIN = -__MAX

    agent_type = "CustomAgent"

    @property
    def control_schemes(self):
        low = [self.__MIN]*4
        high = [self.__MAX]*4
        return [("[first, second, third, fourth]", ContinuousActionSpace([4], low=low, high=high))]

    def get_joint_constraints(self, joint_name):
        return None

    def __repr__(self):
        return "CustomAgent " + self.name

    def __act__(self, action):
        np.copyto(self._action_buffer, np.array(action))
        np.copyto(self._action_buffer, action)
```


在同一文件的下方，[AgentDefinition](https://github.com/OpenHUTB/Underwater/blob/d26be1f6b14112f69981388130332abaa3b348a3/client/src/holoocean/agents.py#L861) 类中，有一个字典将名称映射到 Python 类。为我们的新类添加一个条目，例如“CustomAgent”: CustomAgent,。名称应与类中设置的 agent_type 匹配。

### C++ 部分

接下来，在 UE4 中打开 [Underwater](https://github.com/OpenHUTB/Underwater)。然后转到“文件”->“打开 Visual Studio”（或者在您选择的 C++ 编辑器中打开项目文件）。您需要复制 4 个 TurtleAgent 文件，并相应地重命名它们：TurtleAgent.cpp、TurtleAgent.h、TurtleAgentController.cpp 和 TurtleAgentController.h 应分别复制到 CustomAgent.cpp、CustomAgent.h、CustomAgentController.cpp 和 CustomAgentController.h。确保它们与被复制的文件位于同一文件夹中（应该位于公共/私有文件夹的组合中）。

接下来，我们将编辑 CustomAgent.h。请执行以下操作：

* 将 `ATurtleAgent();` 改为 `ACustomAgent();`

* 将 `class HOLODECK_API ATurtleAgent : public AHolodeckAgent` 改为`class HOLODECK_API ACustomAgent : public AHolodeckAgent`

* 将 `unsigned int GetRawActionSizeInBytes() const override { return 2 * sizeof(float); };` 这行代码中的 2 改为你的代理的输入数量。

* 将 `float CommandArray[2];` 这行代码中的 2 改为你的代理的输入数量。


CustomAgent.cpp 文件是大部分魔法发生的地方：你的动态特性、对输入的反应等等都应该在这里实现。在其中，将以下所有内容更改为：

* `#include "TurtleAgent.h"` 改为 `#include "CustomAgent.h"`

* 所有 `ATurtleAgent` 改为 `ACustomAgent`

* 你希望代理执行的任何操作，或者它如何响应输入，都需要放入 `Tick(float DeltaSeconds)` 函数中。


在 CustomAgentController.h 文件中，将以下所有内容更改为：

* `#include "TurtleAgent.h"` 改为 `#include "CustomAgent.h"`

* `#include "TurtleAgentController.generated.h"` 改为 `#include "CustomAgentController.generated.h"`

* 将所有 `ATurtleAgentController` 实例更改为 `ACustomAgentController`


在 CustomAgentController.cpp 文件中，将以下所有内容更改为：

* `#include "TurtleAgentController.h"` 改为 `#include "CustomAgentController.h"`

将所有 `ATurtleAgentController` 实例更改为 `ACustomAgentController`

以上就是 C++ 部分的内容。


### 虚幻引擎

这一步可能有点隐蔽。在 UE4 中，点击顶部工具栏上的编译按钮。这会将我们新的 C++ 代码加载到 UE4 中。如果出现错误，很可能是上一步操作有误，需要返回调试。编译成功后，在内容浏览器中导航至 [Content/HolodeckContent/Agents](https://github.com/OpenHUTB/Underwater/tree/master/Content/HolodeckContent/Agents) 文件夹。创建一个新文件夹用于存放你的代理，并进入该文件夹。右键单击并选择创建蓝图类。此时会弹出一个对话框，要求你选择父类。选择上一步中的 C++ 类（`CustomAgent`），并将你的新蓝图命名为类似 CustomAgentBp 的名称。在这里，你可以添加网格、权重等，使你的代理拥有你想要的外观和重量。这有时会有点棘手，但网上有很多关于制作自定义 Pawn 的 UE4 教程。

最后，我们需要将 Python 类与 UE4/C++ 代码连接起来。在内容浏览器中导航至 [Content/](https://github.com/OpenHUTB/Underwater/tree/master/Content) 目录，然后打开 [HolodeckGameModeBP](https://github.com/OpenHUTB/Underwater/blob/master/Content/HolodeckGameModeBP.uasset)。您会在右侧的“默认”部分看到一个名为“Agent Bp Map”的条目。展开它，并插入一个新条目。在左侧选择您之前在代码中设置的 agent_type，然后在右侧选择我们刚刚创建的蓝图（CustomAgentBp）。

就是这样！如果您发现任何不清楚或错误的地方，请随时编辑并澄清，以便其他读者理解。您需要重新打包您的环境（参见上文），然后应该就可以使用您的新代理了！


## 浮力代理 <span id="buoyant_agents"></span>

`AHolodeckBuoyantAgent` 类的创建是为了避免未来所有添加到 Underwater 中的 AUV 都需要重新实现浮力动力学。只需设置一些必要的变量，一切即可开箱即用。所有物理信息都在 C++ 中设置，而不是在蓝图中设置。蓝图中设置的任何内容（例如质量或质心偏移）都会在 C++ 中被覆盖。

我们不会在此详细介绍如何创建自定义代理，请参阅上文相关章节。唯一的区别是，您需要继承 `AHolodeckBuoyantAgent` 而不是 `AHolodeckAgent`，并且可能需要复制 `AHoveringAUV` 的文件而不是 `ATurtleAgent` 的文件。


### 必要变量

!!! 注意
    所有这些变量都基于正确的原点存储（不包含 OffsetToOrigin 偏移量）。

必须在类构造函数中或在调用 `Super::InitializeAgent()` 之前在 `InitializeAgent` 函数中设置以下变量。
```cpp
float Volume;
FVector CenterBuoyancy;
FVector CenterMass;
float MassInKG;
FVector OffsetToOrigin = FVector(0,0,0);
```

这些设置基本都符合预期。如果你的网格导入时轴心点正确，那么你可以不用设置 `OffsetToOrigin`。


### 额外变量

!!! 注意
    除 `SurfacePoints` 外，所有这些变量均以正确的原点为基准存储（不包含 OffsetToOrigin 和 CenterVehicle 参数）。

您可以设置这些变量来自定义表面浮力的各种使用方式，即使不进行设置，所有变量也会被计算。表面浮力的计算方法是：在载具的“边界框”内随机采样点，然后实时检查有多少点位于表面之上。您可以通过在 UE4 中打开静态网格并点击“边界框”来查看此边界框。如果您的机器人不是方框，则此方法显然不够精确，但对于我们更接近方框的载具来说，这种方法是有效的。或者，如果您想离线采样并存储这些点，您可以手动显式设置它们。

```cpp
FVector CenterVehicle = FVector(0,0,0); // 载具中心相对于真实原点的位置。如果原点不是载具中心，则需要进行设置。
int NumSurfacePoints = 1000;
FBox BoundingBox = FBox();
TArray<FVector> SurfacePoints;
float SurfaceLevel = 0;
```

* `CenterVehicle` 是载具物理中心到真实原点的距离。它用于确保边界框位于正确的位置。如果您不使用载具中心作为表面点，则必须设置此值。

* `NumSurfacePoints` 可能是您接下来最可能需要设置的参数。顾名思义，它代表的是表面点的数量。根据机器人的大小，可能需要调整此值的大小。

* `BoundingBox` 是载具周围的边界框。如果未设置，网格会自动计算。如果自动计算的边界框过大，您可以手动设置。

* `SurfacePoints` 是采样点。如果您不想使用边界框方法，请显式设置此参数。注意：为了降低复杂度，这些点已预先加上 `OffsetToOrigin` 和 `CenterVehicle` 的值。（也就是说，我们不希望每个游戏刻都重复执行 2 * NumSurfacePoints 的加法运算）

* `SurfaceLevel` 是水位。对于我们所有的环境，该值均已设置为 0。


### 调试工具

为了能够可视化边界框和表面点，确保它们的位置正确，您可以在代理的 tick 方法中使用继承的 `ShowBoundingBox()` 和 `ShowSurfacePoints()` 函数。

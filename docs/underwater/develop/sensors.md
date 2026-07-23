# 开发传感器

与代理类似，传感器也是同时使用 C++ 和 Python 构建的。

## C++ <span id="cpp"></span>

每个传感器都需要一个“.h”头文件和一个“.cpp”文件，这是 C++ 的标准做法。

这两个文件都将放在 Underwater 代码库中。您的“.h”头文件很可能应该放在 [Source/Holodeck/Sensors/Public](https://github.com/OpenHUTB/Underwater/tree/master/Source/Holodeck/Sensors/Public) 目录下，而您的“.cpp”文件则应该放在 [Source/Holodeck/Sensors/Private](https://github.com/OpenHUTB/Underwater/tree/master/Source/Holodeck/Sensors/Private) 目录下。

### .h 文件

首先，您需要在 .h 文件中包含以下内容：
```cpp
#pragma once
#include "Holodeck.h"
#include "HolodeckSensor.h"
```

接下来，您需要设置传感器的类，其代码大致如下：
```cpp
#include "ExampleSensor.generated.h"

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class HOLODECK_API UExampleSensor : public UHolodeckSensor {
    GENERATED_BODY()
    public:
        ...
    protected:
        ...
    private:
        ...
};
```

需要注意以下几点：

* 传感器名称前必须包含字符“U”。

* GENERATED_BODY() 函数会自动生成一些内容，但要使其正常工作，您还需要在包含文件中添加以下代码行，并使用您的传感器名称。在本例中，我们使用的是 ExampleSensor：
```cpp
#include "ExampleSensor.generated.h"
```

现在我们来看看需要添加到 .h 文件中的一些主要函数。首先，请确保您的传感器有一个构造函数和一个类似这样的 InitializeSensor() 重写函数（请注意，这些函数应该放在“public”下）：

```cpp
UExampleSensor();
virtual void InitializeSensor() override;
```

接下来，在“受保护的（`protected`）”部分，你需要一个 tick 函数。这个函数定义了每次仿真周期开始时传感器的行为。它的细节可以在我们讲解“.cpp”文件时再详细介绍，但现在，只需像这样声明它：
```cpp
void TickSensorComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
```

最后，传感器必不可少的最后一个要素是“private”部分中指向父代理的指针。它存储着传感器所附加对象的引用。您只需要以下代码行：
```cpp
AActor* Parent;
```

您可能还需要添加一些辅助函数和一些类变量，但是以上内容应该是您自定义传感器所需的基本要素。

### .cpp 文件

现在您正在编辑 .cpp 文件，请确保包含匹配的头文件，以及 `holodeck.h` 和您需要的任何其他库。接下来，我们可以开始定义函数了。首先从构造函数开始。它应该类似于以下代码：
```cpp
UExampleSensor::UExampleSensor() {
    PrimaryComponentTick.bCanEverTick = true;
    SensorName = "ExampleSensor";
}
```
现在我们还需要初始化传感器，使其具备正常工作所需的所有变量。例如，我们需要确保将传感器附加到其父级，如下所示：
```cpp
void UExampleSensor::InitializeSensor() {
    Super::InitializeSensor();
    // 你需要获取指向传感器所连接对象的指针。
    Parent = this->GetAttachmentRootActor();
}
```
接下来我们可以看一下 tick 函数。它的工作原理通常是让引擎通过共享缓冲区将传感器信息返回给客户端。所以，我们让传感器每次 tick 时都返回浮点数 2.0：

```cpp
void UExampleSensor::TickSensorComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) {
    float* FloatBuffer = static_cast<float*>(Buffer);
    FloatBuffer[0] = 2.0;
}
```

这些应该是所有必要的功能，但您还需要根据 .h 文件填写其他功能。

## Python <span id="python"></span>

现在我们有了 C++ 文件，实际上不需要为传感器创建一个新的 Python 文件。相反，你需要打开 sensors.py 文件（位于 Underwater 代码库的 [client/src/holoocean/sensors.py](https://github.com/OpenHUTB/Underwater/blob/master/client/src/holoocean/sensors.py)），并为你的新传感器添加一个类。请务必按如下方式设置传感器类型，因为这在后面会很重要。
```python
class ExampleSensor(HolodeckSensor):
    sensor_type = "ExampleSensor"
```

此时，您还需要初始化所有需要初始化的内容，但所有与传感器无关的内容都可以由父类初始化。如果您有需要初始化的项目，至少您可能需要类似以下的代码：
```python
def __init__(self, client, agent_name, agent_type, name="OpticalModemSensor",  config=None):
        super(ExampleSensor, self).__init__(client, agent_name, agent_type, name=name, config=config)
```

!!! 注意
    以上内容并非总是必需的，但在某些情况下会很有用。

除此之外，还需要指定数据类型 (dtype) 和数据形状 (data_shape)。它们让客户端知道应该从缓冲区接收哪种类型的数据。回想一下，在 .cpp 文件中，我们将 tick 函数设置为返回浮点数 2.0。我们也只返回了单个浮点数，而不是多个。考虑到这一点，我们知道 dtype 应该是浮点数，data_shape 应该是 1。它应该看起来像这样：
```python
@property
def dtype(self):
    return np.float32 # 请注意，我们使用 numpy 的数据类型来获得 Python 数据的正确大小。

@property
def data_shape(self):
    return [1]
```

!!! 注意
    data_shape 可以根据需要存储多维数组，因此对于 2x2 数组，返回 [2, 2]。


## 允许你的传感器在 Underwater 中使用 <span id="allowing_your_sensor_to_be_used_in_underwater"></span>

至此，传感器的主体部分基本已经完成。但还有一些地方需要修改。首先，在 [sensors.py](https://github.com/OpenHUTB/Underwater/blob/master/client/src/holoocean/sensors.py) 文件的末尾，SensorDefinition 类中应该有一个 _sensor_keys_ 字典。你需要向该字典添加一行，以便某些函数能够根据正确的字符串获取传感器类型。在本例中，我们只需在字典末尾添加以下代码：
```python
"ExampleSensor":ExampleSensor,
```

同样，您需要找到文件 [AddSensorCommand.h](https://github.com/OpenHUTB/Underwater/blob/master/Source/Holodeck/ClientCommands/Public/AddSensorCommand.h)，并在将传感器添加到 [AddSensorCommand.cpp](https://github.com/OpenHUTB/Underwater/blob/d26be1f6b14112f69981388130332abaa3b348a3/Source/Holodeck/ClientCommands/Private/AddSensorCommand.cpp#L28) 的 SensorMap 之前，添加 #include 语句来包含您的传感器的 .h 文件，如下所示：
```cpp
{ "ExampleSensor", UExampleSensor::StaticClass() },
```

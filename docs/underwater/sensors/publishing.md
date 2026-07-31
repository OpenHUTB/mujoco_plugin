# 发布传感器数据

## 使用 LCM 发布数据

HoloOcean 支持将数据发布到**轻量级通信和编组**（Lightweight Communications and Marshalling, LCM），LCM 是一种用于在不同进程之间通信的消息系统。这允许您将传感器数据发布到 LCM 通道，这些通道可用于与其他系统通信。

LCM 配置在[场景](../usage/scenarios.md)文件中进行。LCM 将数据发布到称为提供程序的介质。提供程序可以是本地、网络、日志文件等。可以在场景文件的头部指定提供程序。有关选项，请参阅[此处](https://lcm-proj.github.io/lcm/)。如果未指定提供程序，HoloOcean 将使用默认的 LCM udqm。

```json
{
   "name": "{Scenario Name}",
   "world": "{world it is associated with}",
   "lcm_provider": "file:///home/lcm.log"
   "agents":[
      "array of agent objects"
   ]
}
```

选定服务提供者后，HoloOcean 会单独发布每个传感器。lcm_channel 参数在传感器配置中设置。如果未指定通道，则不会发布该传感器。

```json
{
   "sensor_type": "RGBCamera",
   "sensor_name": "FrontCamera",
   "lcm_channel": "CAMERA",
}
```

## 使用 ROS2 Bridge 发布数据 <span id='ros'></span>

ROS2（机器人操作系统）是一款流行的机器人开发中间件。我们开发了 ROS2 桥接包，使用户能够将 ROS2 与其他中间件系统（例如 LCM 和 HoloOcean）连接起来。这样，您就可以使用 ROS2 控制 HoloOcean 智能体，并将传感器数据发布到 ROS2 主题。

此功能专为与福森车辆动力学实现配合使用而编写。


### 安装

使用 ROS2 Bridge 需要下载一个单独的软件包。安装 HoloOcean 后，将以下仓库克隆到 ROS2 工作区：[https://github.com/byu-holoocean/holoocean-ros](https://github.com/byu-holoocean/holoocean-ros)

!!! 警告
    * 目前，ROS2 桥接器仅支持单代理场景。

    * 在虚拟环境（例如 conda）中运行 holoocean 和 ROS2 可能会导致依赖关系问题。

    * 仿真速度可能会达到极限，从而导致计时误差。

holoocean 的 ROS 工作空间与 Humble 安装的 ROS2 兼容。请按照 [ROS2 安装教程](https://docs.ros.org/en/humble/Tutorials) 进行操作。

### 使用方法

在 ROS 工作空间中构建软件包后，即可运行示例控制器：

```shell
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash

ros2 launch holoocean_main torpedo_launch.py
```

请按照 ROS2 文档构建用于控制 holoocean 环境的节点。

holoocean_main 节点：

* 订阅控制器命令

* 发布 holoocean 状态下返回的传感器数据

* 创建一个定时器来向环境发送节拍信息

holoocean 发布者将使用命名空间“holoocean”（请参阅​​ ROS 文档中关于命名空间的说明）。主题名称将与传感器的场景名称保持一致。如果没有指定名称，则主题名称将与传感器类型相同。

Holoocean接口包：

* 包含用于发布传感器数据的消息和服务

command_example节点：

* 按指定时间间隔发布随机HSD命令

* 或者发布预先编程的HSD命令序列

## 发布您自己的传感器

ROS2 桥接器可以配置为与自定义传感器配合使用。在 HoloOcean 中实现您的传感器（参见[开发传感器](../develop/sensors.md)）后，请按照以下步骤发布您的传感器数据： 

- 在 `holoocean_interfaces` 目录下创建一个 `.msg` 文件（例如 `SensorData.msg`） 

- 将 `.msg` 文件添加到 CMake 列表中（例如 `msg/SensorData.msg`） 

- 在传感器数据转换器文件中：

    * 在 convert_to_msg 函数中添加一个 elif 语句

    * 向 sensor_keys 表中添加一个键

    * 在文件的第一行导入消息对象（例如 from holoocean_interfaces.msg import SensorData）

    * 添加一个将数据编码为 ROS 消息的函数

运行以下代码以重新构建您的 ROS2 工作区：

```shell
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## 记录数据

您可以使用 `ros2bag` 记录 HoloOcean 环境中的数据。安装 `ros2bag` 后，您可以在 ros2_ws 文件夹中运行如下命令来记录传感器数据或命令：
```shell
source install/setup.bash
ros2 bag record /holoocean/desiredHSD /holoocean/RotationSensor /holoocean/LocationSensor -o /path/to/save_data
```

您可以点击[此处](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Recording-And-Playing-Back-Data/Recording-And-Playing-Back-Data.html)阅读 ROS2 文档，了解更多关于录制和回放 ROS2 bag 数据的信息。

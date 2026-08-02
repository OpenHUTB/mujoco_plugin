# 传感器

HoloOcean 传感器用于从环境中收集数据。传感器连接到代理的特定位置，称为“插槽”（有关每个代理上的插槽位置，请参阅 [HoloOcean 代理](../agents/agents.md)）。传感器将数据发布到模拟状态，该状态可以通过环境的 `.tick()` 和 `.step()` 函数的返回值来访问。

## 使用传感器

* [传感器配置](./sensor_config.md)

* [八叉树生成](../usage/octree.md)

* [发布传感器数据](./publishing.md)


## HoloOcean传感器

以下传感器的设计灵感源于真实世界的传感器，旨在收集真实数据。大多数传感器都包含用于调整噪声、偏差和其他特性的参数，以模拟真实世界传感器的行为。

### 感知传感器

* [单波束声呐](./singlebeam_sonar_sensor.md)

* [侧扫声呐](./sidescan_sonar_sensor.md)

* [成像声呐](./imaging_sonar_sensor.md)

* [剖面声呐](./profiling_sonar_sensor.md)

* [多普勒测速仪 (DVL)](./dvl_sensor.md)

* [深度传感器](./depth_sensor.md)

* [RGB 摄像机](./rgb_camera_sensor.md)

* [摄像机](./camera_sensor.md)

* [语义分割相机](./semantic_segmentation_camera_sensor.md)

* [惯性测量单元 (IMU)](./imu_sensor.md)

* [全球定位系统 (GPS)](./gps_sensor.md)

* [磁力计](./magnetometer_sensor.md)

* [测距传感器](./range_finder_sensor.md)

* [Raycast激光雷达](./raycast_lidar_sensor.md)

* [Raycast语义激光雷达传感器](./raycast_semantic_lidar_sensor.md)

* [生物量、盐度和温度（BST）传感器](./bst_sensor.md)


### 通信传感器

* [声学信标](./acoustic_beacon_sensor.md)

* [光调制解调器](./optical_modem_sensor.md)

### 状态传感器

以下传感器并非物理传感器，而是用于返回仅在仿真环境中可用的信息。它们有助于调试、收集真实数据、捕获仿真视频以及其他需要仿真信息的应用。其中一些传感器的功能有所重叠，但为了方便不同应用场景，我们仍将其列出。

视窗传感器

位置传感器

旋转传感器

方向传感器

姿态传感器

速度传感器

动力学传感器

# Mujoco 插件

该插件将 Mujoco 物理引擎与引擎集成在一起，使您可以将 Mujoco XML 文件直接加载到引擎中并运行高级物理模拟。

## 特性

- 将 Mujoco XML 文件加载到虚幻引擎中
- 运行Mujoco模拟并显示实时结果
- 支持非主要 MuJoCo 形状的程序化网格生成
- 从 MuJoCo 模型导入对象的颜色
- 支持多个同时模拟实例

## 演示

![Simulation Demo](https://cdn.loom.com/sessions/thumbnails/ec26c892b5014a03afb7d016b2d4b4d5-88ba2fce00140e4d-full-play.gif)

![Simulation Demo 2](https://cdn.loom.com/sessions/thumbnails/c750fc543f3548208ad88d14b0447251-beb5032d0c1cdf27-full-play.gif)

![Simulation Demo 3](https://cdn.loom.com/sessions/thumbnails/81d84c9a8565465199aae22d4d5e627c-47d9ea28f3266022-full-play.gif)

## 安装

1. 克隆此存储库到您的虚幻引擎项目的插件`Plugins`文件夹
2. 重新构建您的项目
3. 在项目设置中启用 Mujoco 插件

## 用法

### 基本设置

1. 在您的关卡中放置一个`MuJoCoSimulation`参与者
2. 在参与者属性中设置 XML 文件路径
3. 开始播放模式以查看模拟

### 控制

- **Z 键**: 保持则运行模拟，释放则暂停
- **R 键**: 重置模拟到初始状态
- **C 键**: 测试 Mujoco 执行器的控制（将执行器 0 设置为一个小值，可用于诸如 car.xml 之类的测试模型）

## 当前的限制

- 尚未实现纹理的支持（仅导入颜色）
- 它仍然很粗糙，并且没有针对性能进行优化

## 参考

* [MuJoCo-Unreal-Engine-Plugin](https://github.com/oneclicklabs/MuJoCo-Unreal-Engine-Plugin)
* [mujoco-unreal-plugin](https://github.com/carTloyal123/mujoco-unreal-plugin)

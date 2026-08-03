# 水下机器人开发指南

这份文档足以帮助您着手进行 HoloOcean 的开发工作。如果您发现其中有明显的遗漏或不足，欢迎提交 Issue 或 Pull Request 加以完善！

我们已力求内容详尽，但查阅 Holodeck 的文档或许能为您提供更多相关信息。

## 内容

* [入门指南](./start.md)
    * [克隆代码库](./start.md#cloning)
    * [打开并准备项目](./start.md#opening_prepping_project)
    * [配置 VSCode](./start.md#setting_up_vscode)
    * [编译](./start.md#compiling)
    * [启动游戏（实时模式）](./start.md#launching_game_live)
    * [日志记录](./start.md#logging)
    * [代码格式化](./start.md#code_formatting)
* [开发环境](./env.md)
    * [添加 Underwater 世界](./env.md#adding_underwater_worlds)
    * [内容烘焙](./env.md#cooking_content)
    * [打包 Underwater](./env.md#packing_underwater)
    * [将文件放置在安装目录中](./env.md#place_in_install_directory)
    * [关于创建环境对象和声呐的说明](./env.md#note_on_creating_environment_objects_and_sonar)
* [开发传感器](./sensors.md)
    * [C++](./sensors.md#cpp)
    * [Python](./sensors.md#python)
    * [让您的传感器在 Underwater 中可用](./sensors.md#allowing_your_sensor_to_be_used_in_underwater)
* [开发代理（Agents）](./agents.md)
    * [通用代理](./agents.md#general_agents)
    * [浮力代理](./agents.md#buoyant_agents)
* [通信协议](./semaphores.md)
    * [预备阅读材料](./semaphores.md#prerequisite_reading)
    * [holoocean 的两个部分](./semaphores.md#the_two_halves_of_holoocean)
    * [简单使用示例](./semaphores.md#simple_usage_example)
    * [第 1 部分：holoocean.make()](./semaphores.md#simple_usage_example)
    * [第 2 部分：.step()](./semaphores.md#part_2_step)
    * [备注](./semaphores.md#remarks)
* [holodeck 开发维基页面](../wiki/Holodeck-Onboarding.md) - [参考页面](https://github.com/BYU-PCCL/holodeck/wiki)

## Holodeck

* [holodeck文档](https://holodeck.readthedocs.io/en/latest/)
* [所有相关的仓库](https://bitbucket.org/frostlab/workspace/projects/FROST_CORE)

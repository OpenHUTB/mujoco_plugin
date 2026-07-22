# HoloOcean 开发指南

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
* 开发环境
    * 添加 HoloOcean 世界
    * 烘焙（Cooking）资源
    * 打包 holodeck-engine
    * 放置到安装目录
    * 关于创建环境对象和声纳（Sonar）的说明：
* 开发传感器
    * C++
    * Python
    * 让您的传感器在 HoloOcean 中可用
* 开发智能体（Agents）
    * 通用智能体
    * 浮力智能体
* 通信协议
    * 预备阅读材料
    * HoloOcean 的两个组成部分
    * 简单使用示例
    * 第 1 部分：holoocean.make()
    * 第 2 部分：.step()
    * 备注
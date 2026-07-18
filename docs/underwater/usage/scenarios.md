# 场景

什么是场景（Scenario）？

场景用于告知 HoloOcean 需要加载哪个世界、在世界中放置哪些代理（agent），以及这些代理需要配备哪些传感器。

它定义了：

* 要加载的世界

* 代理定义

    * 代理的类型

    * 代理的位置

    * 代理配备的传感器

!!! 提示
    你可以把“场景”（scenarios）想象成《光环》（Halo）中的地图或游戏模式变体：地图本身保持不变，但其中的事物以及你的目标可能会发生变化。

场景功能允许同一个世界用于多种不同的用途，并且允许您扩展和自定义我们提供的场景以满足您的需求，而无需重新打包引擎。

当您调用 `holoocean.make()` 创建环境时，您需要传入一个场景名称，例如 `holoocean.make("Pier-Hovering")`。这会告诉 HoloOcean 要加载哪个世界以及在哪里放置代理。


## 场景文件格式

场景 `.json` 文件以包的形式分发（参见[包内容](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/packages/docs/package-structure.html#package-contents)），且必须命名为 `{WorldName}-{ScenarioName}.json`。默认情况下，它们存储在 `worlds/{PackageName}` 目录下，但也支持直接从 Python 字典加载。

# 迁移至 UE4.26



## 问题

* 打开 HolodeckContent/Agents/HoveringAUV/HoveringAUV Bluieprint后报错：无法加载蓝图，因为它派生自一个无效类。请检查，确保该蓝图的父类未被删除！是否继续（可能导致编辑器崩溃）？
    * （分析）：HoveringAUV 继承自 [AHolodeckBuoyantAgent](https://github.com/OpenHUTB/hutb/blob/70c92f545785b7db243c5ecd1fbb7cb4bf5a458b/Unreal/CarlaUE4/Plugins/HoloOcean/Source/Holodeck/Agents/Public/HoveringAUV.h#L18) （又继承自 [AHoveringAUV](https://github.com/OpenHUTB/hutb/blob/70c92f545785b7db243c5ecd1fbb7cb4bf5a458b/Unreal/CarlaUE4/Plugins/HoloOcean/Source/Holodeck/Agents/Public/HoveringAUV.h#L13)）。
    * 解决办法：在虚幻编辑器的“内容浏览器”中，右键“Holodeck Content目录”，点击“修复文件中的重定向”，再次打开蓝图后不再出错。


* 将 HoveringAUV 蓝图添加到场景后，运行时候却看不到
    * 分析：AI控制器类为 HoveringAUVController，之前删除了 DefaultPlayerController.uasset
    * 分析：只是“编辑器视图专用”可视元素（按 G 会切换 Editor/ Game 视图，HoveringAUV 元素在 Game 视图下会消失）。但是鱼雷型潜水器不消失。

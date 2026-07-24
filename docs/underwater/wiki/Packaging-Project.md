虚幻引擎项目在分发前需要进行打包。此过程会生成引擎可执行文件，并将客户端启动引擎所需的所有资源打包在一起，无需通过编辑器或 Visual Studio 启动。

此过程还会编译 Holodeck 的 C++ 代码，并将 `.uasset` 文件（包括蓝图！）打包成一个大型 `.pak` 文件，并创建所需的目录结构。


## 添加 Holodeck 世界

最终的软件包将仅包含已添加到项目中的世界（在编辑器中称为“关卡”）。`holodeck-engine` 代码库仅包含示例关卡。其余世界位于 [holodeck-worlds repo](https://github.com/BYU-PCCL/holodeck-worlds) 代码库中，该代码库包含多个原版虚幻引擎项目。要将它们添加到项目中，请克隆 worlds 代码库，然后从要添加的世界中复制 `Content` 文件夹。将此文件夹粘贴到 `holodeck-engine` 代码库中，并允许其覆盖任何冲突的文件。

!!! 注意
   由于这些世界包含付费资源，因此仅供 BYU PCCL 的正式成员使用。其他用户需要使用 holodeck-engine 开发自己的世界。

后面内容参考[内容烘焙、打包、放置](../../underwater/develop/develop.md#cooking_content)
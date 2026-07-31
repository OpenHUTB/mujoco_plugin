# 添加自定义语义标签

为了让 HoloOcean 识别语义标签，关卡中的每个资源都必须添加标签并更改渲染设置。这些更改必须在虚幻引擎编辑器中完成。

!!! 注意
    HoloOcean 的语义实现使用模板值作为标签，因此标签值范围为 0-255。

为了方便操作，HoloOcean 提供了一个 Tagger 类，可以根据对象的文件夹标题自动应用标签。如果您不需要任何自定义标签，可以参考 HoloOcean 提供的标签列表（位于[可用语义标签](#semantic_labels)页面），然后继续[使用 Tagger 类自动添加标签](#automatic_labels)。

## 设置自定义标签

要向 HoloOcean 添加新标签，您需要将其添加到几个 C++ 文件中，并选择一种颜色与标签关联。

### 自定义标签

要添加自定义标签，请将标签名称添加到 Tagger.cpp 中的 GetLabelByFolderName 函数以及 ObjectLabel.h 中的 ObjectLabel 枚举中。

![](../../img/underwater/tagger_label.png)


“GetLabelByFolderName”中包含的文件夹标题示例

![](../../img/underwater/object_label.png)


“对象标签”中与文件夹标题关联的数字示例

### 更改标签颜色

要更改每个标签关联的颜色，您可以修改 engine/source/Holodeck/Utils/Public/HolooceanPallete.h 中列出的 RGB 值。


## 为资源添加标签

### 使用标签器自动添加标签 <span id='automatic_labels'></span>

要让标签器自动添加标签，您需要确保资源放置在与其标签对应的文件夹中。例如，所有放置在“Bus”文件夹中的公交车资源都将被标记为与“Bus”对应的模板值。

![](../../img/underwater/folder_structure.png)

接下来，启用标签器。在虚幻编辑器中，找到 C++ 类，然后导航到 Holodeck/Utils/Public/Tagger 目录，找到标签器的 C++ 文件。

![](../../img/underwater/tagger_location.png)

将 Tagger C++ 文件拖入关卡中。在“详细信息”面板中，单击 Tagger 并启用“应为语义分割添加标签”。

![](../../img/underwater/tagger_enabled.png)

然后，点击“触发标签对象”以自动应用标签。

![](../../img/underwater/tagger_triggered.png)


### 手动添加标签

要手动设置标签，请在“详细信息”面板中选择要添加标签的资源。在该资源下，搜索“标签”以查找演员标签。将您的标签添加到参与者标签列表中。

![](../../img/underwater/manual_tag.png)

然后，搜索“深度”，启用“渲染自定义深度通道”，并将“自定义深度模板值”设置为与您的标签关联的值。对每个要添加标签的资源执行此操作。此外，为景观启用“渲染自定义深度通道”，以确保其在深度输出中可见。

![](../../img/underwater/manual_stencil.png)


## 在编辑器中可视化标签

要可视化关卡并确保对象标签正确，请将视图模式从“点亮”更改为“自定义模板”。

![](../../img/underwater/custom_stencil_view.png)



## 可用语义标签 <span id='semantic_labels'></span>

以下是 HoloOcean 当前已实现的所有标签列表。Ocean 和 BusinessCampus 包中的每个世界都使用这些标签的子集，具体取决于该世界中的资源（请参阅 [BusinessCampus](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/packages/BusinessCampus/BusinessCampus.html#business-campus) 和 [Ocean 包](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/packages/Ocean/Ocean.html#ocean)中的世界子页面）。

## 参考

* [Adding Custom Semantic Labels](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/develop/env-docs/custom-semantics.html)
## 软件包安装位置

HoloOcean 软件包默认保存在当前用户配置文件中，具体位置取决于平台。

| 平台 | 位置 |
|-------|---------------|
| Linux | ~/.local/share/holoocean/{holoocean_version}/worlds/ |
| Windows | %USERPROFILE%\AppData\Local\holoocean\{holoocean_version}\worlds |

!!! 注意
    软件包会根据 HoloOcean 的版本保存在不同的子文件夹中。这样可以允许多个 HoloOcean 版本共存，而不会导致版本不兼容冲突。

这是 [holoocean.util.get_holoocean_path()](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/util.html#holoocean.util.get_holoocean_path) 返回的路径。

worlds 文件夹内的每个子文件夹都被视为一个单独的软件包，因此其格式必须符合[软件包内容](package_structure.md#package_contents)中描述的归档格式。

## 覆盖位置 <span id="overriding_location"></span>

您可以设置环境变量 `HOLODECKPATH` 来覆盖上述默认位置。

!!! 警告
    如果使用 `HOLODECKPATH`，它将覆盖此版本分区，因此请确保 `HOLODECKPATH` 仅指向与您的 Holodeck 版本兼容的软件包。

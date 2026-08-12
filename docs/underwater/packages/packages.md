# HoloOcean 软件包

HoloOcean 软件包包含一个或多个**世界**（地图），每个世界又包含一个或多个**场景**（同一个地图的不同配置）。场景是对世界的特定配置，包括代理、传感器和其他设置。软件包预定义了一些场景以方便使用，但用户也可以自定义场景。

Oceans 软件包是 HoloOcean 的默认软件包。它包含三个主要世界，每个世界都包含多个场景，方便使用。

BusinessCampus 软件包适用于涉及陆地车辆的应用。它包含一个楼层，内有 3 栋建筑、停车场和各种车辆。它不包含任何用于水下航行器的海洋区域。

## 包的文档

* [软件包的结构](./package_structure.md)

    * [软件包的内容](./package_structure.md#package_contents)

    * [软件包的结构](./package_structure.md#package_structure)

    * [config.json](./package_structure.md#config_json)

    * [materials.csv](./package_structure.md#materials_csv)

* [软件包的安装位置](installation.md)

    * [覆盖位置](./installation.md#overriding_location)

## HoloOcean 软件包 <span id="all_packages"></span>

* 海洋包

    * 大坝（[Dam](./Ocean/Dam/)）

        * 大坝附近悬停（[Dam-Hovering](./Ocean/Dam/Dam-Hovering.md)）

        * 大坝附近悬停的相机（[Dam-HoveringCamera](./Ocean/Dam/Dam-HoveringCamera.md)）

        * 大坝附近悬停的成像声呐（[Dam-HoveringImagingSonar](./Ocean/Dam/Dam-HoveringImagingSonar.md)）

    * 开放水域（[OpenWater](./Ocean/OpenWater/openwater.md)）

        * 开放水域悬停（[OpenWater-Hovering](./Ocean/OpenWater/OpenWater-Hovering.md)）

        * 开放水域悬停相机（[OpenWater-HoveringCamera](./Ocean/OpenWater/OpenWater-HoveringCamera.md)）

        * 开放水域悬停成像声呐（[OpenWater-HoveringImagingSonar](./Ocean/OpenWater/OpenWater-HoveringImagingSonar.md)）

        * 开放水域鱼雷型（[OpenWater-Torpedo](./Ocean/OpenWater/OpenWater-Torpedo.md)）

        * 开放水域鱼雷型剖面声呐（[OpenWater-TorpedoProfilingSonar](./Ocean/OpenWater/OpenWater-TorpedoProfilingSonar.md)）

        * 开放水域鱼雷型侧扫声呐（[OpenWater-TorpedoSidescanSonar](./Ocean/OpenWater/OpenWater-TorpedoSidescanSonar.md)）

        * 开放水域鱼雷型单波束声呐（[OpenWater-TorpedoSinglebeamSonar](./Ocean/OpenWater/OpenWater-TorpedoSinglebeamSonar.md)）

    * 码头港口（[PierHarbor](./Ocean/PierHarbor/pierharbor.md)）

        * 码头港口悬停（[PierHarbor-Hovering](./Ocean/PierHarbor/PierHarbor-Hovering.md)）

        * 码头港口悬停的相机（[PierHarbor-HoveringCamera](./Ocean/PierHarbor/PierHarbor-HoveringCamera.md)）

        * 码头港口悬停的成像声呐（[PierHarbor-HoveringImagingSonar](./Ocean/PierHarbor/PierHarbor-HoveringImagingSonar.md)）

        * 码头港口鱼雷型机器人（[PierHarbor-Torpedo](./Ocean/PierHarbor/PierHarbor-Torpedo.md)）

    * 房间（[Rooms](./Ocean/Rooms/rooms.md)）

        * 房间数据生成器（[Rooms-DataGen](./Ocean/Rooms/Rooms-DataGen.md)）

    * 简易水下（[SimpleUnderwater](./Ocean/SimpleUnderwater/simpleunderwater.md)）

        * 简易水下悬停（[SimpleUnderwater-Hovering](./Ocean/SimpleUnderwater/SimpleUnderwater-Hovering.md)）

        * 简易水下鱼雷型机器人（[SimpleUnderwater-Torpedo](./Ocean/SimpleUnderwater/SimpleUnderwater-Torpedo.md)）

* [商业园区 BusinessCampus](./business_campus.md)







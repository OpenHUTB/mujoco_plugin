# 软件包结构

holoOcean 软件包是一个 `.zip` 文件，其中包含 [holoocean-engine](https://github.com/OpenHUTB/Underwater) 的构建版本，该版本包含世界以及这些世界的[场景](../usage/scenarios.md#scenarios)。


软件包文件是平台特定的，因为它包含 HoloOcean 的编译二进制文件。

## 软件包的内容 <span id="package_contents"></span>

`.zip` 文件必须包含以下元素：

1.[holoocean-engine](https://github.com/OpenHUTB/Underwater) 的构建版本

2.定义压缩包中包含的世界的 `config.json` 文件

3.这些世界的场景配置

## 软件包结构 <span id="package_structure"></span>

package.zip 文件根目录下包含一个 `config.json` 文件，以及软件包中包含的每个世界的全部场景文件。场景文件必须遵循 `{WorldName}-{ScenarioName}.json` 的格式。

```json
+package.zip
+-- config.json
+-- materials.csv
+-- WorldName-ScenarioName.json
+-- LinuxNoEditor
    + UE4 build output
```

## config.json <span id="config_json"></span>

此配置文件包含包级别的配置。以下是配置文件应遵循的格式：

config.json:
```json
{
   "name": "{package_name}",
   "platform": "{Linux | Windows}",
   "version": "{package_version}",
   "path" : "{path to binary within the archive}",
   "worlds": [
      {
         "name": "{world_name}",
         "pre_start_steps": 2,
         "env_min": [-10, -10, -10],
         "env_max": [10, 10, 10]
      }
   ]
}
```

世界对象的“pre_start_steps”属性定义了在开始模拟之前应该经过多少个节拍，以应对世界对象的特殊性。

`env_min`/`env_max` 属性用于设置环境的上限/下限，在为声呐传感器创建八叉树时会用到。

## materials.csv <span id="materials_csv"></span>

此文件包含环境中各种材料的声学特性，用于计算声呐图像。以下是配置文件应遵循的格式：

```csv
Material, Density kg/m^3, Speed of Sound m/s
M_Landscape, 3200, 4500
M_URockA, 3000, 5000
```

每次模拟开始时，都会读取此文件，以便在无需重新编译整个虚幻引擎二进制文件的情况下对其进行编辑。第一行会被忽略，仅用于编辑文件时作为参考。第一列是UE4中的材质名称，第二列是材质密度（单位为kg/m³），第三列是声速（单位为m/s）。这些数据用于计算环境中各种材质的声强。

!!! 注意
    如果在环境中发现的材质未包含在.csv文件中，则会将其添加到.csv文件中，并默认使用10,000的密度和声速（这将导致完全声反射）。

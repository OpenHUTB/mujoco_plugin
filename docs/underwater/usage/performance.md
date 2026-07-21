# 提升 HoloOcean 性能

HoloOcean 默认性能相当不错，但您也可以牺牲一些功能来提高帧率。

* __[RGBCamera](#rgbcamera)__
    * __[禁用 RGBCamera](#disabling_the_rgbcamera)__
    * __[降低 RGBCamera 分辨率](#lowering_the_rgbcamera_resolution)__
    * __[调整每次拍摄的节拍数](#changing_ticks_per_capture)__
* __[声呐传感器](#sonar_sensors)__
    * __[降低八叉树分辨率](#lowering_octree_resolution)__
    * __[更改每次捕获的帧数](#changing_ticks_per_capture)__
* __[禁用视窗渲染](#disable_viewport_rendering)__
* __[更改渲染质量](#change_render_quality)__



## RGBCamera <span id="rgbcamera"></span>

要显著提升性能，最有效的方法莫过于禁用 `RGBCamera`。每帧都渲染摄像机会导致引擎渲染代码深处发生上下文切换，从而造成严重的性能损失。

此图表显示了调整 RGBCamera 设置后性能的提升或损失（左列为帧时间，单位为毫秒）。请注意，所有测试均在原版 Holodeck 中进行，但结果应该相同。

| 分辨率  | UrbanCity | | MazeWorld | | MazeWorld | |
|-------|--------| ---|--------|---|--------|---|
| 没有相机     | 8.55 ms | 117 fps  | 4.69 ms | 213 fps  |  2.47 ms | 405 fps
| 64     | 17 ms | 59 fps  | 11 ms | 91 fps  |  4.87 ms | 205 fps
| 128     | 20 ms | 50 fps  | 11.6 ms | 86 fps  |  5.59 ms | 179 fps
| 256     | 22 ms | 45 fps  | 14.71 ms | 68 fps  |  9.02 ms | 111 fps
| 512     | 35 ms | 29 fps  | 30.8 ms | 32 fps  |  24.81 ms | 40 fps
| 1024     | 89 ms | 11 fps  | 84.2 ms | 12 fps  |  94.55 ms | 11 fps
| 2048     | 410 ms | 2 fps  | 383 ms | 3 fps  |  366 ms | 3 fps


### 禁用 `RGBCamera` <span id="disabling_the_rgbcamera"></span>

从您正在使用的场景配置文件中移除 `RGBCamera` 条目。

请参阅[自定义场景配置](../example/custom_scenarios.md#custom-scenarios)。


### 降低 `RGBCamera` 分辨率 <span id="lowering_the_rgbcamera_resolution"></span> 

降低 `RGBCamera` 的分辨率也有助于提高速度。创建一个[自定义场景](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/usage/examples/custom-scenarios.html#custom-scenarios)，并在 RGBCamera 的[配置块](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/usage/scenarios.html#configuration-block)中设置 `CaptureWidth` 和 `CaptureHeight` 参数。

更多详情请参见 [RGBCamera](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.RGBCamera)。



### 调整每次拍摄的节拍数 <span id="changing_ticks_per_capture"></span>

可以降低相机采样率来提高平均每秒帧数。有关更多信息，请参阅[传感器对象](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/usage/scenarios.html#configure-sensors)和`Hz`参数。



## 声呐传感器 <span id="sonar_sensors"></span> 

声呐传感器也会消耗大量性能资源。有很多方法可以帮助提高它们的性能。


### 降低八叉树分辨率 <span id="lowering_octree_resolution"></span>  

八叉树分辨率对声呐性能影响很大。`octree_min` 值越高，需要搜索的叶子节点就越少，运行速度也就越快。但这会影响图像质量，尤其是在近距离探测时。如果大多数被探测目标距离较远，则可以安全地大幅提高此参数。

有关如何操作的详细信息，请参阅[配置八叉树](./scenarios.md#configure_octree)。

### 更改每次捕获的帧数 <span id="changing_ticks_per_capture"></span>  

可以降低声呐采样率以提高平均每秒帧数。有关更多信息，请参阅[传感器对象](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/usage/scenarios.html#configure-sensors)和`Hz`参数。


## 禁用视窗渲染 <span id="disable_viewport_rendering"></span>

训练过程中，视窗的渲染可能并非必要。您可以使用 [should_render_viewport()](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.should_render_viewport) 方法禁用视窗渲染。

在较低的 `RGBCamera` 分辨率下，帧时间预计可减少约 40%。

## 改变渲染质量 <span id="change_render_quality"></span> 

您可以调整 HoloOcean 的渲染质量，以降低（或提高）渲染质量来提升性能。请参阅 [set_render_quality()](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.set_render_quality) 方法。

以下是不同渲染质量下帧时间（以毫秒为单位）的对比。

| 质量  | MazeWorld | UrbanCity | AndroidPlayground |
|-------|--------|--------|-----|
| `0`     | 10.34  | 12.33  | 6.63  |
| `1`     | 10.53  | 15.06  | 6.84  |
| `2`     | 14.81  | 19.19  | 8.66  |
| `3`     | 15.58  | 21.78  | 9.2  |

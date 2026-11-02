# 天气控制器

HoloOcean 世界拥有可配置的天气设置，既可通过​​场景设置，也可通过编程实时控制。天气仅为视觉效果，不会影响载具移动或传感器数据输入。

## 天气选项

### 类型

![](../../img/underwater/weather.gif)


HoloOcean 世界有三种天气类型：`0 - 晴天`，`1 - 多云`，`2 - 雨天`。

### 在一个场景中

```json
config = {
   "name": "weather_test",
   ...
   "weather": {
      "type": 0
   }
}
```

### 以编程方式
```python
with holoocean.make("...") as env:
   while True:
      env.change_weather(0)
      ...
      env.tick()
```

## 降雨参数

在雨天模拟中，您可以以编程方式自定义雨滴的速度和生成速率（雨滴数量）。此功能仅在模拟期间可用，无法通过场景配置实现。

![](../../img/underwater/weather.gif)


### 速度

雨滴速度由三个分量定义：`x`、`y` 和 `z`，分别对应于沿每个轴的运动。这些分量可用于模拟风：

* **x** 分量：控制相对于世界坐标系的水平倾斜（左/右）。

* **y** 分量：控制相对于世界坐标系的水平倾斜（前/后）。

* **z** 分量：控制垂直速度。该值必须为负值才能使雨滴向下落。正的 `z` 值会使雨滴上升，从而使载具周围的雨滴不可见。

一个适合模拟轻微倾斜雨滴的初始值是：
```python
velocity = (0, 400, -1000)
```

### 生成速率

此参数定义生成的雨滴粒子数量。为了获得逼真的雨效，典型值范围为 1000 到 4000。您可以根据需要调整此值以模拟小雨或大雨。

!!警告
    将生成速率设置得过高（例如，数百万）可能会严重影响性能或导致模拟崩溃。

### 用法

要设置雨滴参数，请使用以下命令：
```python
set_rain_parameters(vel_x, vel_y, vel_z, spawn_rate)
```
如果未明确设置，则默认降雨设置如下：
```python
velocity = (0, 300, -1000)
spawn_rate = 3000
```

### 以编程方式
```python
with holoocean.make("...") as env:
   while True:
      env.change_weather(2)  # 在此处或在配置中将天气设置为下雨
      env.set_rain_parameters(0,400,-1000, 2000)  # 自定义降雨行为
      ...
      env.tick()
```

!!! 注意
    有关如何使用这些命令的更多信息，请参阅 API 文档：[ChangeWeatherCommand](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/holoocean/commands.html#holoocean.command.ChangeWeatherCommand) 和 [SetRainParametersCommand](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/holoocean/commands.html#holoocean.command.SetRainParametersCommand) 。
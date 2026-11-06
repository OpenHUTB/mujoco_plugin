# 手电筒

HoloOcean 的载具内置一个或多个手电筒，**默认情况下处于关闭状态**。

## 位置
手电筒的位置和数量因载具而异：

* BlueROV2 手电筒

* 悬停式 AUV 手电筒

* CougUV 手电筒

* 鱼雷式 AUV 手电筒

* 水面舰艇手电筒

## 命令

![](../../img/underwater/flashlights_hov.gif)

有两种命令可用于控制手电筒：`TurnOnFlashlightCommand` 和 `TurnOffFlashlightCommand`。`TurnOnFlashlightCommand` 允许您选择性地自定义多个参数，例如：亮度、光束宽度、位置、旋转和颜色。

!!! 注意
    手电筒颜色值使用 **0.0 – 1.0** 范围内的归一化 RGB 值，而非标准的 0 – 255 范围。

有关完整的使用详情，请参阅 Python API 文档：

* [TurnOnFlashlightCommand](https://byu-holoocean.github.io/holoocean-docs/develop/holoocean/commands.html#holoocean.command.TurnOnFlashlightCommand)

* [TurnOffFlashlightCommand](https://byu-holoocean.github.io/holoocean-docs/develop/holoocean/commands.html#holoocean.command.TurnOffFlashlightCommand)

## 使用示例（适用于 HoveringAUV/BlueROV2）

### 在以下场景中

```json
config = {
    "name": "test_flashlight",
    "main_agent": "auv0",
    ...
    "flashlight":[
        {
            "flashlight_name": "flashlight1",
            "intensity": 10000,
            "beam_width": 60,
        },
        {
            "flashlight_name": "flashlight4",
            "intensity": 10000,
            "color_G": 0,
            "angle_pitch": -30,
        },
    ]
}
```

### 以编程方式

```json
with holoocean.make("...") as env:
    while True:
        if 'o' in pressed_keys:
            env.turn_on_flashlight("flashlight1")
            env.turn_on_flashlight("flashlight4", beam_width=80, color_B=0) # 打开手电筒 4，光束宽度为 80 度，并将蓝色分量调至零。

        if 'p' in pressed_keys:
            env.turn_off_flashlight("flashlight1")
            env.turn_off_flashlight("flashlight4")

        env.tick()
```

!!! 注意
    调用 `turn_on_flashlight("flashlight_number")` 函数时，如果未指定其他参数，系统会首先查找场景配置中定义的值。如果手电筒已在场景配置中配置，则这些值将成为其默认值。只有当未找到任何配置值时，该命令才会回退到其内置的默认参数。
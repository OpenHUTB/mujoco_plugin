# 视窗传感器

捕获视窗所显示的内容（即仿真窗口显示的内容）。它比相机速度更快，但只能捕获一个视窗。使用 [move_viewport()](https://openhutb.github.io/doc/python_api/#move_viewport) 函数移动视窗可能很有用。请注意，配置中设置的尺寸必须与视窗的尺寸匹配。默认设置与默认视窗分辨率匹配。

有关 Python API，请参阅 [ViewportCapture](https://openhutb.github.io/doc/python_api/#holoocean.sensors.ViewportCapture)。

传感器定义示例：
```json
{
    "sensor_type": "ViewportCapture",
    "socket": "Viewport",
    "configuration": {
        "Width": 1280,
        "Height": 7200,
    }
}
```
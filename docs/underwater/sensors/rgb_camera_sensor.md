# RGB 相机

从相机捕获 RGBA 图像。

请参阅[可视化 RGBCamera 输出](../example/camera.md)了解如何使用此传感器的示例。

请参阅 RGBCamera 的 Python API。传感器定义示例（来自 HoveringAUV）：

```json
{
    "sensor_type": "RGBCamera",
    "sensor_name": "RightCamera",
    "socket": "CameraRightSocket",
    "Hz": 5,
    "configuration": {
        "CaptureWidth": 512,
        "CaptureHeight": 512
    }
}
```
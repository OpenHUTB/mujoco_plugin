# 传感器配置

传感器定义在代理对象的 sensors 数组中。每个传感器都使用列表中的一个新字典进行定义。

```json
"sensors":[
   {
      "sensor_name": "FrontCamera",
      "sensor_type": "RGBCamera",
      "socket": "socket name",
      "location": [1.0, 2.0, 3.0],
      "rotation": [1.0, 2.0, 3.0],
      "Hz": 5,
      "lcm_channel": "channel_name",
      "ros_publish": "False",
      "configuration": {
         "array of sensor configurations"
      }
   }
]
```

## 传感器放置位置 <span id='sockets'></span>

传感器放置位置可以通过以下几种方式定义：

**1.提供一个插槽名称**

这将把传感器放置在指定的插槽中。
```json
{
   "sensor_type": "RGBCamera",
   "socket": "CameraSocket"
}
```

**2.提供插槽、位置和/或旋转参数**

传感器将根据指定的位置和旋转参数相对于插槽进行偏移放置。旋转参数为`[roll, pitch, yaw]`度，绕XYZ固定轴旋转，即 \(R_z R_y R_x\) 。
```json
{
   "sensor_type": "RGBCamera",
   "socket": "CameraSocket"
   "location": [1.0, 2.0, 3.0],
   "rotation": [1.0, 2.0, 3.0],
}
```

**3.只需提供位置和/或旋转角度即可**

传感器将放置在给定的坐标处，相对于代理的根节点进行偏移。

```json
{
   "sensor_type": "RGBCamera",
   "location": [1.0, 2.0, 3.0],
   "rotation": [1.0, 2.0, 3.0]
}
```

## 传感器采样率

传感器将以指定的采样率（单位为 `Hz`）进行采样。请注意，此值必须小于 `ticks_per_sec`，并且最好是 `ticks_per_sec` 的倍数。有关 `ticks_per_sec` 的更多信息，请参阅[帧速率](../usage/scenarios.md#configure_framerate)部分。

```json
{
   "sensor_type": "RGBCamera",
   "Hz": 20
}
```

## 发布消息

HoloOcean 支持向 LCM 发布传感器消息和数据。此外，还提供 HoloOcean-ROS2 桥接器包。

要向 LCM 发布传感器数据，请指定要发布的类型和要发布的通道：

```json
{
   "sensor_type": "RGBCamera",
   "lcm_channel": "CAMERA"
}
```
要将传感器数据发布到 ROS2，请将 ros_publish 设置为 True：

```json
{
   "sensor_type": "RGBCamera",
   "ros_publish": "True"
}
```

有关 ROS2 桥接器的更多信息，请参阅[使用 ROS2 Bridge 发布数据](./publishing.md#ros)。

## 配置块

配置块的内容与传感器密切相关。配置块会原封不动地传递给传感器，由传感器进行解析。


例如，[RGBCamera](https://byu-holoocean.github.io/holoocean-docs/v2.0.0/holoocean/sensors.html#holoocean.sensors.RGBCamera) 的文档字符串指出它接受 `CaptureWidth` 和 `CaptureHeight` 参数，因此一个示例传感器配置如下：
```json
"sensors": [
   {
      "sensor_name": "RBGCamera",
      "sensor_type": "RGBCamera",
      "socket": "CameraSocket",
      "configuration": {
         "CaptureHeight": 1920,
         "CaptureWidth": 1080
      }
   }
]
```





# 潮汐控制器

HoloOcean 世界拥有可配置的潮汐设置，既可以通过场景进行配置，也可以在模拟过程中通过命令实时配置。

![](../../img/underwater/tidesinaction.gif)

## 潮汐选项

Holoocean 世界拥有潮汐配置和命令。您可以设置世界中的固定潮汐周期，也可以使用 `env.tide()` 命令随时设置或调整潮汐。通过该命令，您可以将 `absolute` 参数设置为 `True` 来设置潮汐水位，也可以将 `absolute` 参数设置为 `False` 来偏移当前潮汐水位。

### 场景示例

振幅单位为厘米，频率单位为节拍数。
```json
config = {
   "tide_cycle":{
         "active": True,
         "amplitude": ###,
         "frequency": ###,
    },
}
```

### 以编程方式

使用命令。

```python
env = holoocean.make("...")
# 这将使潮位达到1米
env.tide(1, True)
# 这将使潮汐相对于当前位置向-2米调整，即潮汐位置变为-1米
env.tide(-2, False)
```

例如，按下按钮使潮水上升 10 厘米。

```python
with holoocean.make("...") as env:
   while True:
      if 't' in pressed_keys:
         # 潮水上涨10厘米
         env.tide(0.1, False)
```

!!! 注意
    有关如何使用此命令的更多信息，请参阅 API 文档：[TideCommand](https://openhutb.github.io/doc/python_api/#holoocean.command.TideCommand)。


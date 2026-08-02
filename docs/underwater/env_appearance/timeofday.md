# 时间控制器

HoloOcean 世界支持可配置的时间设置，可通过场景或以编程方式实时设置。此外，还可在场景中定义日期循环频率。

![](../../img/underwater/time_cycle.gif)


## 时间

时间可以使用介于 0 和 24 之间的浮点数设置，代表所需的小时数。例如，13.5 对应下午 1:30。本系统假设一个简化的昼夜循环：日出时间为上午 6:00，日落时间为下午 6:00。

### 在某个场景中
```json
config = {
   "name": "time_test",
   ...
   "time_cycle": {
      "active": True,
      "hour": 12
   }
}
```

### 以编程方式

```python
with holoocean.make("...") as env:
   while True:
      env.change_time_of_day(12) # 设定时间为中午12点
      ...
      env.tick()
```

## 日周期

日周期的持续时间以模拟时钟周期数 (ticks_per_sec) 为单位定义。例如，如果 ticks_per_sec = 60 且 time_cycle 频率设置为 600，则完整的日周期大约持续 10 秒（600 个时钟周期 ÷ 60 个时钟周期/秒）。

### 在场景中
```json
config = {
   "name": "time_cycle_test",
   ...
   "time_cycle": {
      "active": True,
      "frequency": 600
   }
}
```

!!! 注意
    有关如何使用此命令的更多信息，请参阅 API 文档：[ChangeTimeOfDayCommand](https://byu-holoocean.github.io/holoocean-docs/v2.3.0/holoocean/commands.html#holoocean.command.ChangeTimeOfDayCommand)。



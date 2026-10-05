# 交互式波浪

本示例演示如何在 HoloOcean 仿真过程中生成并动态切换波浪。在仿真运行时改变波浪并同时控制载具是很有用的功能，本脚本展示了如何结合场景配置、用户按键和波浪命令来实现这一点。

场景配置中的 `"fft_waves"` 字段是生成波浪的必要条件，还可以在此添加更多参数（详见 [FFT 水波控制器](../env_appearance/waves.md)）。运行后按数字键 `0`-`6` 可实时切换海况等级，按 `i`/`k` 控制前进与后退，`j`/`l` 控制左转与右转，按 `-` 键退出。

```python
import holoocean
import numpy as np
from pynput import keyboard

config = {
    "name": "test",
    "world": "OpenWater",
    "package_name": "Ocean",
    "main_agent": "sv0",
    "ticks_per_sec": 60,
    "frames_per_sec": 60,
    # This is required to initiate waves, however more parameters could be added.
    "fft_waves": {"sea_state": 0},
    "agents": [
        {
            "agent_name": "sv0",
            "agent_type": "SurfaceVessel",
            "sensors": [],
            "control_scheme": 0,
            "location": [10, 10, -5],
            "rotation": [0, 0, 0],
        },
    ],
}

pressed_keys = list()

def on_press(key):
    global pressed_keys
    if hasattr(key, "char"):
        pressed_keys.append(key.char)
        pressed_keys = list(set(pressed_keys))

def on_release(key):
    global pressed_keys
    if hasattr(key, "char"):
        pressed_keys.remove(key.char)

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

force = 1000
def parse_keys(keys, val):
    command = np.zeros(2)
    if "i" in keys:  # forward thrust
        command[:] += val
    if "k" in keys:  # backward thrust
        command[:] -= val
    if "j" in keys:  # roll CCW
        command[0] -= val
        command[1] += val
    if "l" in keys:  # roll CW
        command[0] += val
        command[1] -= val

    return command

with holoocean.make(scenario_cfg=config) as env:
    while True:
        if "-" in pressed_keys:
            break
        if "0" in pressed_keys:
            env.fftwaves.fft_sea_state(0)
        if "1" in pressed_keys:
            env.fftwaves.fft_sea_state(1)
        if "2" in pressed_keys:
            env.fftwaves.fft_sea_state(2)
        if "3" in pressed_keys:
            env.fftwaves.fft_sea_state(3)
        if "4" in pressed_keys:
            env.fftwaves.fft_sea_state(4)
        if "5" in pressed_keys:
            env.fftwaves.fft_sea_state(5)
        if "6" in pressed_keys:
            env.fftwaves.fft_sea_state(6)

        command = parse_keys(pressed_keys, force)
        env.act("sv0", command)
        state = env.tick()
```

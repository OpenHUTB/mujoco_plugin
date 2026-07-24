# 手动控制 [controller.py](https://github.com/OpenHUTB/mujoco_plugin/blob/main/src/underwater/holo_ocean/controller.py)

我们发现 pynput 是一个很好的库，用于向代理发送键盘命令以进行手动控制。

这是一个使用以下键盘快捷键控制 [HovingAUV](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/agents/hovering-auv-agent.html#hovering-auv-agent) 的示例。

![](../../img/underwater/controller.jpg)

| 键 | 前进键 | 后退键 |
|-------|---------------|-----------|
| 上/下 | `i` | `k` |
| 左/右偏航 | `j` | `l` |
| 前进/后退 | `w` | `s` |
| 左/右扫 | `w` | `s` |

```python
import holoocean
import numpy as np
from pynput import keyboard

pressed_keys = list()
force = 25

def on_press(key):
    global pressed_keys
    if hasattr(key, 'char'):
        pressed_keys.append(key.char)
        pressed_keys = list(set(pressed_keys))

def on_release(key):
    global pressed_keys
    if hasattr(key, 'char'):
        pressed_keys.remove(key.char)

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

def parse_keys(keys, val):
    command = np.zeros(8)
    if 'i' in keys:
        command[0:4] += val
    if 'k' in keys:
        command[0:4] -= val
    if 'j' in keys:
        command[[4,7]] += val
        command[[5,6]] -= val
    if 'l' in keys:
        command[[4,7]] -= val
        command[[5,6]] += val

    if 'w' in keys:
        command[4:8] += val
    if 's' in keys:
        command[4:8] -= val
    if 'a' in keys:
        command[[4,6]] += val
        command[[5,7]] -= val
    if 'd' in keys:
        command[[4,6]] -= val
        command[[5,7]] += val

    return command

with holoocean.make("Dam-Hovering") as env:
    while True:
        if 'q' in pressed_keys:
            break
        command = parse_keys(pressed_keys, force)

        # 发送到 holoocean
        env.act("auv0", command)
        state = env.tick()
```


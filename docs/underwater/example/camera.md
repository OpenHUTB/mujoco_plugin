# 可视化 RGB 相机（RGBCamera）输出

在代理训练时显示RGB相机的输出可能很有用。下面是一个使用 `cv2` 库的示例。

当窗口打开时，按 `0` 键勾选环境并显示下一个窗口。

```python
import holoocean, cv2

env = holoocean.make("Dam-HoveringCamera")
env.act('auv0', [10,10,10,10,0,0,0,0])

for _ in range(200):
    state = env.tick()

    if "LeftCamera" in state:
        pixels = state["LeftCamera"]
        cv2.namedWindow("Camera Output")
        cv2.imshow("Camera Output", pixels[:, :, 0:3])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
```


## 参考

* [Visualizing RGBCamera Output](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/usage/examples/camera.html)
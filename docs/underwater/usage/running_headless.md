# 使用 HoloOcean 无头模式

在 Linux 系统上，HoloOcean 可以无头运行，无需打开视窗。这可以自动完成，也可以手动强制隐藏。


## 无头模式与禁用视窗渲染 <span id="headless_mode_vs_disabling_viewport_rendering"></span>

这是两个不同的功能。

**禁用视窗渲染**是指调用 HoloOceanEnvironment 的 [should_render_viewport()](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.should_render_viewport) 方法。此操作可在运行时执行。此时，视窗中渲染的图像看起来会像冻结了一样，但 RGBCamera 和其他传感器仍会正确更新。

**无头模式**是指视窗窗口不显示。如果手动启用无头模式，则也会自动禁用视窗渲染。


## 强制启用无头模式 <span id="forcing_headless_mode"></span>

在 holoocean.make() 中，将 `show_viewport` 设置为 `False`。

!!! 注意
    这也会禁用视窗渲染 (`should_render_viewport()`)。

    如果您仍然希望在无头模式下渲染视窗（例如，用于 [ViewportCapture](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/sensors.html#holoocean.sensors.ViewportCapture) ），只需将 [should_render_viewport](https://byu-holoocean.github.io/holoocean-docs/UE4.27_archival_develop/holoocean/environments.html#holoocean.environments.HoloOceanEnvironment.should_render_viewport) 设置为 `True` 即可。


## 自动无头模式  <span id="automatic_headless_mode"></span>

如果引擎未检测到 `DISPLAY` 环境变量，则不会打开窗口。如果 HoloOcean 通过 SSH 会话运行，则会自动执行此操作。

!!! 注意
    这不会禁用视窗渲染。


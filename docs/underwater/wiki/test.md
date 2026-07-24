# Holodeck 集成测试

## 前提条件

`pip install tox`

### 什么是 tox

Tox 会自动创建一个虚拟环境，并根据 `config.py` 中指定的依赖项进行配置，然后针对该虚拟环境运行 `pytest`。这使得我们可以像测试安装在全新机器上的软件包一样测试 Holodeck。

## 我只想对正在使用的代码进行测试

### 安装 Holodeck 的开发版本

你可以使用 pip 安装 `Holodeck` 模块的“可编辑”模式——这意味着你可以从任何位置`import holodeck`，它将使用 [src/holodeck](https://github.com/BYU-PCCL/holodeck/tree/master/src/holodeck) 目录下的代码。


首先，卸载你已安装的任何 Holodeck 版本：`pip uninstall holodeck`

然后，从该仓库的根目录运行 `pip install --editable .`

打开 Python 终端，确保导入 Holodeck `import holodeck` 并运行 `holodeck.util.get_holodeck_version()` 后输出 `X.Y.Zdev`


### 运行 pytest

安装好 Holodeck 的开发版本后，从该仓库的根目录运行 `pytest`。你应该会看到类似这样的输出。

```
============================= test session starts =============================
platform win32 -- Python 3.7.1, pytest-4.5.0, py-1.8.0, pluggy-0.12.0
cachedir: .tox\py37\.pytest_cache
rootdir: C:\Users\jayde\Documents\holodeck, inifile: pytest.ini
collected 28 items

tests\scenarios\test_loading_scenarios.py ..............           [ 50%]
tests\scenarios\test_reset.py .......                              [ 75%]
tests\scenarios\test_rgb_camera_not_null.py .......                [100%]

========================= 28 passed in 131.77 seconds =========================
___________________________________ summary ___________________________________
  py37: commands succeeded
  congratulations :)
```

在 PyCharm 中，你也可以右键点击测试用例，单独运行/调试它。

## 运行 Tox

只需在本仓库根目录下输入 `tox` 即可。

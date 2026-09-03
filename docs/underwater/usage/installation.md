# 安装

HoloOcean 的安装分为两部分：首先安装 Python 客户端库（`holoocean`），随后由该库下载“世界”包（world packages）。Python 部分非常小巧，而“世界”包（即“二进制文件”）的体积则可能达到数 GB。

备用下载地址：水下机器人相关文件位于[网盘](https://pan.baidu.com/s/1n2fJvWff4pbtMe97GOqtvQ?pwd=hutb)中的`software/underwater/`，其中`Linux_1.0.0.zip`为Linux平台下的UE4版本，[Linux_2.3.0.zip](https://robots.et.byu.edu/holo/Ocean/v2.3.0/Linux.zip)为Linux平台下的UE5版本，`Windows.zip`为Windows下UE4的版本。


## 要求

* \(\geq\) Python 3.7 （Python 3.7 成功，Python 3.10 报错）

* 数 GB 存储空间

* pip3

* 64 位 Linux 或 Windows

* 建议配备性能良好的 GPU

* Linux 环境：OpenGL 3+、gcc（至少需安装 build-essential 软件包）

* 对于 Linux 上的 build-essential 软件包，您可以运行以下控制台命令：

```shell
sudo apt install build-essential
```

## 稳定安装

根据 Unreal Engine 的最终用户许可协议（EULA），我们无法再通过 PyPI 提供 HoloOcean（PyPi 不能包含引擎工具，但可以包含引擎二进制）。不过，HoloOcean 的安装依然相当简单，只是需要多几个步骤。

首先，请按照此处的步骤将您的 GitHub 账户[与 Unreal 关联](https://www.unrealengine.com/en-US/ue-on-github)。注意：账户页面可能已更新，目前的关联选项标签为“Apps and Accounts”（应用与账户）。此过程需要您接受其 EULA。

!!! 注意
    Epic Games 正在调整其 GitHub 组织结构。如果您是在 6 月 10 日之后关联的账户，且处于其镜像组织（mirror organization）中，则相应的链接应为 [byu-holoocean-mirror/HoloOcean](github.com/byu-holoocean-mirror/HoloOcean)，对应的 git clone 命令为
    ```shell
    git clone git@github.com:byu-holoocean-mirror/HoloOcean.git holoocean
    ```

如果您遇到任何其他问题，请告知我们。

接下来，请下载或克隆 [byu-holoocean/HoloOcean](https://github.com/byu-holoocean/HoloOcean)。

!!! 注意
    如果遇到“Page Not Found”（页面未找到）错误，这是因为您尚未将 GitHub 账户与 Epic Games 账户关联。请参考上一段内容，完成账户关联。

我们建议按照示例代码中的做法，使用小写名称来克隆仓库，具体如下：
```shell
git clone git@github.com:byu-holoocean/HoloOcean.git holoocean
```
在克隆的仓库中，执行以下操作：
```shell
cd holoocean/client
pip install .
```

!!! 注意
    如果安装时出现报错信息：WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'ProxyError('Cannot connect to proxy.', OSError(0, 'Error'))': /simple/setuptools/，则关闭本地代理在进行安装

接下来，若要安装 oceans 软件包的最新版本，请通过输入以下内容打开 Python shell 并按回车键。
```shell
python
```

然后在该 Python shell 中运行 Python 命令。
```python
import holoocean
holoocean.install("Ocean")
```
或者作为一条单独的控制台命令，
```shell
python -c `import holoocean; holoocean.install("Ocean")`
```

!!! 注意
    Windows 系统上 `pywin32` 包存在一个偶尔发生的 bug。如果您看到“ImportError: DLL load failed while importing win32event: The specified module could not be found.”的错误信息，可以通过运行 `pip install pywin32==225` 命令来修复。


## Beta 版安装

!!! 注意
    如果您之前已安装过 holoocean，之后才切换到 develop 分支或其他分支，则需要先运行 `holoocean.remove("Ocean")` 卸载该二进制文件，然后再继续操作。否则可能会导致无法预知的行为。

要安装 develop 分支，只需运行
```shell
git clone https://github.com/byu-holoocean/HoloOcean.
cd holoocean/client
git checkout develop
pip install .
```

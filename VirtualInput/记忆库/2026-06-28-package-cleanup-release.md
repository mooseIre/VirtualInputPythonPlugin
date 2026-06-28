# 2026-06-28 发布包、清理与卸载验证

## 本轮目标

- 清理过程文件。
- 将源码、记忆库、Python 调用脚本提交到根仓库 Git。
- 生成可交付 zip 到项目根目录。
- 发布包内包含驱动文件、Python 调用脚本、安装/卸载 BAT、测试模式开关。
- 验证安装和卸载脚本，卸载必须清理设备、Driver Store 包和测试证书。

## 发布包

发布目录：

```text
C:\Users\moose\Desktop\RF4-Image-Assistant\InputBridge-Package
```

zip：

```text
C:\Users\moose\Desktop\RF4-Image-Assistant\InputBridge-Package.zip
```

发布包内容：

- `driver/InputBridge.sys`
- `driver/InputBridge.inf`
- `driver/InputBridge.cat`
- `driver/InputBridgeTest.cer`
- `python/virtual_input.py`
- `python/example.py`
- `tools/devcon.exe`
- `manage-driver.bat`
- `install-driver.bat`
- `uninstall-driver.bat`
- `uninstall-clean.ps1`
- `smoke_test.py`
- `README.md`

## 脚本能力

`manage-driver.bat` 提供菜单：

- 安装驱动。
- 干净卸载驱动。
- 运行 Python smoke test。
- 开启 Windows test mode。
- 关闭 Windows test mode。
- 查看驱动状态。

也支持命令行模式：

```bat
manage-driver.bat install
manage-driver.bat uninstall
manage-driver.bat test
manage-driver.bat testmode-on
manage-driver.bat testmode-off
manage-driver.bat status
```

## 验证结果

安装验证：

```text
devcon status ROOT\InputBridgeDevice
Driver is running
1 matching device(s) found.
```

调用验证：

```text
python smoke_test.py
smoke=ok
```

卸载验证：

- `devcon status ROOT\InputBridgeDevice` 返回 `No matching devices found.`
- `pnputil /enum-drivers` 中不再存在 `inputbridge.inf` / `MooseIre` / `InputBridge`。
- `Cert:\LocalMachine\Root` 和 `Cert:\LocalMachine\TrustedPublisher` 中不再存在 `CN=InputBridge Test Certificate`。

## 清理

- 删除了 `VirtualInput/x64/` 编译中间目录。
- 删除了 Python `__pycache__/`。
- 删除了安装测试日志和临时清理脚本。
- 删除了嵌套仓库 `VirtualInput/.git`，使根仓库能正常提交源码。
- 根 `.gitignore` 添加了驱动构建输出和 Python cache 规则。

## 注意

发布包内保留 `devcon.exe`，所以后续即使卸载 WDK，也可以继续通过 zip 内脚本安装和卸载驱动。

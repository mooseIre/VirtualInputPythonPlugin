# 2026-06-28 安装成功与 Python 调用修复

## 本轮目标

- 用户关闭 Secure Boot 并成功执行测试签名配置后，继续安装和调用测试。
- 修复 Python 端可以枚举设备但发送 HID 输出报告失败的问题。

## 当前安装状态

- `devcon status ROOT\InputBridgeDevice` 显示 3 个 `Input Bridge Device`，状态均为 `Driver is running`。
- `Win32_PnPEntity` 显示 `ConfigManagerErrorCode = 0`。
- Code 52 / `CM_PROB_UNSIGNED_DRIVER` 已消失。

## Python 调用问题

测试输出曾显示：

```text
devices=[...]
call_test=failed
发送 HID 输出报告失败; Windows error=1
```

原因是枚举出的 HID output collection 的 `usage` 都是 `0`，原 Python 封装按 `usage == keyboard/mouse` 选择句柄会选错 collection。键盘报告被发到了 4 字节相对鼠标 collection，导致 `HidD_SetOutputReport` 失败。

## 代码修复

- 修改 `python/virtual_input.py`：
  - 按 `OutputReportByteLength` 选择 HID collection。
  - `4` 字节：相对鼠标。
  - `9` 字节：键盘。
  - `6` 字节：绝对鼠标。
  - 如果缺少任一 report collection，抛出明确错误。
- 修改安装脚本：
  - `package/x64/install-and-test.ps1`
  - `package/x64/install-driver.ps1`
  - 安装前先执行 `devcon status ROOT\InputBridgeDevice`。
  - 已存在设备时不再重复 `devcon install`，避免继续生成重复根枚举实例。

## 验证

执行：

```powershell
python .\package\x64\test-inputbridge.py
```

结果：

```text
call_test=ok
```

额外 smoke test：

- `key_up()`
- `mouse_move(1, 0)`
- `mouse_move(-1, 0)`
- `mouse_up()`
- `mouse_move_abs(16384, 16384)`

结果：

```text
smoke=ok
```

## 遗留事项

- 由于之前多次运行 `devcon install`，系统当前存在 3 个 `Input Bridge Device` 实例，每个实例包含 3 个 HID collection，因此 `list_devices()` 返回 9 项。
- 尝试用 `pnputil /remove-device ROOT\HIDCLASS\0001`、`ROOT\HIDCLASS\0002` 和 `devcon remove` 清理重复实例未成功。
- 当前 Python 封装只打开每类 report 的第一个 collection，因此调用测试可正常通过；重复实例暂不阻塞功能。

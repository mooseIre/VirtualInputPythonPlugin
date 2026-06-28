# 2026-06-28 Root 枚举安装与 Code 52 诊断

## 本轮目标

- 修复 `pnputil /add-driver /install` 后 `devices=[]`、`未找到 InputBridge HID 设备` 的问题。
- 尝试完成安装并运行 Python 调用测试。

## 变更

- 将 INF 硬件 ID 从 `HID\InputBridgeDevice` 改为 `ROOT\InputBridgeDevice`。
- 更新 `package/x64/install-and-test.ps1`，改用 WDK `devcon install package\x64\InputBridge.inf ROOT\InputBridgeDevice` 创建设备节点。
- 更新 `package/x64/install-driver.ps1` 与 `ReadMe.md` 的安装命令。
- 重新运行 `Inf2Cat` 生成 `package/x64/inputbridge.cat`。
- 使用 `InputBridge Test Certificate` 对 catalog 重新签名。
- 新增 `package/x64/enable-testsigning.ps1`，用于管理员模式开启 Windows 测试签名。

## 验证结果

- `devcon install` 已成功创建设备节点：
  - 设备名：`Input Bridge Device`
  - 实例：`ROOT\HIDCLASS\0000`
- Python 测试仍失败：
  - `devices=[]`
  - `call_test=failed`
  - `未找到 InputBridge HID 设备`
- `devcon status ROOT\InputBridgeDevice` 显示：
  - `The device has the following problem: 52`
- SetupAPI 日志明确显示：
  - `CM_PROB_UNSIGNED_DRIVER`
  - `problem status: 0xc0000428`

## 当前阻塞

驱动包已入库、设备节点已创建，但 Windows 拒绝加载测试签名的内核驱动。尝试执行：

```powershell
bcdedit /set testsigning on
```

失败，错误为：

```text
该值受安全引导策略保护，无法进行修改或删除。
```

这说明当前机器开启了 Secure Boot。Secure Boot 开启时，本地测试证书签名的内核驱动不能通过测试签名模式加载。

## 下一步

1. 在 BIOS/UEFI 中关闭 Secure Boot。
2. 进入 Windows 后，以管理员 PowerShell 运行：

```powershell
bcdedit /set testsigning on
```

3. 重启 Windows。
4. 重新运行：

```powershell
Set-Location "C:\Users\moose\Desktop\RF4-Image-Assistant\VirtualInput"
powershell -ExecutionPolicy Bypass -File .\package\x64\install-and-test.ps1
```

预期测试签名生效后，设备不再是 Code 52，`test-inputbridge.py` 才能发现 HID 设备并发送调用测试。

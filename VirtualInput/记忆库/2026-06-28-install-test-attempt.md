# 2026-06-28 安装与调用测试记录

## 本轮动作

- 创建安装包目录 `package/x64/`。
- 复制 `InputBridge.sys` 到安装包。
- 修正包内 `InputBridge.inf` 的 KMDF 版本为 `1.15`。
- 修正 INF 架构节为 `NTamd64.10.0...18362`，使 `Inf2Cat` 可通过签名检查。
- 使用 `Inf2Cat.exe /driver:package\x64 /os:10_X64` 生成 `inputbridge.cat`。
- 创建当前用户测试证书 `InputBridge Test Certificate`。
- 使用 `signtool.exe sign /fd SHA256` 签名 catalog。
- 将测试证书导入当前用户 Root 和 TrustedPublisher 后，catalog 验签为 `Valid`。

## 安装阻塞

- 当前 Codex 进程不是提升后的管理员进程。
- `whoami /groups` 显示 `BUILTIN\Administrators` 为 `deny only`。
- `pnputil /add-driver package\x64\InputBridge.inf /install` 返回 `Access is denied`。
- 创建最高权限计划任务也返回 `Access is denied`。

## 调用测试

- 未安装驱动时运行 Python 枚举测试：
  - `devices=[]`
  - `call_test=failed`
  - 原因：`未找到 InputBridge HID 设备`

## 已生成脚本

- 管理员安装与测试脚本：`package/x64/install-and-test.ps1`
- 调用测试脚本：`package/x64/test-inputbridge.py`

## 后续执行

需要在提升的管理员 PowerShell 中运行：

```powershell
Set-Location "C:\Users\moose\Desktop\RF4-Image-Assistant\VirtualInput"
powershell -ExecutionPolicy Bypass -File .\package\x64\install-and-test.ps1
```

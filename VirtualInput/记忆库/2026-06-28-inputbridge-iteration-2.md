# 2026-06-28 InputBridge 迭代 2 记忆

## 用户要求

- 示例添加组合键。
- 解释 `virtual_input.py` 如何控制移动速度。
- 添加移动时间参数。
- 在 Python 封装层模拟人工抖动、随机移动曲线。
- 驱动名称不要出现旧项目和业务前缀字样。
- 安装最小可用编译环境并完成编译。

## 已设计实现

- Python 层新增 `InputBridge` 类，并移除旧别名。
- 移动速度由 Python 层控制：把总相对位移拆成多个 HID relative mouse report，并按 `duration_ms / steps` 间隔发送。
- `human_mouse_move()` 使用 smoothstep 曲线和随机 jitter 生成非线性路径，最后补偿残差，确保总位移落点正确。
- 示例文件已包含 `Ctrl+S`、`Ctrl+Shift+A`、长按、定时移动、人工曲线移动。

## 驱动命名

- 输出二进制: `InputBridge.sys`
- INF Hardware ID: `HID\InputBridgeDevice`
- Device description: `Input Bridge Device`
- Service display name: `Input Bridge`

## 编译环境状态

- 已通过 `winget` 安装 Visual Studio Build Tools 2022。
- 已通过 `winget` 安装 Windows Driver Kit 10.0.26100。
- 已通过 `winget` 安装 Windows SDK 10.0.18362，用于补齐 VS SDK 检查。
- VS Build Tools 当前未能以非提升进程注册 `WindowsKernelModeDriver10.0` 平台工具集，因此本轮使用项目本地 `.build/VCTargets` 临时覆盖目录完成构建。
- WPP `.tmh` 文件用 `tracewpp.exe -km -I"...\WppConfig\Rev1" -scan:Trace.h ...` 生成；这些文件是构建产物，已加入 `.gitignore`。
- Release x64 已编译成功，输出 `x64/Release/InputBridge.sys`。

## 本轮源码修复

- `Driver.h` 删除不存在的 `queue.h` 引用，实际项目使用 `QueueDefault.h` 和 `QueueManual.h`。
- 添加 `.gitignore` 忽略 `x64/`、`.build/`、`*.tmh` 等构建产物。

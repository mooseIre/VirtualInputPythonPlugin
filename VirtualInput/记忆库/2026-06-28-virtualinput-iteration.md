# 2026-06-28 VirtualInput 迭代记忆

## 目标

- 在根目录同步 `https://github.com/mooseIre/VirtualInput.git` 到 `VirtualInput/`。
- 改写驱动特征码，不保留项目原始空白硬件特征。
- 设计并实现外部程序调用模式，目标调用方是 Python 程序。
- 支持键盘按键、长按、鼠标点击、鼠标相对移动、鼠标绝对移动。

## 当前设计

- 外部调用方式：Python 通过 Windows HID API 发送 Output Report 给驱动。
- 驱动侧仍使用 HID 标准通道，不新增私有 IOCTL，减少内核态改动风险。
- Python 封装文件：`python/virtual_input.py`。
- 示例文件：`python/example.py`。

## 关键协议

- Vendor ID: `0x5146`
- Product ID: `0x2026`
- Version: `0x0101`
- 鼠标相对移动 Output Report ID: `0x02`
- 键盘 Output Report ID: `0x04`
- 鼠标绝对移动 Output Report ID: `0x06`

## 已修改的驱动身份

- INF 安装硬件 ID: `HID\RF4VirtualInput`
- 设备描述: `RF4 Virtual Input Device`
- 服务显示名: `RF4 Virtual Input`
- 设备接口 GUID: `a7285398-bede-4435-b4fa-0ad43c1ddc21`
- Trace GUID: `07dd4295-82b1-47ed-9946-1a10b2729038`

## 后续注意

- 驱动构建需要 Windows WDK 与 Visual Studio Driver 工具链。
- 安装命令应使用 `devcon install VirtualInput.inf HID\RF4VirtualInput`。
- Python 端当前使用 `ctypes` 调用 `hid.dll/setupapi.dll/kernel32.dll`，不依赖第三方包。
- 若后续需要更强的进程隔离或权限控制，可以再追加一个用户态本地 RPC 服务，但本轮没有新增网络调用。

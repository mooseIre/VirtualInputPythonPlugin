## InputBridge

A Windows HID driver that includes a mouse, keyboard, and an additional mouse with absolute coordinates. It is based on [loki-hidriver](https://github.com/hedgar2017/loki-hidriver).

## Current identity

This fork rewrites the default hardware identity instead of keeping the original empty identifiers.

- Hardware ID: `ROOT\InputBridgeDevice`
- Vendor ID: `0x5146`
- Product ID: `0x2026`
- Version: `0x0101`
- Driver binary: `InputBridge.sys`
- Device description: `Input Bridge Device`

## Installation

1. Run `bcdedit /set testsigning on` to enable test mode, then reboot your system.
2. Build the project in Debug or Release mode with Visual Studio Build Tools and the Windows Driver Kit.
3. Open the output folder and run:

```powershell
devcon install InputBridge.inf ROOT\InputBridgeDevice
```

## External call mode

External programs call the driver by sending HID Output Reports. The driver receives those reports through `IOCTL_HID_WRITE_REPORT` or `IOCTL_HID_SET_OUTPUT_REPORT`, then forwards the matching HID Input Report to Windows.

A Python ctypes client is provided in `python/virtual_input.py`. It discovers the HID device by Vendor ID and Product ID, opens the HID device path, and sends output reports with `HidD_SetOutputReport`.

Supported operations:

- `key_press(key_code, modifiers=0, hold_ms=40)`
- `key_hold(key_code, hold_ms, modifiers=0)`
- `key_combo(key_codes, modifiers=0, hold_ms=40)`
- `key_down(key_code, modifiers=0)`
- `key_up()`
- `mouse_click(button=BUTTON_LEFT, hold_ms=40)`
- `mouse_down(button=BUTTON_LEFT)`
- `mouse_up()`
- `mouse_move(dx, dy, buttons=0, duration_ms=0, steps=None)`
- `human_mouse_move(dx, dy, duration_ms=300, steps=None, buttons=0, jitter=1.5)`
- `mouse_move_abs(x, y, buttons=0)` for absolute movement in `0..32767`

## Movement speed

The driver itself does not store movement speed. The Python wrapper controls speed by splitting the requested relative movement into small HID reports and sleeping between reports. For example, `mouse_move(300, 120, duration_ms=500)` sends several smaller relative moves over about 500 ms.

`human_mouse_move()` uses a smoothstep timing curve plus bounded random jitter before each step, so the cursor path is less linear. The final correction step still lands on the requested total delta.

Example:

```python
from virtual_input import BUTTON_LEFT, MOD_LEFT_CTRL, MOD_LEFT_SHIFT, InputBridge

with InputBridge() as bridge:
    bridge.key_press(0x04)  # A
    bridge.key_combo([0x16], modifiers=MOD_LEFT_CTRL)  # Ctrl+S
    bridge.key_combo([0x04], modifiers=MOD_LEFT_CTRL | MOD_LEFT_SHIFT)  # Ctrl+Shift+A
    bridge.key_hold(0x1A, hold_ms=600)  # W
    bridge.mouse_move(300, 120, duration_ms=500)
    bridge.human_mouse_move(300, -80, duration_ms=700, jitter=2.0)
    bridge.mouse_click(BUTTON_LEFT)
```

## Development memory

Each iteration should write a markdown record under `记忆库/`.

## Development

To view the logs sent by `TraceEvents()`, use `traceview.exe` with the tracing GUID `07dd4295-82b1-47ed-9946-1a10b2729038` (defined in `Trace.h`).
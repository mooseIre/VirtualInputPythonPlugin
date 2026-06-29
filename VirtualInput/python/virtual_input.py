"""Python client for the InputBridge HID driver.

The driver receives HID output reports and converts them to input reports.
This module uses the Windows HID APIs directly through ctypes so callers do
not need third-party packages.
"""

from __future__ import annotations

import ctypes
import math
import random
import time
from ctypes import wintypes
from dataclasses import dataclass
from typing import Iterable


VENDOR_ID = 0x5146
PRODUCT_ID = 0x2026
USAGE_PAGE_GENERIC_DESKTOP = 0x01
USAGE_MOUSE = 0x02
USAGE_KEYBOARD = 0x06

REPORT_ID_MOUSE_OUTPUT = 0x02
REPORT_ID_KEYBOARD_OUTPUT = 0x04
REPORT_ID_MOUSE_ABS_OUTPUT = 0x06

BUTTON_LEFT = 0x01
BUTTON_RIGHT = 0x02
BUTTON_MIDDLE = 0x04
BUTTON_X1 = 0x08
BUTTON_X2 = 0x10

MOD_LEFT_CTRL = 0x01
MOD_LEFT_SHIFT = 0x02
MOD_LEFT_ALT = 0x04
MOD_LEFT_GUI = 0x08
MOD_RIGHT_CTRL = 0x10
MOD_RIGHT_SHIFT = 0x20
MOD_RIGHT_ALT = 0x40
MOD_RIGHT_GUI = 0x80


GENERIC_WRITE = 0x40000000
GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
HIDP_STATUS_SUCCESS = 0x00110000


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("InterfaceClassGuid", GUID),
        ("Flags", wintypes.DWORD),
        ("Reserved", ctypes.c_size_t),
    ]


class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("ClassGuid", GUID),
        ("DevInst", wintypes.DWORD),
        ("Reserved", ctypes.c_size_t),
    ]


class HIDD_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Size", wintypes.ULONG),
        ("VendorID", wintypes.USHORT),
        ("ProductID", wintypes.USHORT),
        ("VersionNumber", wintypes.USHORT),
    ]


class HIDP_CAPS(ctypes.Structure):
    _fields_ = [
        ("Usage", wintypes.USHORT),
        ("UsagePage", wintypes.USHORT),
        ("InputReportByteLength", wintypes.USHORT),
        ("OutputReportByteLength", wintypes.USHORT),
        ("FeatureReportByteLength", wintypes.USHORT),
        ("Reserved", wintypes.USHORT * 17),
        ("NumberLinkCollectionNodes", wintypes.USHORT),
        ("NumberInputButtonCaps", wintypes.USHORT),
        ("NumberInputValueCaps", wintypes.USHORT),
        ("NumberInputDataIndices", wintypes.USHORT),
        ("NumberOutputButtonCaps", wintypes.USHORT),
        ("NumberOutputValueCaps", wintypes.USHORT),
        ("NumberOutputDataIndices", wintypes.USHORT),
        ("NumberFeatureButtonCaps", wintypes.USHORT),
        ("NumberFeatureValueCaps", wintypes.USHORT),
        ("NumberFeatureDataIndices", wintypes.USHORT),
    ]


setupapi = ctypes.WinDLL("setupapi", use_last_error=True)
hid = ctypes.WinDLL("hid", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

setupapi.SetupDiGetClassDevsW.argtypes = [
    ctypes.POINTER(GUID),
    wintypes.LPCWSTR,
    wintypes.HWND,
    wintypes.DWORD,
]
setupapi.SetupDiGetClassDevsW.restype = wintypes.HANDLE
setupapi.SetupDiEnumDeviceInterfaces.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(SP_DEVINFO_DATA),
    ctypes.POINTER(GUID),
    wintypes.DWORD,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
]
setupapi.SetupDiEnumDeviceInterfaces.restype = wintypes.BOOL
setupapi.SetupDiGetDeviceInterfaceDetailW.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(SP_DEVICE_INTERFACE_DATA),
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(SP_DEVINFO_DATA),
]
setupapi.SetupDiGetDeviceInterfaceDetailW.restype = wintypes.BOOL
setupapi.SetupDiDestroyDeviceInfoList.argtypes = [wintypes.HANDLE]
setupapi.SetupDiDestroyDeviceInfoList.restype = wintypes.BOOL

hid.HidD_GetHidGuid.argtypes = [ctypes.POINTER(GUID)]
hid.HidD_GetAttributes.argtypes = [wintypes.HANDLE, ctypes.POINTER(HIDD_ATTRIBUTES)]
hid.HidD_GetAttributes.restype = wintypes.BOOLEAN
hid.HidD_GetPreparsedData.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.HANDLE)]
hid.HidD_GetPreparsedData.restype = wintypes.BOOLEAN
hid.HidD_FreePreparsedData.argtypes = [wintypes.HANDLE]
hid.HidD_FreePreparsedData.restype = wintypes.BOOLEAN
hid.HidP_GetCaps.argtypes = [wintypes.HANDLE, ctypes.POINTER(HIDP_CAPS)]
hid.HidP_GetCaps.restype = wintypes.LONG
hid.HidD_SetOutputReport.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.ULONG]
hid.HidD_SetOutputReport.restype = wintypes.BOOLEAN

kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE,
]
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL


@dataclass(frozen=True)
class HidDeviceInfo:
    path: str
    usage_page: int
    usage: int
    output_report_length: int


class InputBridgeError(RuntimeError):
    pass


def _raise_last_error(message: str) -> None:
    error = ctypes.get_last_error()
    raise InputBridgeError(f"{message}; Windows error={error}")


def _open_handle(path: str) -> wintypes.HANDLE:
    handle = kernel32.CreateFileW(
        path,
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None,
    )
    if handle == INVALID_HANDLE_VALUE:
        _raise_last_error(f"无法打开 HID 设备: {path}")
    return handle


def _get_caps(handle: wintypes.HANDLE) -> HIDP_CAPS:
    preparsed = wintypes.HANDLE()
    if not hid.HidD_GetPreparsedData(handle, ctypes.byref(preparsed)):
        _raise_last_error("无法读取 HID preparsed data")

    try:
        caps = HIDP_CAPS()
        status = hid.HidP_GetCaps(preparsed, ctypes.byref(caps))
        if status != HIDP_STATUS_SUCCESS:
            raise InputBridgeError(f"无法读取 HID caps; HidP status={status}")
        return caps
    finally:
        hid.HidD_FreePreparsedData(preparsed)


def _device_paths() -> Iterable[str]:
    guid = GUID()
    hid.HidD_GetHidGuid(ctypes.byref(guid))

    digcf_present = 0x00000002
    digcf_deviceinterface = 0x00000010
    info_set = setupapi.SetupDiGetClassDevsW(
        ctypes.byref(guid),
        None,
        None,
        digcf_present | digcf_deviceinterface,
    )
    if info_set == INVALID_HANDLE_VALUE:
        _raise_last_error("无法枚举 HID 设备")

    try:
        index = 0
        while True:
            iface = SP_DEVICE_INTERFACE_DATA()
            iface.cbSize = ctypes.sizeof(SP_DEVICE_INTERFACE_DATA)
            ok = setupapi.SetupDiEnumDeviceInterfaces(
                info_set,
                None,
                ctypes.byref(guid),
                index,
                ctypes.byref(iface),
            )
            if not ok:
                break

            required = wintypes.DWORD()
            setupapi.SetupDiGetDeviceInterfaceDetailW(
                info_set,
                ctypes.byref(iface),
                None,
                0,
                ctypes.byref(required),
                None,
            )

            detail = ctypes.create_string_buffer(required.value)
            ctypes.cast(detail, ctypes.POINTER(wintypes.DWORD))[0] = (
                8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
            )

            if setupapi.SetupDiGetDeviceInterfaceDetailW(
                info_set,
                ctypes.byref(iface),
                detail,
                required,
                None,
                None,
            ):
                offset = ctypes.sizeof(wintypes.DWORD)
                yield ctypes.wstring_at(ctypes.addressof(detail) + offset)
            index += 1
    finally:
        setupapi.SetupDiDestroyDeviceInfoList(info_set)


def list_devices(
    vendor_id: int = VENDOR_ID,
    product_id: int = PRODUCT_ID,
) -> list[HidDeviceInfo]:
    devices: list[HidDeviceInfo] = []
    for path in _device_paths():
        try:
            handle = _open_handle(path)
        except InputBridgeError:
            continue
        try:
            attrs = HIDD_ATTRIBUTES()
            attrs.Size = ctypes.sizeof(HIDD_ATTRIBUTES)
            if not hid.HidD_GetAttributes(handle, ctypes.byref(attrs)):
                continue
            if attrs.VendorID != vendor_id or attrs.ProductID != product_id:
                continue

            caps = _get_caps(handle)
            devices.append(
                HidDeviceInfo(
                    path=path,
                    usage_page=caps.UsagePage,
                    usage=caps.Usage,
                    output_report_length=caps.OutputReportByteLength,
                )
            )
        finally:
            kernel32.CloseHandle(handle)
    return devices


class InputBridge:
    def __init__(self) -> None:
        devices = list_devices()
        if not devices:
            raise InputBridgeError("未找到 InputBridge HID 设备")

        keyboard = self._find_by_report_length(devices, 9)
        mouse_rel = self._find_by_report_length(devices, 5)
        mouse_abs = self._find_by_report_length(devices, 6)

        if keyboard is None or mouse_rel is None or mouse_abs is None:
            lengths = sorted({device.output_report_length for device in devices})
            raise InputBridgeError(f"InputBridge HID reports 不完整; output lengths={lengths}")

        self._keyboard = _open_handle(keyboard.path)
        self._mouse_rel = _open_handle(mouse_rel.path)
        self._mouse_abs = _open_handle(mouse_abs.path)

    @staticmethod
    def _find_by_report_length(
        devices: list[HidDeviceInfo],
        output_report_length: int,
    ) -> HidDeviceInfo | None:
        return next(
            (
                device
                for device in devices
                if device.output_report_length == output_report_length
            ),
            None,
        )

    def close(self) -> None:
        if self._keyboard:
            kernel32.CloseHandle(self._keyboard)
            self._keyboard = None
        same_mouse_handle = self._mouse_abs and self._mouse_abs == self._mouse_rel
        if self._mouse_rel:
            kernel32.CloseHandle(self._mouse_rel)
            self._mouse_rel = None
        if self._mouse_abs and not same_mouse_handle:
            kernel32.CloseHandle(self._mouse_abs)
        self._mouse_abs = None

    def __enter__(self) -> "InputBridge":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def _send(self, handle: wintypes.HANDLE, payload: bytes) -> None:
        buffer = ctypes.create_string_buffer(payload)
        if not hid.HidD_SetOutputReport(handle, buffer, len(payload)):
            _raise_last_error("发送 HID 输出报告失败")

    def keyboard_set(self, key_codes: Iterable[int], modifiers: int = 0) -> None:
        keys = list(key_codes)[:6]
        keys.extend([0] * (6 - len(keys)))
        self._send(
            self._keyboard,
            bytes([REPORT_ID_KEYBOARD_OUTPUT, modifiers, 0, *keys]),
        )

    def key_down(self, key_code: int, modifiers: int = 0) -> None:
        self.keyboard_set([key_code], modifiers)

    def key_up(self) -> None:
        self._send(self._keyboard, bytes([REPORT_ID_KEYBOARD_OUTPUT, 0, 0, 0, 0, 0, 0, 0, 0]))

    def key_press(self, key_code: int, modifiers: int = 0, hold_ms: int = 40) -> None:
        self.key_down(key_code, modifiers)
        time.sleep(hold_ms / 1000)
        self.key_up()

    def key_hold(self, key_code: int, hold_ms: int, modifiers: int = 0) -> None:
        self.key_press(key_code, modifiers, hold_ms)

    def key_combo(
        self,
        key_codes: Iterable[int],
        modifiers: int = 0,
        hold_ms: int = 40,
    ) -> None:
        self.keyboard_set(key_codes, modifiers)
        time.sleep(hold_ms / 1000)
        self.key_up()

    def _send_relative_report(
        self,
        dx: int,
        dy: int,
        buttons: int = 0,
        wheel: int = 0,
    ) -> None:
        dx = max(-127, min(127, dx))
        dy = max(-127, min(127, dy))
        wheel = max(-127, min(127, wheel))
        self._send(
            self._mouse_rel,
            bytes([REPORT_ID_MOUSE_OUTPUT, buttons, dx & 0xFF, dy & 0xFF, wheel & 0xFF]),
        )

    def _send_relative_move(self, dx: int, dy: int, buttons: int = 0) -> None:
        self._send_relative_report(dx, dy, buttons)

    def mouse_move(
        self,
        dx: int,
        dy: int,
        buttons: int = 0,
        duration_ms: int = 0,
        steps: int | None = None,
    ) -> None:
        if duration_ms <= 0 and steps is None:
            self._send_relative_move(dx, dy, buttons)
            return

        self._move_curve(
            dx=dx,
            dy=dy,
            duration_ms=max(0, duration_ms),
            steps=steps,
            buttons=buttons,
            jitter=0.0,
            humanize=False,
        )

    def human_mouse_move(
        self,
        dx: int,
        dy: int,
        duration_ms: int = 300,
        steps: int | None = None,
        buttons: int = 0,
        jitter: float = 1.5,
    ) -> None:
        self._move_curve(
            dx=dx,
            dy=dy,
            duration_ms=max(1, duration_ms),
            steps=steps,
            buttons=buttons,
            jitter=max(0.0, jitter),
            humanize=True,
        )

    def _move_curve(
        self,
        dx: int,
        dy: int,
        duration_ms: int,
        steps: int | None,
        buttons: int,
        jitter: float,
        humanize: bool,
    ) -> None:
        distance = max(abs(dx), abs(dy))
        if steps is None:
            if humanize:
                steps = max(6, min(180, math.ceil(distance / random.uniform(8.0, 14.0))))
            else:
                steps = max(1, min(120, math.ceil(distance / 30)))
        interval = duration_ms / 1000 / steps if duration_ms > 0 else 0
        vector_length = math.hypot(dx, dy)
        if humanize and vector_length > 0:
            perp_x = -dy / vector_length
            perp_y = dx / vector_length
            curve = random.uniform(-0.18, 0.18) * min(vector_length, 220)
            wave_phase = random.uniform(0, math.tau)
        else:
            perp_x = 0.0
            perp_y = 0.0
            curve = 0.0
            wave_phase = 0.0

        sent_x = 0
        sent_y = 0
        for index in range(1, steps + 1):
            t = index / steps
            if humanize:
                eased_t = 3 * t * t - 2 * t * t * t
                arc = math.sin(math.pi * t) * curve
                arc += math.sin(math.tau * t + wave_phase) * curve * 0.18
                target_x = dx * eased_t + perp_x * arc
                target_y = dy * eased_t + perp_y * arc
            else:
                target_x = dx * t
                target_y = dy * t
            if humanize and index < steps:
                settle = max(0.15, 1.0 - t * 0.85)
                target_x += random.uniform(-jitter, jitter) * settle
                target_y += random.uniform(-jitter, jitter) * settle

            step_x = round(target_x - sent_x)
            step_y = round(target_y - sent_y)
            sent_x += step_x
            sent_y += step_y

            while step_x or step_y:
                chunk_x = max(-127, min(127, step_x))
                chunk_y = max(-127, min(127, step_y))
                self._send_relative_move(chunk_x, chunk_y, buttons)
                step_x -= chunk_x
                step_y -= chunk_y

            if interval > 0 and index < steps:
                sleep_for = interval
                if humanize:
                    sleep_for *= random.uniform(0.65, 1.45)
                    if index < steps - 1 and random.random() < 0.05:
                        sleep_for += min(0.035, interval * random.uniform(0.8, 2.4))
                time.sleep(sleep_for)

        remain_x = dx - sent_x
        remain_y = dy - sent_y
        if remain_x or remain_y:
            self._send_relative_move(remain_x, remain_y, buttons)

    def mouse_move_abs(self, x: int, y: int, buttons: int = 0) -> None:
        x = max(0, min(32767, x))
        y = max(0, min(32767, y))
        self._send(
            self._mouse_abs,
            bytes(
                [
                    REPORT_ID_MOUSE_ABS_OUTPUT,
                    buttons,
                    x & 0xFF,
                    (x >> 8) & 0xFF,
                    y & 0xFF,
                    (y >> 8) & 0xFF,
                ]
            ),
        )

    def mouse_down(self, button: int = BUTTON_LEFT) -> None:
        self.mouse_move(0, 0, button)

    def mouse_up(self) -> None:
        self.mouse_move(0, 0, 0)

    def mouse_click(self, button: int = BUTTON_LEFT, hold_ms: int = 40) -> None:
        self.mouse_down(button)
        time.sleep(hold_ms / 1000)
        self.mouse_up()

    def mouse_wheel(self, delta: int, buttons: int = 0) -> None:
        delta = int(delta)
        while delta:
            chunk = max(-127, min(127, delta))
            self._send_relative_report(0, 0, buttons, chunk)
            delta -= chunk

    def wheel_up(self, clicks: int = 1, buttons: int = 0) -> None:
        self.mouse_wheel(abs(int(clicks)), buttons)

    def wheel_down(self, clicks: int = 1, buttons: int = 0) -> None:
        self.mouse_wheel(-abs(int(clicks)), buttons)


if __name__ == "__main__":
    with InputBridge() as bridge:
        bridge.key_press(0x04)
        bridge.mouse_move(20, 0)
        bridge.mouse_click()

import time

from virtual_input import (
    BUTTON_LEFT,
    BUTTON_RIGHT,
    BUTTON_X1,
    BUTTON_X2,
    MOD_LEFT_CTRL,
    MOD_LEFT_SHIFT,
    InputBridge,
)


with InputBridge() as bridge:
    bridge.key_up()
    bridge.mouse_up()
    bridge.mouse_move(1, 0)
    bridge.mouse_move(-1, 0)

    # Examples for external callers:
    # bridge.key_press(0x04)  # HID key code 0x04 = A
    # bridge.key_combo([0x16], modifiers=MOD_LEFT_CTRL)  # Ctrl+S
    # bridge.key_combo([0x04], modifiers=MOD_LEFT_CTRL | MOD_LEFT_SHIFT)  # Ctrl+Shift+A
    # bridge.key_hold(0x1A, hold_ms=600)  # W
    # bridge.mouse_move(300, 120, duration_ms=500)
    # bridge.human_mouse_move(300, -80, duration_ms=700, jitter=2.0)
    # bridge.human_mouse_move(-180, 90, duration_ms=850, jitter=1.2)
    # bridge.mouse_click(BUTTON_LEFT)
    # bridge.mouse_click(BUTTON_X1)
    # bridge.mouse_click(BUTTON_X2)
    # bridge.wheel_up(3)
    # bridge.wheel_down(3)
    # bridge.mouse_down(BUTTON_LEFT)
    # time.sleep(0.8)
    # bridge.mouse_up()
    # bridge.mouse_down(BUTTON_RIGHT)
    # time.sleep(0.8)
    # bridge.mouse_up()
    # bridge.mouse_move_abs(16384, 16384)

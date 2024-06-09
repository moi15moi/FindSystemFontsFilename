from ctypes import windll, wintypes
from ..exceptions import SystemApiError

__all__ = ["User32"]


class User32():
    def __init__(self) -> None:
        user32 = windll.user32

        self.HWND_BROADCAST = wintypes.HWND(0xFFFF)
        self.WM_FONTCHANGE = wintypes.UINT(0x001D)

        # https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendnotifymessagew
        self.SendNotifyMessageW = user32.SendNotifyMessageW
        self.SendNotifyMessageW.restype = wintypes.BOOL
        self.SendNotifyMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        self.SendNotifyMessageW.errcheck = self.errcheck_is_result_0_or_null

    @staticmethod
    def errcheck_is_result_0_or_null(result, func, args):
        if not result:
            raise SystemApiError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result

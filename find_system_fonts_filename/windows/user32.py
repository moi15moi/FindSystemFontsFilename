from ctypes import windll, wintypes

__all__ = ["User32"]


class User32():
    def __init__(self) -> None:
        user32 = windll.user32
        
        self.HWND_BROADCAST = wintypes.HWND(0xffff)
        self.WM_FONTCHANGE = wintypes.UINT(0x001D)

        self.SendMessageW = user32.SendMessageW
        self.SendMessageW.restype = wintypes.LONG
        self.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

        self.SendNotifyMessageW = user32.SendNotifyMessageW
        self.SendNotifyMessageW.restype = wintypes.BOOL
        self.SendNotifyMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        self.SendNotifyMessageW.errcheck = self.is_return_0

    @staticmethod
    def is_return_0(result, func, args):
        if result == 0:
            raise OSError(f"{func.__name__} fails. 0 font have been removed")
        return result

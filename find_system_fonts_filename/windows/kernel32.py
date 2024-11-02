from ctypes import windll, wintypes
from ..exceptions import SystemApiError

__all__ = ["Kernel32"]


class Kernel32():
    def __init__(self) -> None:
        kernel32 = windll.LoadLibrary("kernel32")

        self.LOCALE_NAME_MAX_LENGTH = 85

        # https://learn.microsoft.com/en-us/windows/win32/api/winnls/nf-winnls-getuserdefaultlocalename
        self.GetUserDefaultLocaleName = kernel32.GetUserDefaultLocaleName
        self.GetUserDefaultLocaleName.restype = wintypes.INT
        self.GetUserDefaultLocaleName.argtypes = [wintypes.LPWSTR, wintypes.INT]
        self.GetUserDefaultLocaleName.errcheck = self.errcheck_is_result_0_or_null

    @staticmethod
    def errcheck_is_result_0_or_null(result, func, args):
        if not result:
            raise SystemApiError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result

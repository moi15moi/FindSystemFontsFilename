from ctypes import c_size_t, windll, wintypes
from ..exceptions import SystemApiError

__all__ = ["MSVCRT"]


class MSVCRT:
    def __init__(self) -> None:
        msvcrt = windll.LoadLibrary("msvcrt")

        # https://learn.microsoft.com/fr-fr/cpp/c-runtime-library/reference/strncpy-s-strncpy-s-l-wcsncpy-s-wcsncpy-s-l-mbsncpy-s-mbsncpy-s-l?view=msvc-170
        self.wcsncpy_s = msvcrt.wcsncpy_s
        self.wcsncpy_s.restype = wintypes.INT
        self.wcsncpy_s.argtypes = [wintypes.LPWSTR, c_size_t, wintypes.LPCWSTR, c_size_t]
        self.wcsncpy_s.errcheck = self.errcheck_wcsncpy_s

        self.TRUNCATE = c_size_t(-1).value

    @staticmethod
    def errcheck_wcsncpy_s(result, func, args):
        STRUNCATE = 80
        if result not in (0, STRUNCATE):
            raise SystemApiError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result

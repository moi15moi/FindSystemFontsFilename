from ctypes import windll, wintypes

__all__ = ["GDI32"]


class GDI32:
    def __init__(self) -> None:
        gdi = windll.gdi32

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-addfontresourcew
        self.AddFontResourceW = gdi.AddFontResourceW
        self.AddFontResourceW.restype = wintypes.INT
        self.AddFontResourceW.argtypes = [wintypes.LPCWSTR]
        self.AddFontResourceW.errcheck = self.errcheck_is_result_0_or_null

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-removefontresourcew
        self.RemoveFontResourceW = gdi.RemoveFontResourceW
        self.RemoveFontResourceW.restype = wintypes.BOOL
        self.RemoveFontResourceW.argtypes = [wintypes.LPCWSTR]
        self.RemoveFontResourceW.errcheck = self.errcheck_is_result_0_or_null

    @staticmethod
    def errcheck_is_result_0_or_null(result, func, args):
        if not result:
            raise OSError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result

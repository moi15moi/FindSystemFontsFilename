from ctypes import Structure, c_ubyte, windll, wintypes

__all__ = [
    "LOGFONTW",
    "TEXTMETRIC",
    "GDI",
]

class LOGFONTW(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-logfontw
    _fields_ = [
        ("lfHeight", wintypes.LONG),
        ("lfWidth", wintypes.LONG),
        ("lfEscapement", wintypes.LONG),
        ("lfOrientation", wintypes.LONG),
        ("lfWeight", wintypes.LONG),
        ("lfItalic", c_ubyte), # Cannot use c_ubyteS on old version of python, see https://github.com/python/cpython/issues/60580
        ("lfUnderline", c_ubyte),
        ("lfStrikeOut", c_ubyte),
        ("lfCharSet", c_ubyte),
        ("lfOutPrecision", c_ubyte),
        ("lfClipPrecision", c_ubyte),
        ("lfQuality", c_ubyte),
        ("lfPitchAndFamily", c_ubyte),
        ("lfFaceName", wintypes.WCHAR * 32),
    ]


class TEXTMETRIC(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-textmetricw
    _fields_ = [
        ('tmHeight', wintypes.LONG),
        ('tmAscent', wintypes.LONG),
        ('tmDescent', wintypes.LONG),
        ('tmInternalLeading', wintypes.LONG),
        ('tmExternalLeading', wintypes.LONG),
        ('tmAveCharWidth', wintypes.LONG),
        ('tmMaxCharWidth', wintypes.LONG),
        ('tmWeight', wintypes.LONG),
        ('tmOverhang', wintypes.LONG),
        ('tmDigitizedAspectX', wintypes.LONG),
        ('tmDigitizedAspectY', wintypes.LONG),
        ('tmFirstChar', wintypes.WCHAR),
        ('tmLastChar', wintypes.WCHAR),
        ('tmDefaultChar', wintypes.WCHAR),
        ('tmBreakChar', wintypes.WCHAR),
        ('tmItalic', c_ubyte),
        ('tmUnderlined', c_ubyte),
        ('tmStruckOut', c_ubyte),
        ('tmPitchAndFamily', c_ubyte),
        ('tmCharSet', c_ubyte)
    ]


class GDI:
    def __init__(self) -> None:
        gdi = windll.gdi32

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createcompatibledc
        self.CreateCompatibleDC = gdi.CreateCompatibleDC
        self.CreateCompatibleDC.restype = wintypes.HDC
        self.CreateCompatibleDC.argtypes = [wintypes.HDC]
        self.CreateCompatibleDC.errcheck = self.errcheck_is_result_0_or_null

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-deletedc
        self.DeleteDC = gdi.DeleteDC
        self.DeleteDC.restype = wintypes.BOOL
        self.DeleteDC.argtypes = [wintypes.HDC]
        self.DeleteDC.errcheck = self.errcheck_is_result_0_or_null

    @staticmethod
    def errcheck_is_result_0_or_null(result, func, args):
        if not result:
            raise OSError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result

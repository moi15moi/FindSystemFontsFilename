from ctypes import c_ubyte, POINTER, Structure, windll, WINFUNCTYPE, wintypes

__all__ = [
    "LOGFONTW",
    "TEXTMETRICW",
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


class TEXTMETRICW(Structure):
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


class ENUMLOGFONTEXW(Structure):
    # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-enumlogfontexw
    _fields_ = [
        ("elfLogFont", LOGFONTW),
        ("elfFullName", wintypes.WCHAR * 64),
        ("elfStyle", wintypes.WCHAR * 32),
        ("elfScript", wintypes.WCHAR * 32),
    ]


class FontRealizationInfo(Structure):
    # https://gitlab.winehq.org/wine/wine/-/blob/b210a204137dec8d2126ca909d762454fd47e963/dlls/dwrite/gdiinterop.c#L740-749
    _fields_ = [
        ("size", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("cache_num", wintypes.DWORD),
        ("instance_id", wintypes.DWORD),
        ("file_count", wintypes.DWORD),
        ("face_index", wintypes.WORD),
        ("simulations", wintypes.WORD),
    ]


class FontFileInfo(Structure):
    # https://gitlab.winehq.org/wine/wine/-/blob/b210a204137dec8d2126ca909d762454fd47e963/dlls/dwrite/gdiinterop.c#L751-756
    _fields_ = [
        ("writetime", wintypes.FILETIME),
        ("size", wintypes.LARGE_INTEGER),
        ("path", wintypes.WCHAR), # The size can varies
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

        # https://learn.microsoft.com/en-us/previous-versions/dd162618(v=vs.85)
        self.ENUMFONTFAMEXPROC = WINFUNCTYPE(
            wintypes.INT,
            ENUMLOGFONTEXW,
            TEXTMETRICW,
            wintypes.DWORD,
            wintypes.LPARAM,
        )

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-enumfontsw
        self.EnumFontsW = gdi.EnumFontsW
        self.EnumFontsW.restype = wintypes.INT
        self.EnumFontsW.argtypes = [wintypes.HDC, wintypes.LPCWSTR, self.ENUMFONTFAMEXPROC, wintypes.LPARAM]

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-enumfontfamiliesw
        self.EnumFontFamiliesW = gdi.EnumFontFamiliesW
        self.EnumFontFamiliesW.restype = wintypes.INT
        self.EnumFontFamiliesW.argtypes = [wintypes.HDC, wintypes.LPCWSTR, self.ENUMFONTFAMEXPROC, wintypes.LPARAM]

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-enumfontfamiliesexw
        self.EnumFontFamiliesExW = gdi.EnumFontFamiliesExW
        self.EnumFontFamiliesExW.restype = wintypes.INT
        self.EnumFontFamiliesExW.argtypes = [wintypes.HDC, POINTER(LOGFONTW), self.ENUMFONTFAMEXPROC, wintypes.LPARAM, wintypes.DWORD]

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createfontindirectw
        self.CreateFontIndirectW = gdi.CreateFontIndirectW
        self.CreateFontIndirectW.restype = wintypes.HFONT
        self.CreateFontIndirectW.argtypes = [POINTER(LOGFONTW)]
        self.CreateFontIndirectW.errcheck = self.errcheck_is_result_0_or_null

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-selectobject
        self.SelectObject = gdi.SelectObject
        self.SelectObject.restype = wintypes.HGDIOBJ
        self.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
        self.SelectObject.errcheck = self.has_SelectObject_failed

        # https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-deleteobject
        self.DeleteObject = gdi.DeleteObject
        self.DeleteObject.restype = wintypes.BOOL
        self.DeleteObject.argtypes = [wintypes.HGDIOBJ]
        self.DeleteObject.errcheck = self.errcheck_is_result_0_or_null

        # Not documented by Microsoft
        # From https://gitlab.winehq.org/wine/wine/-/blob/b210a204137dec8d2126ca909d762454fd47e963/dlls/dwrite/gdiinterop.c#L759
        self.GetFontRealizationInfo = gdi.GetFontRealizationInfo
        self.GetFontRealizationInfo.restype = wintypes.BOOL
        self.GetFontRealizationInfo.argtypes = [wintypes.HDC, POINTER(FontRealizationInfo)]
        self.GetFontRealizationInfo.errcheck = self.errcheck_is_result_0_or_null

        # Not documented by Microsoft
        # From https://gitlab.winehq.org/wine/wine/-/blob/b210a204137dec8d2126ca909d762454fd47e963/dlls/dwrite/gdiinterop.c#L760
        self.GetFontFileInfo = gdi.GetFontFileInfo
        self.GetFontFileInfo.restype = wintypes.BOOL
        self.GetFontFileInfo.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, POINTER(wintypes.DWORD)]

        self.LF_FACESIZE = 32
        self.RASTER_FONTTYPE = 0x0001
        self.DEVICE_FONTTYPE = 0x0002
        self.TRUETYPE_FONTTYPE = 0x0004

    @staticmethod
    def errcheck_is_result_0_or_null(result, func, args):
        if not result:
            raise OSError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result

    @staticmethod
    def has_SelectObject_failed(result, func, args):
        HGDI_ERROR = wintypes.HGDIOBJ(0xFFFFFFFF)
        if result == None or result == HGDI_ERROR:
            raise OSError(f"{func.__name__} fails. The result is {result} which is invalid")
        return result